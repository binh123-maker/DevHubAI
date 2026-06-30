# 16. Architecture Review — DevHub AI

**Ngày review:** 23/06/2025  
**Cập nhật:** P0 fixes applied — xem [17-Revised-MVP-Architecture.md](./17-Revised-MVP-Architecture.md)  
**Phạm vi:** 15 tài liệu thiết kế gốc (docs/01–15)  
**Mục tiêu:** Đánh giá tính nhất quán, khả thi triển khai, và đề xuất MVP tối ưu cho sinh viên năm 3

> **Trạng thái:** Các khuyến nghị P0 đã được áp dụng. MVP-8W là mục tiêu triển khai chính thức.

---

## Tóm tắt điều hành

| Hạng mục | Đánh giá | Mức độ nghiêm trọng |
|----------|----------|---------------------|
| Database schema | Tốt về cấu trúc tổng thể, có 8 vấn đề cần sửa | Trung bình |
| API ↔ Database | 12 endpoint/thuộc tính chưa có bảng hoặc thiếu cột | Cao |
| Use Case ↔ SRS | Lệch hệ thống đánh số UC, thiếu 6 use case | Cao |
| UI ↔ Chức năng | 21 trang nhưng chỉ 9 wireframe, nhiều màn hình “ảo” | Trung bình |
| Khả thi SV năm 3 | Full scope ~20 tuần quá tải; cần cắt 60% | Cao |
| MVP hiện tại (doc 14) | Khả thi 8 tuần với team 4 người; cần tinh gọn thêm cho 6 tuần | Trung bình |

**Kết luận chung:** Bộ thiết kế **đủ chi tiết và có tầm nhìn tốt** cho sản phẩm hoàn chỉnh, nhưng **chưa đồng bộ nội bộ** ở ma trận truy vết (SRS ↔ UC ↔ API ↔ DB ↔ UI). Triển khai full theo 15 tài liệu trong 1 học kỳ là **không realistic** cho nhóm sinh viên năm 3. Cần áp dụng **MVP Phase 0** (6 tuần) hoặc **MVP Phase 1** (8 tuần) như đề xuất cuối tài liệu.

---

## 1. Review Database Schema

### 1.1 Bảng hiện có (18 bảng)

| Bảng | Trong SRS yêu cầu | Ghi chú |
|------|-------------------|---------|
| users | ✓ | |
| user_profiles | ✓ | |
| workspaces | ✓ | |
| folders | ✓ | |
| documents | ✓ | |
| document_chunks | ✓ | |
| websites | ✓ | |
| website_contents | ✓ | |
| notes | ✓ | |
| bookmarks | ✓ | |
| chats | ✓ | |
| chat_messages | ✓ | |
| citations | ✓ | |
| flashcards | ✓ | |
| quizzes | ✓ | |
| tags | ✓ | |
| document_tags | (junction) | Không liệt kê riêng trong SRS |
| note_tags | (junction) | Không liệt kê riêng trong SRS |
| ai_usage_logs | ✗ | Thêm hợp lý cho thống kê |

### 1.2 Bảng / cột dư thừa hoặc denormalized

| Vấn đề | Chi tiết | Mức độ | Đề xuất |
|--------|----------|--------|---------|
| **D1. `document_chunks.content` + `content_markdown`** | Lưu song song plain text và markdown | Thấp | MVP chỉ cần `content_markdown`; bỏ `content` hoặc dùng generated column |
| **D2. `documents.user_id` + `workspaces.user_id`** | `user_id` lặp lại trên documents, websites, notes | Thấp | Giữ vì tối ưu query bảo mật (`WHERE user_id = ?`), nhưng cần trigger/constraint đồng bộ khi đổi workspace |
| **D3. `flashcards.user_id` / `quizzes.user_id`** | Đã có qua `documents.user_id` | Thấp | Có thể bỏ nếu luôn query qua document |
| **D4. `chats.message_count`** | Denormalized, có thể `COUNT(*)` | Thấp | Giữ cho performance hoặc bỏ ở MVP |
| **D5. ERD `websites.url UK` toàn cục** | Schema thực tế: `UNIQUE(user_id, url)` | Trung bình | Sửa ERD cho khớp schema — đúng hơn theo user |

### 1.3 Quan hệ thiếu hoặc không nhất quán

| ID | Vấn đề | Tác động | Đề xuất sửa |
|----|--------|----------|-------------|
| **D6** | `citations.source_type` có `'note'` nhưng **không có `note_id` FK** | Không thể trích dẫn ghi chú trong chat | Thêm `note_id UUID REFERENCES notes(id)` |
| **D7** | `bookmarks` dùng polymorphic (`entity_type` + `entity_id`) **không có FK** | Orphan bookmarks, không referential integrity | Chấp nhận cho MVP; thêm cleanup job hoặc dùng 4 bảng junction |
| **D8** | `notes.search_vector` **không có trigger** cập nhật FTS | Search notes không hoạt động | Thêm trigger tương tự `document_chunks` |
| **D9** | **Thiếu `refresh_tokens`** table | API `/auth/refresh` và NFR-02.1 (refresh 7 ngày) không implement được | Thêm bảng `refresh_tokens` hoặc bỏ refresh token khỏi MVP |
| **D10** | **Thiếu token blacklist** cho logout | `POST /auth/logout` chỉ xóa client-side JWT | MVP: client-only logout; Full: thêm `token_blacklist` hoặc Redis |
| **D11** | **Không có bảng lưu AI Summary / Keywords / Mindmap** | API `/ai/summarize`, `/ai/keywords`, `/ai/mindmap` chỉ trả ephemeral | Thêm `document_summaries` hoặc ghi rõ “không persist” trong API |
| **D12** | **Di chuyển Folder giữa Workspace** (FR-05.2) | `folders.workspace_id` đổi nhưng `documents.workspace_id`, `websites.workspace_id`, `notes.workspace_id` **không tự cập nhật** | Transaction cascade update hoặc bỏ FR-05.2 khỏi MVP |
| **D13** | **Thiếu UNIQUE `(oauth_provider, oauth_id)`** khi oauth_id NOT NULL | OAuth user có thể duplicate | Thêm partial unique index |
| **D14** | `folders.parent_id` hỗ trợ nested folder nhưng SRS ghi **Could** | Phức tạp UI/API không có trong MVP | Giữ schema, UI chỉ 1 cấp folder |

### 1.4 Ma trận quan hệ — Đánh giá tổng thể

```
users ──1:1── user_profiles          ✓ Đúng
users ──1:N── workspaces             ✓ Đúng
workspaces ──1:N── folders           ✓ Đúng
workspaces ──1:N── documents         ✓ Đúng (kèm folder_id optional)
documents ──1:N── document_chunks    ✓ Đúng — core của Source Tracking
documents ──N:M── tags               ✓ Qua document_tags
chats ──1:N── chat_messages          ✓ Đúng
chat_messages ──1:N── citations      ✓ Đúng
citations ──?── notes                ✗ THIẾU note_id
```

**Điểm mạnh schema:** `document_chunks` với `page_number`, `line_start`, `line_end` + `search_vector` là thiết kế đúng hướng cho citation không cần vector DB.

---

## 2. Review API ↔ Database

### 2.1 API có đủ bảng hỗ trợ

| Nhóm API | Bảng sử dụng | Khớp? |
|----------|--------------|-------|
| `/auth/register`, `/login` | users, user_profiles | ✓ |
| `/auth/forgot-password`, `/reset-password` | users.reset_token | ✓ |
| `/users/me/*` | users, user_profiles | ✓ |
| `/workspaces/*`, `/folders/*` | workspaces, folders | ✓ |
| `/documents/*` | documents, document_chunks, document_tags, tags | ✓ |
| `/websites/*` | websites, website_contents | ✓ |
| `/chats/*` | chats, chat_messages, citations | ✓ |
| `/ai/flashcards`, `/ai/quiz` | flashcards, quizzes | ✓ |
| `/notes/*` | notes, note_tags | ✓ (thiếu API gắn tag) |
| `/bookmarks/*` | bookmarks | ✓ |
| `/dashboard/stats` | aggregate + ai_usage_logs | ✓ |
| `/admin/*` | users + all tables | ✓ |

### 2.2 API thiếu cột / bảng / logic DB

| ID | API | Vấn đề | Đề xuất |
|----|-----|--------|---------|
| **A1** | `POST /auth/refresh` | Không có `refresh_tokens` table | Bỏ endpoint MVP hoặc thêm bảng |
| **A2** | `POST /auth/logout` | Không có server-side invalidation | Document: client-only logout cho MVP |
| **A3** | `POST /ai/summarize/{id}` | Không persist | Response only; hoặc thêm `document_summaries` |
| **A4** | `POST /ai/keywords/{id}` | Không có bảng keywords | Trả về inline hoặc gắn vào tags |
| **A5** | `POST /ai/notes/{id}` | Không phân biệt AI note vs user note | Tạo record trong `notes` với flag `is_ai_generated` |
| **A6** | `POST /ai/mindmap/{id}` | Không có bảng mindmap | JSON response only (ephemeral) |
| **A7** | `POST /documents/{id}/tags` | Chỉ gắn, **không có API gỡ tag** | Thêm `DELETE /documents/{id}/tags/{tag_id}` |
| **A8** | `GET /notes/*` | `note_tags` tồn tại nhưng **không có API tag cho notes** | Thêm endpoints hoặc bỏ `note_tags` khỏi MVP |
| **A9** | `PUT /folders/{id}/move` | Cần cascade update workspace_id trên children | Implement service layer transaction |
| **A10** | `GET /statistics/*` vs `GET /dashboard/*` | **Trùng lặp** chức năng thống kê | Gộp: dashboard = user view, statistics = detailed charts |
| **A11** | `POST /chats` | Request chỉ show `workspace_id`; DB có `folder_id`, `document_id` | Bổ sung schema request đầy đủ theo `chat_mode` |
| **A12** | `GET /documents/{id}/content` | Không rõ lấy từ `file_path` hay aggregate `chunks` | Document: ưu tiên chunks markdown đã xử lý |
| **A13** | `POST /websites/{id}/recrawl` | Không định nghĩa xóa `website_contents` cũ | Delete + re-insert hoặc upsert by content_index |

### 2.3 Response API vs cột DB

| Field API response | Cột DB | Khớp? |
|--------------------|--------|-------|
| `user.full_name` | user_profiles.full_name | ✓ (join) |
| `user.created_at` | users.created_at | ✓ |
| `workspace.folder_count` | computed | ✓ (không lưu DB) |
| `document.status: processing` | document_status enum | ✓ |
| `citation.source_name` | citations.source_name | ✓ |
| `chat.total_ai_queries` | ai_usage_logs COUNT | ✓ |
| `GET /users/me` thiếu `gender` trong register flow | user_profiles.gender | ✓ có cột, default OK |

### 2.4 Đếm endpoint

| Loại | Số lượng |
|------|----------|
| Tổng endpoint thiết kế (doc 07) | ~65 |
| MVP đề xuất (doc 14) | 20 |
| Endpoint cần cho MVP tối ưu (đề xuất §6) | **16** |

---

## 3. Review Use Case ↔ SRS

### 3.1 Vấn đề đánh số Use Case — Nghiêm trọng

Hai tài liệu dùng **hệ thống đánh số UC hoàn toàn khác nhau**:

| SRS (ma trận §7) | Use Case Diagram (doc 02) | Nội dung thực tế |
|------------------|---------------------------|------------------|
| UC-01 ~ UC-05 Auth | UC-01 ~ UC-06 Auth | UC-06 = Logout trong diagram, Profile trong SRS |
| UC-06 ~ UC-08 Profile | UC-07 ~ UC-09 Profile | Lệch 1 số |
| UC-09 Dashboard | UC-23 Dashboard | Khác hoàn toàn |
| UC-10 ~ UC-13 Workspace | UC-10 Workspace (gộp) | SRS tách 4 UC, diagram gộp 1 |
| UC-30 ~ UC-36 AI Chat | UC-17 AI Chat (overview) / UC-30~41 (detail) | 3 hệ số khác nhau |
| UC-37 Citation | UC-18 / UC-40 | Trùng / lệch |
| UC-51 ~ UC-54 Admin | UC-26 ~ UC-28 | Khác số |

**Khuyến nghị:** Chuẩn hóa 1 bảng UC master duy nhất, map `FR-xx` → `UC-xx` → API → DB → Page.

### 3.2 SRS có nhưng Use Case thiếu / không đủ chi tiết

| FR ID | Yêu cầu SRS | Use Case | Trạng thái |
|-------|-------------|----------|------------|
| FR-01.9 | Reset password (riêng forgot) | Chỉ UC-05 Quên MK | ⚠️ Thiếu UC Reset Password |
| FR-05.2 | Di chuyển Folder giữa Workspace | Không có | ✗ Thiếu |
| FR-05.3 | Folder lồng nhau | parent_id trong DB, không UC | ⚠️ Thiếu |
| FR-06.6 | Document Viewer highlight citation | Không có | ✗ Thiếu |
| FR-08.4 | Folder Chat | UC-34 (detail diagram) | ✓ Có trong detail |
| FR-08.5 | Document Chat | UC-35 | ✓ |
| FR-10.5 | Sinh ghi chú AI | Không có UC riêng | ✗ Thiếu |
| FR-10.6 | Sinh Mindmap | Không có | ✗ Thiếu |
| FR-14 | Statistics (riêng Dashboard) | UC-24 gộp mơ hồ với UC-23 | ⚠️ Không tách bạch |

### 3.3 Use Case có nhưng SRS không nhấn mạnh / priority khác

| UC | Ghi chú |
|----|---------|
| UC-56~58 Document Processing | Đúng là include của Upload — nên đánh dấu `<<include>>` system use case, không phải user-facing |
| UC-41 Mở tài liệu gốc | SRS: Should — diagram detail có, overview không |

### 3.4 Ma trận truy vết SRS → UC (đề xuất chuẩn hóa)

| Module SRS | FR Count (Must) | UC đề xuất | Coverage |
|------------|-----------------|------------|----------|
| Auth | 7 Must + 2 Should | UC-A01~A08 | 88% (OAuth Could) |
| Profile | 5 Must | UC-P01~P04 | 100% |
| Dashboard | 2 Must + 2 Should | UC-D01~D02 | 100% |
| Workspace | 3 Must | UC-W01~W04 | 100% |
| Folder | 1 Must + 1 Should | UC-F01~F04 | 75% (move = Should) |
| Knowledge | 5 Must + 1 Should | UC-K01~K08 | 100% |
| Website | 4 Must + 1 Should | UC-WB01~WB05 | 100% |
| AI Chat | 7 Must + 1 Should | UC-C01~C10 | 100% |
| Citation | 3 Must + 1 Should | UC-CT01~CT03 | 100% |
| AI Doc | 3 Must + 2 Should + 1 Could | UC-AI01~AI06 | 83% |
| Notes | 2 Must | UC-N01~N04 | 100% |
| Bookmark | 1 Should | UC-B01 | 100% |
| Search | 2 Must | UC-S01 | 100% |
| Statistics | 1 Must + 2 Should | UC-ST01~ST03 | 100% |
| Admin | 2 Must + 1 Should | UC-AD01~AD04 | 100% |

---

## 4. Review UI ↔ Chức năng

### 4.1 Bảng đối chiếu trang ↔ wireframe ↔ SRS

| # | Trang (doc 08) | Wireframe (doc 10) | SRS Module | Khớp? |
|---|----------------|-------------------|------------|-------|
| 1 | Landing Page | ✓ §10.2 | Public | ✓ |
| 2 | Login | ✓ §10.3 | FR-01 | ✓ |
| 3 | Register | ✗ Thiếu | FR-01.1 | ⚠️ |
| 4 | Forgot Password | ✗ Thiếu | FR-01.8 | ⚠️ |
| 5 | Dashboard | ✓ §10.5 | FR-03 | ✓ (wireframe có chart — SRS Should) |
| 6 | Workspace List | ✗ (gộp trong §10.8) | FR-04 | ⚠️ |
| 7 | Workspace Detail | ✓ §10.8 | FR-04,05,06,07,11 | ✓ |
| 8 | Folder Detail | ✗ Thiếu | FR-05 | ⚠️ |
| 9 | Document List | ✗ (tab trong workspace) | FR-06 | ⚠️ Trùng route `/documents` |
| 10 | Document Viewer | ✓ §10.7 | FR-06, FR-10 | ⚠️ Wireframe có AI panel — không trong MVP |
| 11 | Website Knowledge | ✗ Thiếu | FR-07 | ✗ |
| 12 | AI Chat | ✓ §10.6 | FR-08, FR-09 | ✓ |
| 13 | Chat History | Gộp trong §10.6 sidebar | FR-08.7 | ⚠️ Trùng `/chat` và `/chat-history` |
| 14 | Notes | ✗ Thiếu | FR-11 | ✗ |
| 15 | Bookmark | ✗ Thiếu | FR-12 | ✗ |
| 16 | Statistics | ✗ Thiếu | FR-14 | ✗ |
| 17 | Profile | ✗ Thiếu | FR-02 | ⚠️ |
| 18-21 | Admin (4 trang) | ✗ Thiếu | FR-15 | ✗ |

**Kết quả:** 21 trang được khai báo, **chỉ 6 wireframe chi tiết** (29%). Sidebar layout (§10.4) hiển thị đủ module nhưng nhiều module chưa có thiết kế màn hình.

### 4.2 Mâu thuẫn UI cụ thể

| ID | Mâu thuẫn | Tài liệu |
|----|-----------|----------|
| **U1** | Header có **Global Search** (§10.4) | MVP (doc 14) loại Global Search |
| **U2** | Login có **Google/Facebook** buttons (§10.3) | MVP loại OAuth |
| **U3** | Dashboard wireframe có **Bar/Line Chart** | MVP chỉ stats cards |
| **U4** | Document Viewer có **Flashcard/Quiz panel** | MVP loại AI Doc Assistant |
| **U5** | Chat wireframe có **"Mở tài liệu →"** | MVP loại citation jump |
| **U6** | Route `/chat` và `/chat-history` **trùng chức năng** với ChatSidebar | Nên gộp 1 trang |
| **U7** | Route `/documents` riêng vs tab trong Workspace Detail | 2 cách điều hướng — cần chọn 1 |
| **U8** | AdminLayout + 4 admin pages | Không có wireframe, không trong MVP |
| **U9** | `ConfirmDialog` logout (§10.9) | ✓ Khớp FR-01.7 | |
| **U10** | Workspace Detail tabs: Website, Ghi chú | Module chưa trong MVP nhưng UI đã thiết kế |

### 4.3 Component frontend vs scope

| Component | Full design | MVP cần? |
|-----------|-------------|----------|
| ChatWindow, CitationList | ✓ | **Bắt buộc** |
| PdfViewer với page jump | ✓ | Không (MVP) |
| FlashcardDeck, QuizPanel | ✓ | Không |
| MarkdownEditor | ✓ | Không |
| GlobalSearch | ✓ | Không |
| LineChart, BarChart, PieChart | ✓ | Không |
| MindmapViewer | ✓ | Không |

---

## 5. Khó khăn triển khai — Sinh viên năm 3

### 5.1 Phân loại theo mức độ khó

#### 🔴 Rất khó (thường vượt năng lực nếu không có mentor)

| # | Hạng mục | Lý do |
|---|----------|-------|
| K1 | **Citation System end-to-end** | Cần: FTS → chọn chunks → prompt engineering → map response → lưu citations. Lỗi nhỏ = hallucination hoặc nguồn sai |
| K2 | **Document processing pipeline** | PyMuPDF, python-docx, chunking với page/line metadata, async processing |
| K3 | **PostgreSQL Full-Text Search** | `tsvector`, triggers, ranking, scoped search theo workspace/folder |
| K4 | **Gemini API integration** | Rate limit, token counting, error handling, context window management |
| K5 | **Web crawler** | robots.txt, JS-rendered pages, encoding, rate limiting, malformed HTML |

#### 🟠 Khó (có thể làm với hướng dẫn)

| # | Hạng mục | Lý do |
|---|----------|-------|
| K6 | OAuth Google/Facebook | Redirect flow, state, callback, account linking |
| K7 | JWT refresh + logout invalidation | Stateless vs stateful session |
| K8 | Celery + Redis workers | DevOps, debugging distributed tasks |
| K9 | PDF Viewer + jump to page | react-pdf hoặc iframe, sync với citation |
| K10 | Shadcn UI + React Query + TypeScript | Learning curve stack hiện đại |
| K11 | Docker Compose multi-service | 5 containers: nginx, api, worker, db, redis |
| K12 | FastAPI layered architecture | models/schemas/services/routes tách biệt |

#### 🟡 Trung bình (phù hợp học tập)

| # | Hạng mục | Lý do |
|---|----------|-------|
| K13 | CRUD Workspace/Folder/Document | Pattern lặp, tốt cho học |
| K14 | Auth register/login bcrypt JWT | Bài lab phổ biến |
| K15 | Dashboard stats aggregation | SQL COUNT/GROUP BY |
| K16 | Markdown editor cho Notes | Dùng thư viện có sẵn |
| K17 | Dark/Light mode | Tailwind + CSS variables |

### 5.2 Ước lượng effort (1 developer full-stack)

| Scope | Tuần công | Realistic team 3-4 SV? |
|-------|-----------|------------------------|
| Full 15 modules (doc 13) | ~80 tuần-công | ✗ Không (1 học kỳ = 16 tuần) |
| MVP doc 14 (8 tuần, 4 người) | ~32 tuần-công | ✓ Có thể (vừa sức) |
| MVP tối ưu 6 tuần (đề xuất §6) | ~18 tuần-công | ✓ Khả thi (3-4 người) |

### 5.3 Rủi ro đặc thù môi trường sinh viên

| Rủi ro | Mô tả | Giảm thiểu |
|--------|-------|------------|
| Gemini API key / chi phí | Cần billing Google Cloud | Dùng free tier, mock AI khi dev |
| Máy yếu chạy Docker | 5 containers nặng | MVP: chỉ PG + API, không Redis/Celery |
| Không có SMTP | Forgot password không test được | Bỏ khỏi MVP |
| Deadline đồ án | Scope creep từ 15 tài liệu | Khóa scope MVP, freeze features |
| Phân công team | Full stack overlap | 1 BE lead, 1 FE lead, chia module rõ |

---

## 6. Đề xuất MVP tối ưu (6–8 tuần)

### 6.1 Nguyên tắc cắt scope

1. **Một luồng demo hoàn chỉnh** quan trọng hơn 15 module dở dang
2. **Citation hiển thị** quan trọng hơn citation jump
3. **TXT + MD + PDF** đủ demo; DOCX thêm nếu còn thời gian
4. **Global Chat only** trước; Workspace scope thêm tuần 7-8
5. **Không OAuth, không Celery, không Admin, không Website**

### 6.2 MVP-6W — Phiên bản 6 tuần (nhóm 3-4 SV, part-time)

**Mục tiêu:** Đăng ký → Upload tài liệu → Chat AI → Thấy citation

| Tuần | Deliverable |
|------|-------------|
| 1 | Setup monorepo, PostgreSQL, Auth (register/login JWT), Layout shell |
| 2 | Workspace CRUD, Folder CRUD (1 cấp, không move) |
| 3 | Upload TXT/MD/PDF, extract text, lưu chunks đơn giản (không markdown phức tạp) |
| 4 | Document list + viewer cơ bản (markdown render; PDF iframe) |
| 5 | AI Chat Global: FTS đơn giản (ILIKE hoặc tsvector) + Gemini + citations |
| 6 | Polish: logout dialog, dashboard counts, demo script, fix bugs |

**Scope MVP-6W:**

| Feature | Included |
|---------|----------|
| Auth email | ✓ |
| Workspace + Folder | ✓ (không move, không nested) |
| Upload | TXT, MD, PDF only |
| Processing | Sync (không background worker) |
| AI Chat | Global mode only |
| Citations | Hiển thị tên file + excerpt (không page/line chính xác) |
| Dashboard | 4 stat cards |
| UI | Light mode only, desktop first |

**Bảng DB MVP-6W (8 bảng):**
```
users, user_profiles, workspaces, folders,
documents, document_chunks,
chats, chat_messages, citations
```

**API MVP-6W (16 endpoints):**
```
POST   /auth/register
POST   /auth/login
GET    /users/me
PUT    /users/me
GET    /dashboard/stats
GET/POST/PUT/DELETE  /workspaces[/{id}]
GET/POST             /workspaces/{id}/folders
PUT/DELETE           /folders/{id}
POST                 /documents/upload
GET/DELETE           /documents[/{id}]
GET/POST             /chats[/{id}/messages]
```

**Trang MVP-6W (8 trang):**
Login, Register, Dashboard, Workspaces, Workspace Detail, Documents, Chat, Profile

---

### 6.3 MVP-8W — Phiên bản 8 tuần (khuyến nghị — cải tiến doc 14)

**Mục tiêu:** MVP-6W + Workspace-scoped chat + DOCX + citation có page/line + dark mode

| Tuần | Thêm so với MVP-6W |
|------|-------------------|
| 7 | DOCX processor, Workspace Chat mode, `ai_usage_logs`, đổi tên/xóa chat |
| 8 | Citation với page/line, Document viewer MD tốt hơn, Dark mode, responsive cơ bản |

**Điều chỉnh so với doc 14 hiện tại:**

| Doc 14 hiện tại | Đề xuất MVP-8W | Lý do |
|-----------------|----------------|-------|
| 12 trang | **10 trang** (bỏ Landing P1, gộp Chat History) | Giảm UI overhead |
| 20 endpoints | **22 endpoints** (+PUT chat, +GET documents list filter) | Đủ rename chat |
| 10 bảng | **10 bảng** (giữ nguyên) | ✓ |
| Folder Detail page riêng | **Bỏ** — dùng tab trong Workspace Detail | Giảm 1 trang |
| Workspace search | **Bỏ** — filter client-side | Đủ MVP |
| Avatar upload | **Optional** — initials fallback | Giảm file upload complexity |
| JWT no refresh | **Giữ** | ✓ Đúng |

**Trang MVP-8W (10 trang):**

| # | Trang | Route |
|---|-------|-------|
| 1 | Login | `/login` |
| 2 | Register | `/register` |
| 3 | Dashboard | `/dashboard` |
| 4 | Workspaces | `/workspaces` |
| 5 | Workspace Detail (gồm folders + documents) | `/workspaces/:id` |
| 6 | Document Viewer | `/documents/:id` |
| 7 | AI Chat (gồm history sidebar) | `/chat`, `/chat/:id` |
| 8 | Profile | `/profile` |
| 9 | Landing (tùy chọn) | `/` |
| — | ~~Chat History~~ | Gộp vào Chat |
| — | ~~Folder Detail~~ | Tab trong Workspace |
| — | ~~Document List~~ | Tab trong Workspace |

### 6.4 So sánh 3 phiên bản MVP

| Tiêu chí | MVP-6W | MVP-8W (khuyến nghị) | MVP doc 14 | Full SRS |
|----------|--------|----------------------|------------|----------|
| Thời gian | 6 tuần | 8 tuần | 8 tuần | 20 tuần |
| Team | 3-4 SV | 3-4 SV | 4 SV | 6+ người |
| Bảng DB | 8 | 10 | 10 | 18 |
| API endpoints | 16 | 22 | 20 | 65 |
| Trang UI | 8 | 10 | 12 | 21 |
| File types | 3 | 4 | 4 | 10 |
| Chat modes | Global | Global + Workspace | Global + Workspace | 4 modes |
| Citation | Basic | Page/line | Page/line | + jump to source |
| Background job | Sync | Sync | BackgroundTasks | Celery |
| Điểm demo | 7/10 | **9/10** | 8/10 | 10/10 |

---

## 7. Danh sách sửa đổi khuyến nghị (Priority)

### P0 — Sửa trước khi code

| # | Tài liệu | Sửa |
|---|----------|-----|
| 1 | doc 02 + doc 01 | Chuẩn hóa bảng mã UC duy nhất |
| 2 | doc 06 | Thêm `note_id` vào `citations` HOẶC bỏ `'note'` khỏi enum |
| 3 | doc 06 | Thêm trigger FTS cho `notes` |
| 4 | doc 07 + doc 06 | Quyết định refresh token: thêm bảng hoặc bỏ `/auth/refresh` |
| 5 | doc 08 + doc 10 | Gộp Chat History vào Chat; bỏ route `/chat-history` |
| 6 | doc 14 | Cập nhật theo MVP-8W §6.3 |

### P1 — Sửa trong sprint 1

| # | Tài liệu | Sửa |
|---|----------|-----|
| 7 | doc 05 | Sửa `websites.url UK` → `UNIQUE(user_id, url)` |
| 8 | doc 07 | Thêm request body đầy đủ cho `POST /chats` theo chat_mode |
| 9 | doc 07 | Thêm `DELETE /documents/{id}/tags/{tag_id}` |
| 10 | doc 10 | Thêm wireframe Register, Profile, Forgot Password |
| 11 | doc 09 | MVP: bỏ Celery workers khỏi docker-compose |

### P2 — Sau MVP

| # | Sửa |
|---|-----|
| 12 | Thêm `document_summaries` table hoặc document API behavior |
| 13 | Cascade update khi move folder cross-workspace |
| 14 | Token blacklist cho logout |
| 15 | Wireframe cho Website, Notes, Admin |

---

## 8. Kết luận

### Điểm mạnh thiết kế
- Kiến trúc Markdown + FTS + Source Tracking **phù hợp** mục tiêu giảm tài nguyên
- Schema `document_chunks` với metadata vị trí là **nền tảng tốt** cho citation
- API RESTful có cấu trúc rõ, pagination/error format thống nhất
- Roadmap 5 phase logic, MVP doc 14 đã có hướng cắt scope

### Điểm yếu cần khắc phục
- **Ma trận truy vết 4 chiều** (SRS–UC–API–UI) chưa đồng bộ
- Một số API **thiết kế trước DB** (refresh token, AI summary persist)
- UI **over-designed** so với MVP (21 trang, 9 wireframe thiếu)
- Full scope **không phù hợp** timeline sinh viên năm 3

### Khuyến nghị cuối

> **Triển khai theo MVP-8W (§6.3)**, team 3–4 sinh viên, lock scope sau tuần 2. Ưu tiên chứng minh luồng **Upload → Chat AI → Citation** trước khi mở rộng Website, Notes, Admin. Nếu chỉ còn 6 tuần, dùng **MVP-6W** và chấp nhận citation đơn giản hơn.

---

## Phụ lục A — Checklist review từng tài liệu

| Doc | Tên | Đánh giá | Ghi chú |
|-----|-----|----------|---------|
| 01 | SRS | ⭐⭐⭐⭐ | Đầy đủ; ma trận UC lệch doc 02 |
| 02 | Use Case | ⭐⭐⭐ | Đánh số lộn xộn; cần chuẩn hóa |
| 03 | Activity | ⭐⭐⭐⭐ | Flow rõ; OAuth/Celery phức tạp cho SV |
| 04 | Sequence | ⭐⭐⭐⭐ | Khớp logic; WebSocket chưa có trong API |
| 05 | ERD | ⭐⭐⭐⭐ | Tốt; sửa URL unique, thêm note_id citation |
| 06 | DB Schema | ⭐⭐⭐⭐ | Production-ready; thiếu refresh_tokens |
| 07 | API Design | ⭐⭐⭐⭐ | Đầy đủ; một số endpoint chưa có DB |
| 08 | Frontend Structure | ⭐⭐⭐ | Quá nhiều component cho MVP |
| 09 | Backend Structure | ⭐⭐⭐⭐ | Tốt; Celery có thể trì hoãn |
| 10 | Wireframe | ⭐⭐⭐ | 6/21 trang; thiếu nhiều |
| 11 | Architecture | ⭐⭐⭐⭐ | Rõ ràng |
| 12 | DFD | ⭐⭐⭐⭐ | Khớp module |
| 13 | Roadmap | ⭐⭐⭐ | 20 tuần optimistic cho SV |
| 14 | MVP | ⭐⭐⭐⭐ | Tốt; cần tinh theo §6.3 |
| 15 | Future | ⭐⭐⭐⭐ | Hợp lý, không ảnh hưởng MVP |

## Phụ lục B — Ma trận FR → MVP-8W

| FR | MVP-8W |
|----|--------|
| FR-01.1~01.3, 01.6~01.7 | ✓ |
| FR-01.4~01.5 OAuth | ✗ |
| FR-01.8~01.9 Forgot password | ✗ |
| FR-02.1~02.2 Profile | ✓ |
| FR-02.3~02.4 Password/Avatar | Partial |
| FR-03.1 Dashboard stats | ✓ |
| FR-03.2~03.4 Charts/Recent | ✗ |
| FR-04.1~04.3 Workspace | ✓ |
| FR-05.1 Folder CRUD | ✓ |
| FR-05.2~05.3 Move/Nested | ✗ |
| FR-06.1 Upload 4 types | ✓ |
| FR-06.2~06.5 Document mgmt | ✓ |
| FR-06.6 Citation highlight | ✗ |
| FR-07 Website | ✗ |
| FR-08.1~08.3, 08.6~08.7 Chat | ✓ |
| FR-08.4~08.5 Folder/Doc chat | ✗ |
| FR-08.8 Search chat | ✗ |
| FR-09.1~09.2, 09.4 Citation | ✓ |
| FR-09.3 Open source | ✗ |
| FR-10 AI Doc Assistant | ✗ |
| FR-11 Notes | ✗ |
| FR-12 Bookmark | ✗ |
| FR-13 Global Search | ✗ |
| FR-14 Statistics | ✗ |
| FR-15 Admin | ✗ |

**Coverage MVP-8W:** ~45% FR Must-have, **~90% giá trị demo cốt lõi** (Knowledge + AI Chat + Citation).
