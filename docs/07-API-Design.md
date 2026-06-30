# 7. API Design — FastAPI

**Base URL:** `/api/v1`  
**Authentication:** Bearer JWT Token (`Authorization: Bearer <access_token>`)  
**Content-Type:** `application/json` (trừ upload: `multipart/form-data`)  
**Use Case registry:** [00-Use-Case-Master.md](./00-Use-Case-Master.md)  
**Official target:** MVP-8W — xem [14-MVP-Version.md](./14-MVP-Version.md)

---

## 7.0 MVP-8W API Summary (26 endpoints)

| # | Method | Endpoint | UC ID | DB Tables |
|---|--------|----------|-------|-----------|
| 1 | POST | `/auth/register` | UC-A01 | users, user_profiles |
| 2 | POST | `/auth/login` | UC-A02 | users, refresh_tokens |
| 3 | POST | `/auth/logout` | UC-A03 | refresh_tokens |
| 4 | POST | `/auth/refresh` | UC-A04 | refresh_tokens |
| 5 | GET | `/users/me` | UC-P01 | users, user_profiles |
| 6 | PUT | `/users/me` | UC-P02 | user_profiles |
| 7 | GET | `/workspaces` | UC-W01 | workspaces |
| 8 | POST | `/workspaces` | UC-W02 | workspaces |
| 9 | GET | `/workspaces/{id}` | UC-W03 | workspaces |
| 10 | PUT | `/workspaces/{id}` | UC-W04 | workspaces |
| 11 | DELETE | `/workspaces/{id}` | UC-W05 | workspaces |
| 12 | GET | `/workspaces/{ws_id}/folders` | UC-F01 | folders |
| 13 | POST | `/workspaces/{ws_id}/folders` | UC-F02 | folders |
| 14 | PUT | `/folders/{id}` | UC-F03 | folders |
| 15 | DELETE | `/folders/{id}` | UC-F04 | folders |
| 16 | POST | `/documents/upload` | UC-K01 | documents |
| 17 | GET | `/documents` | UC-K02 | documents |
| 18 | GET | `/documents/{id}` | UC-K03 | documents |
| 19 | GET | `/documents/{id}/chunks` | UC-K04 | document_chunks |
| 20 | DELETE | `/documents/{id}` | UC-K05 | documents |
| 21 | GET | `/chats` | UC-C01 | chats |
| 22 | POST | `/chats` | UC-C02 | chats |
| 23 | GET | `/chats/{id}` | UC-C03 | chats, chat_messages, citations |
| 24 | PUT | `/chats/{id}` | UC-C04 | chats |
| 25 | DELETE | `/chats/{id}` | UC-C05 | chats |
| 26 | POST | `/chats/{id}/messages` | UC-C06, UC-C07, UC-CT01~02 | chat_messages, citations, ai_usage_logs |

> **UC-K07 (FTS):** Không expose endpoint riêng — gọi nội bộ trong `POST /chats/{id}/messages`.

### POST `/chats` — MVP request body

```json
{
  "title": "Hỏi về React Hooks",
  "chat_mode": "workspace",
  "workspace_id": "uuid"
}
```

`chat_mode` MVP: `"global"` | `"workspace"` (bắt buộc `workspace_id` khi mode=workspace)

### POST `/chats/{id}/messages` — MVP citation response

```json
{
  "message": {
    "id": "uuid",
    "role": "assistant",
    "content": "...",
    "created_at": "2025-06-23T10:05:00Z"
  },
  "citations": [
    {
      "id": "uuid",
      "source_name": "React_Hooks_Guide.pdf",
      "source_type": "document",
      "page_number": 5,
      "line_start": 120,
      "line_end": 145,
      "excerpt": "useEffect is a React Hook..."
    }
  ]
}
```

---

## 7.1 Authentication APIs

| Method | Endpoint | Auth | UC | MVP | Mô tả |
|--------|----------|------|-----|-----|-------|
| POST | `/auth/register` | No | UC-A01 | ✓ | Đăng ký email |
| POST | `/auth/login` | No | UC-A02 | ✓ | Đăng nhập, trả access + refresh token |
| POST | `/auth/logout` | Yes | UC-A03 | ✓ | Revoke refresh_token |
| POST | `/auth/refresh` | No | UC-A04 | ✓ | Đổi refresh token lấy access token mới |
| POST | `/auth/forgot-password` | No | UC-A05 | Post | Gửi email reset |
| POST | `/auth/reset-password` | No | UC-A06 | Post | Reset password |
| GET | `/auth/google/login` | No | UC-A07 | Post | Redirect Google OAuth |
| GET | `/auth/google/callback` | No | UC-A07 | Post | Google OAuth callback |
| GET | `/auth/facebook/login` | No | UC-A08 | Post | Redirect Facebook OAuth |
| GET | `/auth/facebook/callback` | No | UC-A08 | Post | Facebook OAuth callback |

### POST `/auth/register`

```json
// Request
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "Nguyễn Văn A"
}

// Response 201
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Nguyễn Văn A",
    "role": "user"
  }
}
```

### POST `/auth/login`

```json
// Request
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

// Response 200
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "token_type": "bearer",
  "user": { "id": "uuid", "email": "...", "full_name": "...", "role": "user" }
}
```

### POST `/auth/logout` (UC-A03)

Revoke refresh token trong bảng `refresh_tokens`. Access token JWT hết hạn tự nhiên (stateless).

```json
// Request
{ "refresh_token": "..." }

// Response 200
{ "message": "Đăng xuất thành công" }
```

### POST `/auth/refresh` (UC-A04)

```json
// Request
{ "refresh_token": "..." }

// Response 200
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "token_type": "bearer"
}
```

---

## 7.2 User Profile APIs (MVP: UC-P01 ~ UC-P02)

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/users/me` | Yes | UC-P01 | ✓ | Lấy thông tin profile |
| PUT | `/users/me` | Yes | UC-P02 | ✓ | Cập nhật profile |
| PUT | `/users/me/password` | Yes | UC-P03 | Post | Đổi mật khẩu |
| POST | `/users/me/avatar` | Yes | UC-P04 | Post | Upload avatar |

### GET `/users/me`

```json
// Response 200
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "Nguyễn Văn A",
  "avatar_url": "/uploads/avatars/uuid.jpg",
  "gender": "male",
  "role": "user",
  "created_at": "2025-01-15T10:00:00Z"
}
```

### PUT `/users/me`

```json
// Request
{
  "full_name": "Nguyễn Văn B",
  "gender": "male"
}
```

---

## 7.3 Dashboard APIs (Post-MVP — UC-D01)

> Không nằm trong MVP-8W.

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/dashboard/stats` | Yes | Thống kê tổng quan |
| GET | `/dashboard/charts/documents` | Yes | Biểu đồ tài liệu |
| GET | `/dashboard/charts/ai-usage` | Yes | Biểu đồ AI usage |
| GET | `/dashboard/recent` | Yes | Tài liệu/website gần đây |

### GET `/dashboard/stats`

```json
// Response 200
{
  "total_workspaces": 5,
  "total_folders": 12,
  "total_documents": 45,
  "total_websites": 8,
  "total_notes": 23,
  "total_chats": 15,
  "total_ai_queries": 120
}
```

---

## 7.4 Workspace APIs (MVP: UC-W01 ~ UC-W05)

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/workspaces` | Yes | Danh sách workspace |
| POST | `/workspaces` | Yes | Tạo workspace |
| GET | `/workspaces/{id}` | Yes | Chi tiết workspace |
| PUT | `/workspaces/{id}` | Yes | Cập nhật workspace |
| DELETE | `/workspaces/{id}` | Yes | Xóa workspace |
| GET | `/workspaces/search` | Yes | Tìm kiếm workspace |

### POST `/workspaces`

```json
// Request
{
  "name": "Python",
  "description": "Tài liệu Python",
  "color": "#3776AB",
  "icon": "python"
}

// Response 201
{
  "id": "uuid",
  "name": "Python",
  "description": "Tài liệu Python",
  "color": "#3776AB",
  "icon": "python",
  "folder_count": 0,
  "document_count": 0,
  "created_at": "2025-06-23T10:00:00Z"
}
```

---

## 7.5 Folder APIs (MVP: UC-F01 ~ UC-F04)

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/workspaces/{ws_id}/folders` | Yes | Danh sách folder |
| POST | `/workspaces/{ws_id}/folders` | Yes | Tạo folder |
| GET | `/folders/{id}` | Yes | Chi tiết folder |
| PUT | `/folders/{id}` | Yes | Cập nhật folder |
| DELETE | `/folders/{id}` | Yes | Xóa folder |
| PUT | `/folders/{id}/move` | Yes | UC-F05 | Post | Di chuyển folder (cascade workspace_id) |

---

## 7.6 Document APIs (MVP: UC-K01 ~ UC-K05)

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/documents` | Yes | Danh sách tài liệu |
| POST | `/documents/upload` | Yes | Upload tài liệu |
| GET | `/documents/{id}` | Yes | Chi tiết tài liệu |
| PUT | `/documents/{id}` | Yes | Cập nhật metadata |
| DELETE | `/documents/{id}` | Yes | Xóa tài liệu |
| GET | `/documents/{id}/content` | Yes | Nội dung tài liệu |
| GET | `/documents/{id}/chunks` | Yes | Danh sách chunks |
| GET | `/documents/search` | Yes | Tìm kiếm tài liệu |
| POST | `/documents/{id}/tags` | Yes | Gắn tag |

### POST `/documents/upload`

```
Content-Type: multipart/form-data

Fields:
  file: <binary>
  workspace_id: uuid
  folder_id: uuid (optional)
  title: string (optional)
  description: string (optional)

Response 202:
{
  "id": "uuid",
  "title": "Spring_Boot_Basic.pdf",
  "status": "processing",
  "file_type": "pdf",
  "file_size": 2048576
}
```

---

## 7.7 Website APIs (Post-MVP — UC-WB01 ~ UC-WB05)

> Không nằm trong MVP-8W.

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/websites` | Yes | Danh sách website |
| POST | `/websites` | Yes | Thêm & crawl URL |
| GET | `/websites/{id}` | Yes | Chi tiết website |
| PUT | `/websites/{id}` | Yes | Cập nhật metadata |
| DELETE | `/websites/{id}` | Yes | Xóa website |
| POST | `/websites/{id}/recrawl` | Yes | Crawl lại nội dung |
| GET | `/websites/search` | Yes | Tìm kiếm website |

### POST `/websites`

```json
// Request
{
  "url": "https://react.dev",
  "workspace_id": "uuid",
  "folder_id": "uuid",
  "description": "React official docs"
}

// Response 201
{
  "id": "uuid",
  "url": "https://react.dev",
  "title": "React – The library for web and native user interfaces",
  "status": "crawled",
  "content_count": 45,
  "last_crawled_at": "2025-06-23T10:00:00Z"
}
```

---

## 7.8 AI Chat APIs (MVP: UC-C01 ~ UC-C07, UC-CT01 ~ UC-CT02)

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/chats` | Yes | Danh sách chat |
| POST | `/chats` | Yes | Tạo chat mới |
| GET | `/chats/{id}` | Yes | Chi tiết chat + messages |
| PUT | `/chats/{id}` | Yes | Đổi tên chat |
| DELETE | `/chats/{id}` | Yes | Xóa chat |
| POST | `/chats/{id}/messages` | Yes | Gửi message |
| GET | `/chats/search` | Yes | Tìm kiếm chat |

### POST `/chats`

```json
// Request
{
  "title": "Hỏi về React Hooks",
  "chat_mode": "workspace",
  "workspace_id": "uuid"
}
```

### POST `/chats/{id}/messages`

```json
// Request
{
  "content": "useEffect hoạt động như thế nào?"
}

// Response 200
{
  "message": {
    "id": "uuid",
    "role": "assistant",
    "content": "useEffect là một React Hook cho phép bạn đồng bộ component với hệ thống bên ngoài...",
    "created_at": "2025-06-23T10:05:00Z"
  },
  "citations": [
    {
      "id": "uuid",
      "source_name": "React_Documentation.md",
      "source_type": "document",
      "page_number": null,
      "line_start": 120,
      "line_end": 145,
      "url": null,
      "excerpt": "useEffect is a React Hook that lets you synchronize..."
    },
    {
      "id": "uuid",
      "source_name": "react.dev",
      "source_type": "website",
      "url": "https://react.dev/reference/react/useEffect",
      "excerpt": "useEffect is a React Hook..."
    }
  ]
}
```

---

## 7.9 AI Document Assistant APIs (Post-MVP — UC-AI01 ~ UC-AI06)

> Không nằm trong MVP-8W. Loại trừ: Flashcard, Quiz, Mindmap, Summary.

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| POST | `/ai/summarize/{doc_id}` | Yes | Tóm tắt tài liệu |
| POST | `/ai/flashcards/{doc_id}` | Yes | Sinh flashcard |
| POST | `/ai/quiz/{doc_id}` | Yes | Sinh quiz |
| POST | `/ai/keywords/{doc_id}` | Yes | Trích xuất từ khóa |
| POST | `/ai/notes/{doc_id}` | Yes | Sinh ghi chú AI |
| POST | `/ai/mindmap/{doc_id}` | Yes | Sinh mindmap |
| GET | `/ai/flashcards/{doc_id}` | Yes | Lấy flashcards đã sinh |
| GET | `/ai/quiz/{doc_id}` | Yes | Lấy quiz đã sinh |

### POST `/ai/flashcards/{doc_id}`

```json
// Request
{
  "count": 10
}

// Response 200
{
  "flashcards": [
    {
      "id": "uuid",
      "question": "useEffect nhận những tham số gì?",
      "answer": "useEffect nhận 2 tham số: setup function và dependencies array."
    }
  ]
}
```

### POST `/ai/quiz/{doc_id}`

```json
// Request
{
  "count": 5
}

// Response 200
{
  "quizzes": [
    {
      "id": "uuid",
      "question": "useEffect chạy khi nào?",
      "options": { "A": "Sau render", "B": "Trước render", "C": "Khi unmount", "D": "Không bao giờ" },
      "correct_answer": "A",
      "explanation": "useEffect chạy sau khi component render xong."
    }
  ]
}
```

---

## 7.10 Notes APIs (Post-MVP — UC-N01 ~ UC-N04)

> Không nằm trong MVP-8W.

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/notes` | Yes | Danh sách notes |
| POST | `/notes` | Yes | Tạo note |
| GET | `/notes/{id}` | Yes | Chi tiết note |
| PUT | `/notes/{id}` | Yes | Cập nhật note |
| DELETE | `/notes/{id}` | Yes | Xóa note |

---

## 7.11 Bookmark APIs (Post-MVP — UC-B01)

> Không nằm trong MVP-8W.

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/bookmarks` | Yes | Danh sách bookmarks |
| POST | `/bookmarks` | Yes | Thêm bookmark |
| DELETE | `/bookmarks/{id}` | Yes | Xóa bookmark |

---

## 7.12 Search API (Post-MVP — UC-S02)

> MVP-8W chỉ dùng FTS nội bộ (UC-K07) trong chat. Global Search UI là post-MVP.

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/search` | Yes | Tìm kiếm toàn hệ thống |

### GET `/search?q=react&type=all&page=1&limit=20`

```json
// Response 200
{
  "query": "react",
  "total": 15,
  "results": {
    "documents": [{ "id": "uuid", "title": "React Guide.pdf", "excerpt": "..." }],
    "websites": [{ "id": "uuid", "title": "react.dev", "url": "..." }],
    "notes": [{ "id": "uuid", "title": "React Hooks Notes", "excerpt": "..." }],
    "workspaces": [{ "id": "uuid", "name": "ReactJS" }],
    "chats": [{ "id": "uuid", "title": "Hỏi về React" }]
  }
}
```

---

## 7.13 Statistics APIs (Post-MVP — UC-ST01 ~ UC-ST03)

> Không nằm trong MVP-8W.

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/statistics/overview` | Yes | Thống kê tổng quan |
| GET | `/statistics/top-documents` | Yes | Top tài liệu truy cập |
| GET | `/statistics/top-websites` | Yes | Top website truy cập |
| GET | `/statistics/charts` | Yes | Dữ liệu biểu đồ |

---

## 7.14 Admin APIs (Post-MVP — UC-AD01 ~ UC-AD04)

> Không nằm trong MVP-8W.

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/admin/users` | Admin | Danh sách users |
| PUT | `/admin/users/{id}/lock` | Admin | Khóa user |
| DELETE | `/admin/users/{id}` | Admin | Xóa user |
| GET | `/admin/documents` | Admin | Quản lý tài liệu |
| GET | `/admin/websites` | Admin | Quản lý website |
| GET | `/admin/statistics` | Admin | Thống kê hệ thống |

---

## 7.15 Tags APIs (Post-MVP)

> Không nằm trong MVP-8W.

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|-------|
| GET | `/tags` | Yes | Danh sách tags |
| POST | `/tags` | Yes | Tạo tag |
| DELETE | `/tags/{id}` | Yes | Xóa tag |

---

## 7.16 Error Response Format

```json
{
  "detail": "Mô tả lỗi",
  "error_code": "EMAIL_ALREADY_EXISTS",
  "status_code": 400
}
```

| Status Code | Ý nghĩa |
|-------------|---------|
| 400 | Bad Request — validation error |
| 401 | Unauthorized — token invalid/expired |
| 403 | Forbidden — insufficient permissions |
| 404 | Not Found |
| 409 | Conflict — duplicate resource |
| 422 | Unprocessable Entity — Pydantic validation |
| 429 | Too Many Requests — rate limit |
| 500 | Internal Server Error |

---

## 7.17 Pagination Format

Tất cả list endpoints hỗ trợ:

```
?page=1&limit=20&sort=created_at&order=desc
```

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "limit": 20,
  "pages": 5
}
```
