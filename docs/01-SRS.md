# 1. Software Requirement Specification (SRS)


## 1. Giới thiệu

### 1.1 Mục đích

Tài liệu này mô tả đầy đủ các yêu cầu chức năng và phi chức năng cho hệ thống **DevHub AI** — nền tảng quản lý tri thức cá nhân kết hợp AI dành cho sinh viên CNTT, lập trình viên và người tự học công nghệ.

### 1.2 Phạm vi

Hệ thống cho phép người dùng:
- Lưu trữ và tổ chức tài liệu kỹ thuật, website, ghi chú
- Sử dụng AI để tra cứu, hỏi đáp dựa trên dữ liệu cá nhân
- Nhận trích dẫn nguồn chính xác cho mọi câu trả lời AI
- Sinh flashcard, quiz, tóm tắt từ tài liệu
- Theo dõi thống kê học tập qua Dashboard

### 1.3 Đối tượng sử dụng

| Vai trò | Mô tả |
|---------|-------|
| **Guest** | Truy cập Landing Page, đăng ký, đăng nhập |
| **User** | Người dùng chính — quản lý tri thức cá nhân |
| **Admin** | Quản trị hệ thống, quản lý người dùng và dữ liệu |

### 1.4 Định nghĩa, từ viết tắt

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| Workspace | Không gian làm việc chủ đề (Python, ReactJS, ...) |
| Folder | Thư mục con trong Workspace |
| Chunk | Đoạn nội dung được trích xuất từ tài liệu, có metadata vị trí |
| Citation | Trích dẫn nguồn trong câu trả lời AI |
| Source Tracking | Theo dõi nguồn gốc nội dung (trang, dòng, URL) |

---

## 2. Mô tả tổng quan

### 2.1 Bối cảnh hệ thống

```
┌─────────────┐     HTTPS      ┌─────────────┐     REST API    ┌─────────────┐
│   Browser   │ ◄────────────► │   Nginx     │ ◄─────────────► │   FastAPI   │
│  (React)    │                │  (Reverse   │                 │   Backend   │
└─────────────┘                │   Proxy)    │                 └──────┬──────┘
                               └─────────────┘                        │
                                                                      ▼
                                                              ┌─────────────┐
                                                              │ PostgreSQL  │
                                                              └─────────────┘
                                                                      │
                                                                      ▼
                                                              ┌─────────────┐
                                                              │ Gemini API  │
                                                              └─────────────┘
```

### 2.2 Kiến trúc lưu trữ tri thức

Hệ thống **không sử dụng Vector Database**. Thay vào đó:

1. Tài liệu upload → trích xuất text → chuyển Markdown → lưu `document_chunks` với metadata (page, line_start, line_end)
2. Website crawl → HTML → Markdown → lưu `website_contents` với heading hierarchy
3. AI Chat → Full-text search (PostgreSQL `tsvector`) + keyword matching → đưa context có citation vào Gemini → trả lời kèm nguồn

---

## 3. Yêu cầu chức năng

### FR-01: Authentication (Module 1)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-01.1 | Đăng ký bằng Email với validation | Must |
| FR-01.2 | Kiểm tra Email đã tồn tại | Must |
| FR-01.3 | Mã hóa mật khẩu (bcrypt) | Must |
| FR-01.4 | Đăng ký/đăng nhập Google OAuth | Should |
| FR-01.5 | Đăng ký/đăng nhập Facebook OAuth | Could |
| FR-01.6 | Đăng nhập Email + Password, trả JWT | Must |
| FR-01.7 | Đăng xuất với popup xác nhận | Must |
| FR-01.8 | Quên mật khẩu — gửi email reset | Must |
| FR-01.9 | Reset password qua token | Must |

### FR-02: User Profile (Module 2)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-02.1 | Hiển thị Avatar, Họ tên, Email, Giới tính, Ngày tạo | Must |
| FR-02.2 | Cập nhật thông tin cá nhân | Must |
| FR-02.3 | Đổi mật khẩu | Must |
| FR-02.4 | Upload/thay đổi Avatar | Must |
| FR-02.5 | Giới tính: Nam, Nữ, Khác, Không muốn tiết lộ | Must |

### FR-03: Dashboard (Module 3)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-03.1 | Hiển thị tổng Workspace, Folder, Document, Website, Note, Chat, AI Query | Must |
| FR-03.2 | Biểu đồ tài liệu theo thời gian | Should |
| FR-03.3 | Biểu đồ sử dụng AI | Should |
| FR-03.4 | Danh sách tài liệu/website gần đây | Must |

### FR-04: Workspace Management (Module 4)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-04.1 | CRUD Workspace | Must |
| FR-04.2 | Tìm kiếm Workspace | Must |
| FR-04.3 | Mỗi user có nhiều Workspace độc lập | Must |

### FR-05: Folder Management (Module 5)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-05.1 | CRUD Folder trong Workspace | Must |
| FR-05.2 | Di chuyển Folder giữa Workspace | Should |
| FR-05.3 | Folder lồng nhau (1 cấp) | Could |

### FR-06: Knowledge Base (Module 6)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-06.1 | Upload: PDF, DOCX, DOC, TXT, MD, PPTX, XLSX, CSV, JSON, HTML | Must |
| FR-06.2 | Trích xuất nội dung → Markdown chunks | Must |
| FR-06.3 | CRUD, đổi tên, gắn Tag, Mô tả | Must |
| FR-06.4 | Metadata: tên, loại, kích thước, ngày upload, workspace, folder | Must |
| FR-06.5 | Tìm kiếm theo tên, nội dung, tag, loại file | Must |
| FR-06.6 | Document Viewer với highlight citation | Should |

### FR-07: Website Knowledge Collector (Module 7)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-07.1 | Thêm URL website | Must |
| FR-07.2 | Crawl nội dung, trích xuất heading/paragraph | Must |
| FR-07.3 | Chuyển thành Markdown, lưu DB | Must |
| FR-07.4 | Cập nhật nội dung mới (re-crawl) | Should |
| FR-07.5 | Tìm kiếm website | Must |

### FR-08: AI Chat Assistant (Module 8)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-08.1 | Chat AI dựa trên dữ liệu người dùng | Must |
| FR-08.2 | Global Chat — toàn bộ dữ liệu | Must |
| FR-08.3 | Workspace Chat — scoped theo workspace | Must |
| FR-08.4 | Folder Chat — scoped theo folder | Must |
| FR-08.5 | Document Chat — scoped theo document | Must |
| FR-08.6 | Đổi tên, xóa cuộc trò chuyện | Must |
| FR-08.7 | Lưu lịch sử chat | Must |
| FR-08.8 | Tìm kiếm lịch sử chat | Should |

### FR-09: Citation System (Module 9) — BẮT BUỘC

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-09.1 | Mọi câu trả lời AI phải có nguồn trích dẫn | Must |
| FR-09.2 | Hiển thị: tên tài liệu, trang, dòng, URL website | Must |
| FR-09.3 | "Mở tài liệu gốc" — nhảy đến trang/dòng nguồn | Should |
| FR-09.4 | Lưu citations vào DB liên kết chat_message | Must |

### FR-10: AI Document Assistant (Module 10)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-10.1 | Tóm tắt tài liệu (AI Summary) | Must |
| FR-10.2 | Sinh Flashcard (Q&A) | Must |
| FR-10.3 | Sinh Quiz trắc nghiệm | Must |
| FR-10.4 | Trích xuất từ khóa | Should |
| FR-10.5 | Sinh ghi chú AI | Should |
| FR-10.6 | Sinh Mindmap | Could |

### FR-11: Notes (Module 11)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-11.1 | CRUD Note với Markdown Editor | Must |
| FR-11.2 | Liên kết Workspace, Folder, Document | Must |

### FR-12: Bookmark (Module 12)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-12.1 | Bookmark Document, Website, Chat, Note | Should |

### FR-13: Search Engine (Module 13)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-13.1 | Tìm kiếm toàn hệ thống | Must |
| FR-13.2 | Filter theo: File, Website, Workspace, Folder, Note, Chat | Must |

### FR-14: Statistics (Module 14)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-14.1 | Thống kê tổng tài liệu, website, chat | Must |
| FR-14.2 | Top tài liệu/website được truy cập | Should |
| FR-14.3 | Line, Bar, Pie Chart | Should |

### FR-15: Admin Panel (Module 15)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-15.1 | Xem, khóa, xóa User | Must |
| FR-15.2 | Quản lý tài liệu/website toàn hệ thống | Should |
| FR-15.3 | Thống kê: tổng User, Dữ liệu, AI Query | Must |

---

## 4. Yêu cầu phi chức năng

### NFR-01: Hiệu năng

| ID | Yêu cầu | Metric |
|----|---------|--------|
| NFR-01.1 | API response time | < 500ms (95th percentile) |
| NFR-01.2 | AI Chat first token | < 3s |
| NFR-01.3 | Document upload processing | < 30s cho file 10MB |
| NFR-01.4 | Full-text search | < 1s |

### NFR-02: Bảo mật

| ID | Yêu cầu |
|----|---------|
| NFR-02.1 | JWT với expiry 24h, refresh token 7 ngày |
| NFR-02.2 | Password hash bcrypt (cost factor 12) |
| NFR-02.3 | HTTPS only |
| NFR-02.4 | Rate limiting API: 100 req/min/user |
| NFR-02.5 | Input sanitization, SQL injection prevention |
| NFR-02.6 | File upload validation (type, size max 50MB) |
| NFR-02.7 | User data isolation — mỗi user chỉ truy cập dữ liệu của mình |

### NFR-03: Khả năng mở rộng

| ID | Yêu cầu |
|----|---------|
| NFR-03.1 | Horizontal scaling qua Docker |
| NFR-03.2 | Background job queue cho document processing |
| NFR-03.3 | Stateless API design |

### NFR-04: UI/UX

| ID | Yêu cầu |
|----|---------|
| NFR-04.1 | Responsive (mobile, tablet, desktop) |
| NFR-04.2 | Dark Mode / Light Mode |
| NFR-04.3 | Sidebar Navigation |
| NFR-04.4 | Global Search bar |
| NFR-04.5 | Phong cách: Notion + NotebookLM + ChatGPT + Perplexity |

### NFR-05: Khả dụng

| ID | Yêu cầu |
|----|---------|
| NFR-05.1 | Uptime 99.5% |
| NFR-05.2 | Graceful error handling với thông báo thân thiện |
| NFR-05.3 | Auto-save notes mỗi 30 giây |

---

## 5. Ràng buộc

| Loại | Ràng buộc |
|------|-----------|
| Công nghệ | React, FastAPI, PostgreSQL, Gemini API |
| Triển khai | Docker + Nginx |
| Lưu trữ AI | Markdown + Source Tracking (không Vector DB) |
| Ngôn ngữ UI | Tiếng Việt (primary), English (secondary) |

---

## 6. Giả định và phụ thuộc

- Người dùng có kết nối Internet ổn định
- Gemini API key được cấu hình qua environment variable
- SMTP server cho email reset password
- Google/Facebook OAuth credentials được cấu hình

---

## 7. Ma trận truy vết yêu cầu

> **Mã Use Case chuẩn:** xem [00-Use-Case-Master.md](./00-Use-Case-Master.md)

### 7.1 MVP-8W (Official Implementation Target)

| Module | Use Case | API Endpoints | DB Tables |
|--------|----------|---------------|-----------|
| Auth | UC-A01 ~ UC-A04 | `/auth/register`, `/login`, `/logout`, `/refresh` | users, refresh_tokens |
| Profile | UC-P01 ~ UC-P02 | `/users/me` | users, user_profiles |
| Workspace | UC-W01 ~ UC-W05 | `/workspaces/*` | workspaces |
| Folder | UC-F01 ~ UC-F04 | `/workspaces/{id}/folders`, `/folders/*` | folders |
| Document | UC-K01 ~ UC-K07 | `/documents/*` | documents, document_chunks |
| AI Chat | UC-C01 ~ UC-C07 | `/chats/*` | chats, chat_messages |
| Citation | UC-CT01 ~ UC-CT02 | (embedded in `POST /chats/{id}/messages`) | citations |
| Search (FTS) | UC-K07 | (internal — PostgreSQL tsvector) | document_chunks |

### 7.2 Full Product (Post-MVP)

| Module | Use Case | API Endpoints | DB Tables |
|--------|----------|---------------|-----------|
| Auth+ | UC-A05 ~ UC-A08 | `/auth/forgot-password`, `/google/*`, `/facebook/*` | users |
| Profile+ | UC-P03 ~ UC-P04 | `/users/me/password`, `/users/me/avatar` | user_profiles |
| Dashboard | UC-D01 | `/dashboard/*` | (aggregated), ai_usage_logs |
| Website | UC-WB01 ~ UC-WB05 | `/websites/*` | websites, website_contents |
| AI Chat+ | UC-C08 ~ UC-C10 | `/chats/*` (folder/document mode) | chats |
| Citation+ | UC-CT03 | — | citations |
| AI Doc | UC-AI01 ~ UC-AI06 | `/ai/*` | flashcards, quizzes |
| Notes | UC-N01 ~ UC-N04 | `/notes/*` | notes, note_tags |
| Bookmark | UC-B01 | `/bookmarks/*` | bookmarks |
| Global Search | UC-S02 | `/search` | (cross-table) |
| Statistics | UC-ST01 ~ UC-ST03 | `/statistics/*` | ai_usage_logs |
| Admin | UC-AD01 ~ UC-AD04 | `/admin/*` | users, (all) |
| Tags | — | `/tags/*`, `/documents/{id}/tags` | tags, document_tags |
