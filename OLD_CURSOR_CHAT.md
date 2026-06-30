Implement Workspace Module completely.

Use existing scaffold.

Requirements:

CRUD Workspace.

Endpoints:

GET /workspaces
POST /workspaces
GET /workspaces/{id}
PUT /workspaces/{id}
DELETE /workspaces/{id}

Security:

Users can only access their own workspaces.

Frontend:

Implement:

* Workspace List Page
* Create Workspace Dialog
* Edit Workspace
* Delete Workspace

Testing:

Provide API tests and UI verification steps.

Generate complete code.

CURSOR:
Module Workspace đã được triển khai đầy đủ.

Backend
backend/app/services/workspace_service.py
CRUD với kiểm tra ownership (user_id)
Validate tên (không rỗng), màu hex (#RRGGBB)
Trả 404 khi workspace không tồn tại hoặc không thuộc user
backend/app/api/v1/workspaces.py
Method	Endpoint	Status
GET
/api/v1/workspaces
Danh sách workspace của user
POST
/api/v1/workspaces
201 — tạo mới
GET
/api/v1/workspaces/{id}
Chi tiết (chỉ owner)
PUT
/api/v1/workspaces/{id}
Cập nhật (chỉ owner)
DELETE
/api/v1/workspaces/{id}
Xóa (chỉ owner)
Frontend
File	Chức năng
api/workspace.api.ts
API client CRUD
components/ui/dialog.tsx
Dialog tái sử dụng
components/workspace/WorkspaceFormDialog.tsx
Tạo / sửa workspace
components/workspace/DeleteWorkspaceDialog.tsx
Xác nhận xóa
pages/WorkspaceListPage.tsx
Grid cards + CRUD
pages/WorkspaceDetailPage.tsx
Chi tiết + sửa/xóa
UI features: tạo workspace, sửa, xóa (confirm), chọn màu preset, empty state, loading, error handling, link sang detail page.

Frontend build: thành công.

API Tests
File: backend/tests/test_workspaces.py (5 tests)

cd D:\TTICT\DevHub\backend
python -m pytest tests/test_workspaces.py -v
Test	Mô tả
test_workspace_crud_flow
Create → List → Get → Update → Delete
test_workspace_ownership_isolation
User B không get/update/delete workspace của User A
test_workspace_requires_authentication
401 khi không có token
test_create_workspace_invalid_color
422 với màu không hợp lệ
test_list_workspaces_only_returns_own
Mỗi user chỉ thấy workspace của mình
UI Verification Steps
Start stack: docker compose up --build
Đăng ký / đăng nhập → vào /workspaces
Tạo workspace: bấm "Tạo workspace" → nhập tên, mô tả, chọn màu → Lưu → card xuất hiện
Sửa: bấm "Sửa" trên card → đổi tên/màu → Lưu → UI cập nhật
Detail: click tên workspace → trang detail hiển thị đúng thông tin
Xóa: bấm "Xóa" → confirm → workspace biến mất khỏi list
Isolation: đăng nhập user khác → không thấy workspace của user 1; truy cập trực tiếp URL /workspaces/{id} → lỗi 404
Manual API curl
# Sau khi login, lấy TOKEN
curl http://localhost:8000/api/v1/workspaces -H "Authorization: Bearer TOKEN"
curl -X POST http://localhost:8000/api/v1/workspaces `
  -H "Authorization: Bearer TOKEN" `
  -H "Content-Type: application/json" `
  -d '{"name":"ReactJS","description":"React docs","color":"#3B82F6"}'
Bước tiếp theo theo roadmap MVP-8W: Folder CRUD hoặc Document Upload. Bạn muốn làm module nào tiếp?