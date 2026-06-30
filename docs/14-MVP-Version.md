# 14. MVP-8W — Official Implementation Target

**Phiên bản:** 1.1 (P0 fixes applied)  
**Thời gian:** 8 tuần  
**Team:** 3–4 sinh viên (2 Backend + 2 Frontend)  
**Use Case registry:** [00-Use-Case-Master.md](./00-Use-Case-Master.md)

---

## 14.1 MVP Goal

Cho phép người dùng **đăng ký, tổ chức tài liệu theo Workspace/Folder, upload file, chat AI với trích dẫn nguồn chính xác** (tên file, trang, dòng) — chứng minh giá trị cốt lõi DevHub AI.

---

## 14.2 Feature Scope

### Included

#### Authentication (UC-A01 ~ UC-A04)

| Feature | UC ID |
|---------|-------|
| Register | UC-A01 |
| Login | UC-A02 |
| Logout (popup xác nhận) | UC-A03 |
| Refresh Token | UC-A04 |

#### Profile (UC-P01 ~ UC-P02)

| Feature | UC ID |
|---------|-------|
| Xem hồ sơ | UC-P01 |
| Cập nhật họ tên, giới tính | UC-P02 |

#### Knowledge Management

| Feature | UC ID |
|---------|-------|
| Workspace CRUD | UC-W01 ~ UC-W05 |
| Folder CRUD (1 cấp) | UC-F01 ~ UC-F04 |
| Upload Document | UC-K01 |
| Document list & viewer | UC-K02 ~ UC-K04 |
| Xóa document | UC-K05 |

**Supported files:** PDF, DOCX, TXT, Markdown

#### AI Features

| Feature | UC ID |
|---------|-------|
| Global Chat | UC-C06 |
| Workspace Chat | UC-C07 |
| Chat history (list, rename, delete) | UC-C01 ~ UC-C05 |
| Citation System | UC-CT01 ~ UC-CT02 |

**Citation bắt buộc hiển thị:** tên file, số trang, số dòng (line_start / line_end)

#### Search

| Feature | UC ID |
|---------|-------|
| PostgreSQL Full-Text Search | UC-K07 |

FTS dùng nội bộ cho AI Chat và document retrieval — không có Global Search UI.

### Excluded (Post-MVP)

| Feature | Lý do |
|---------|-------|
| Google OAuth | Phức tạp, không cần demo |
| Facebook OAuth | Phức tạp, không cần demo |
| Website Collector | Module riêng, post-MVP |
| Notes | Thay bằng upload MD |
| Bookmark | Nice-to-have |
| Flashcard / Quiz / Mindmap | AI Doc Assistant phase |
| Statistics / Dashboard charts | Post-MVP |
| Admin Panel | Post-MVP |
| Folder Chat / Document Chat | Chỉ Global + Workspace |
| Quên mật khẩu | Cần SMTP |
| Global Search UI | FTS internal only |
| Citation jump to page | Post-MVP (UC-CT03) |
| PPTX, XLSX, CSV, JSON, HTML | Post-MVP |

---

## 14.3 Pages (8 trang)

| # | Page | Route | UC |
|---|------|-------|-----|
| 1 | Login | `/login` | UC-A02 |
| 2 | Register | `/register` | UC-A01 |
| 3 | Workspace List | `/workspaces` | UC-W01 |
| 4 | Workspace Detail | `/workspaces/:id` | UC-W03, UC-F01, UC-K02 |
| 5 | Document Viewer | `/documents/:id` | UC-K03, UC-K04 |
| 6 | AI Chat | `/chat`, `/chat/:id` | UC-C01~C07, UC-CT01 |
| 7 | Profile | `/profile` | UC-P01, UC-P02 |
| 8 | Landing (optional) | `/` | — |

**Đã gộp / loại bỏ:** Chat History → sidebar trong Chat; Folder Detail → tab trong Workspace Detail; Document List → tab trong Workspace Detail; Dashboard → không trong MVP-8W.

---

## 14.4 API Endpoints (26)

```
# Auth — UC-A01~A04
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh

# Profile — UC-P01~P02
GET    /api/v1/users/me
PUT    /api/v1/users/me

# Workspace — UC-W01~W05
GET    /api/v1/workspaces
POST   /api/v1/workspaces
GET    /api/v1/workspaces/{id}
PUT    /api/v1/workspaces/{id}
DELETE /api/v1/workspaces/{id}

# Folder — UC-F01~F04
GET    /api/v1/workspaces/{ws_id}/folders
POST   /api/v1/workspaces/{ws_id}/folders
PUT    /api/v1/folders/{id}
DELETE /api/v1/folders/{id}

# Document — UC-K01~K05
POST   /api/v1/documents/upload
GET    /api/v1/documents
GET    /api/v1/documents/{id}
GET    /api/v1/documents/{id}/chunks
DELETE /api/v1/documents/{id}

# AI Chat — UC-C01~C07, UC-CT01~CT02
GET    /api/v1/chats
POST   /api/v1/chats
GET    /api/v1/chats/{id}
PUT    /api/v1/chats/{id}
DELETE /api/v1/chats/{id}
POST   /api/v1/chats/{id}/messages
```

---

## 14.5 Database Tables (11 bảng MVP)

```
users
user_profiles
refresh_tokens          ← P0 fix
workspaces
folders
documents
document_chunks
chats
chat_messages
citations
ai_usage_logs
```

---

## 14.6 Tech Decisions

| Decision | Choice |
|----------|--------|
| File storage | Local filesystem |
| Background processing | FastAPI BackgroundTasks |
| Search | PostgreSQL FTS (`tsvector` + GIN index) |
| AI model | Gemini 1.5 Flash |
| Auth | JWT access (24h) + refresh token (7d) |
| Frontend state | React Query |
| Deployment | Docker Compose (PostgreSQL + API + Frontend) |

---

## 14.7 Development Timeline (8 tuần)

| Tuần | Focus | Deliverables |
|------|-------|--------------|
| 1 | Setup + Auth | Monorepo, DB migration, UC-A01~A04, Login/Register |
| 2 | Profile + Layout | UC-P01~P02, App shell, protected routes |
| 3 | Workspace + Folder | UC-W01~W05, UC-F01~F04, Workspace pages |
| 4 | Document Upload | UC-K01, UC-K06, PDF/TXT/MD processors |
| 5 | DOCX + Viewer | DOCX processor, UC-K02~K04, Document Viewer |
| 6 | AI Chat Global | UC-C01~C06, UC-K07 FTS, Gemini integration |
| 7 | Workspace Chat + Citations | UC-C07, UC-CT01~CT02, citation UI |
| 8 | Polish + Demo | Logout dialog, bugs, demo script |

---

## 14.8 Success Criteria

| Criteria | Target |
|----------|--------|
| Upload PDF/DOCX/TXT/MD | Processed < 30s (5MB) |
| AI response with citations | > 90% có nguồn |
| Citation fields | source_name + page + line present |
| API response (non-AI) | < 500ms |
| Core flow end-to-end | Demo script 10 bước pass |

---

## 14.9 Demo Script

1. **Đăng ký** `demo@devhub.ai`
2. **Đăng nhập**, nhận JWT + refresh token
3. **Tạo Workspace** "ReactJS"
4. **Tạo Folder** "Hooks"
5. **Upload** `React_Hooks_Guide.pdf`
6. Chờ status `processed`
7. **Mở AI Chat**, mode Workspace "ReactJS"
8. **Hỏi:** "useState và useEffect khác nhau thế nào?"
9. **Xem citation:** `React_Hooks_Guide.pdf` — Trang 5, Dòng 120–145
10. **Đăng xuất** — popup "Bạn có chắc chắn muốn đăng xuất?"

---

## 14.10 MVP → Full Product

```
MVP-8W                          Full Product
────────────────────────────────────────────
UC-A01~A04 Email auth       →   + UC-A05~A08 OAuth, forgot password
UC-P01~P02 Profile          →   + UC-P03~P04 password, avatar
UC-W/F/K Documents          →   + more file types, tags
UC-C06/C07 Chat             →   + UC-C08~C10 folder/doc chat
UC-CT01/CT02 Citations      →   + UC-CT03 jump to source
UC-K07 FTS internal         →   + UC-S02 Global Search UI
—                           →   + Website, Notes, Bookmark
—                           →   + AI Doc, Statistics, Admin
BackgroundTasks             →   + Celery workers
```
