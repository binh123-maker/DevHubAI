# Use Case Master Registry

**Version:** 1.1 — Chuẩn hóa P0 (đồng bộ SRS, UC Diagram, API, MVP)
 

## MVP-8W Use Cases (Official Implementation Target)

### Authentication

| UC ID | Tên | Actor | SRS | MVP API |
|-------|-----|-------|-----|---------|
| UC-A01 | Đăng ký Email | Guest | FR-01.1~01.3 | `POST /auth/register` |
| UC-A02 | Đăng nhập Email | Guest, User | FR-01.6 | `POST /auth/login` |
| UC-A03 | Đăng xuất | User | FR-01.7 | `POST /auth/logout` |
| UC-A04 | Refresh Token | User | NFR-02.1 | `POST /auth/refresh` |

### Profile

| UC ID | Tên | Actor | SRS | MVP API |
|-------|-----|-------|-----|---------|
| UC-P01 | Xem hồ sơ | User | FR-02.1 | `GET /users/me` |
| UC-P02 | Cập nhật hồ sơ | User | FR-02.2 | `PUT /users/me` |

### Knowledge Management — Workspace

| UC ID | Tên | Actor | SRS | MVP API |
|-------|-----|-------|-----|---------|
| UC-W01 | Danh sách Workspace | User | FR-04 | `GET /workspaces` |
| UC-W02 | Tạo Workspace | User | FR-04.1 | `POST /workspaces` |
| UC-W03 | Xem Workspace | User | FR-04 | `GET /workspaces/{id}` |
| UC-W04 | Cập nhật Workspace | User | FR-04.1 | `PUT /workspaces/{id}` |
| UC-W05 | Xóa Workspace | User | FR-04.1 | `DELETE /workspaces/{id}` |

### Knowledge Management — Folder

| UC ID | Tên | Actor | SRS | MVP API |
|-------|-----|-------|-----|---------|
| UC-F01 | Danh sách Folder | User | FR-05.1 | `GET /workspaces/{ws_id}/folders` |
| UC-F02 | Tạo Folder | User | FR-05.1 | `POST /workspaces/{ws_id}/folders` |
| UC-F03 | Cập nhật Folder | User | FR-05.1 | `PUT /folders/{id}` |
| UC-F04 | Xóa Folder | User | FR-05.1 | `DELETE /folders/{id}` |

### Knowledge Management — Document

| UC ID | Tên | Actor | SRS | MVP API |
|-------|-----|-------|-----|---------|
| UC-K01 | Upload tài liệu | User | FR-06.1 | `POST /documents/upload` |
| UC-K02 | Danh sách tài liệu | User | FR-06 | `GET /documents` |
| UC-K03 | Xem tài liệu | User | FR-06 | `GET /documents/{id}` |
| UC-K04 | Xem nội dung chunks | User | FR-06.2 | `GET /documents/{id}/chunks` |
| UC-K05 | Xóa tài liệu | User | FR-06.3 | `DELETE /documents/{id}` |
| UC-K06 | Trích xuất & chunk | System | FR-06.2 | (background) |
| UC-K07 | Tìm kiếm FTS | System | FR-06.5 | (internal / chat) |

### AI Chat

| UC ID | Tên | Actor | SRS | MVP API |
|-------|-----|-------|-----|---------|
| UC-C01 | Danh sách chat | User | FR-08.7 | `GET /chats` |
| UC-C02 | Tạo chat | User | FR-08.1 | `POST /chats` |
| UC-C03 | Xem lịch sử chat | User | FR-08.7 | `GET /chats/{id}` |
| UC-C04 | Đổi tên chat | User | FR-08.6 | `PUT /chats/{id}` |
| UC-C05 | Xóa chat | User | FR-08.6 | `DELETE /chats/{id}` |
| UC-C06 | Global Chat | User | FR-08.2 | `POST /chats/{id}/messages` |
| UC-C07 | Workspace Chat | User | FR-08.3 | `POST /chats/{id}/messages` |

### Citation

| UC ID | Tên | Actor | SRS | MVP API |
|-------|-----|-------|-----|---------|
| UC-CT01 | Hiển thị trích dẫn | User | FR-09.1~09.2 | (response của UC-C06/07) |
| UC-CT02 | Lưu trích dẫn | System | FR-09.4 | (insert `citations`) |

**Citation MVP bắt buộc hiển thị:** `source_name` (tên file), `page_number`, `line_start` / `line_end`

---

## Post-MVP Use Cases (Full Product — tham chiếu)

| UC ID | Tên | Module | SRS |
|-------|-----|--------|-----|
| UC-A05 | Quên mật khẩu | Auth | FR-01.8 |
| UC-A06 | Reset mật khẩu | Auth | FR-01.9 |
| UC-A07 | Đăng nhập Google | Auth | FR-01.4 |
| UC-A08 | Đăng nhập Facebook | Auth | FR-01.5 |
| UC-P03 | Đổi mật khẩu | Profile | FR-02.3 |
| UC-P04 | Upload Avatar | Profile | FR-02.4 |
| UC-D01 | Dashboard thống kê | Dashboard | FR-03 |
| UC-F05 | Di chuyển Folder | Folder | FR-05.2 |
| UC-C08 | Folder Chat | AI Chat | FR-08.4 |
| UC-C09 | Document Chat | AI Chat | FR-08.5 |
| UC-C10 | Tìm kiếm chat | AI Chat | FR-08.8 |
| UC-CT03 | Mở tài liệu gốc | Citation | FR-09.3 |
| UC-WB01~05 | Website Collector | Website | FR-07 |
| UC-N01~04 | Notes | Notes | FR-11 |
| UC-B01 | Bookmark | Bookmark | FR-12 |
| UC-S02 | Global Search | Search | FR-13 |
| UC-ST01~03 | Statistics | Statistics | FR-14 |
| UC-AI01~06 | AI Doc Assistant | AI Doc | FR-10 |
| UC-AD01~04 | Admin Panel | Admin | FR-15 |

---

## Include / Extend (MVP)

```
UC-K01 Upload ──include──> UC-K06 Trích xuất & chunk
UC-K06 ──include──> UC-K07 FTS index
UC-C06 Global Chat ──include──> UC-K07 FTS Search
UC-C06 ──include──> UC-CT01 Hiển thị trích dẫn
UC-C06 ──include──> UC-CT02 Lưu trích dẫn
UC-C07 Workspace Chat ──include──> UC-K07, UC-CT01, UC-CT02
UC-A03 Logout ──extend──> UC-A02 Login (quay lại sau logout)
```
