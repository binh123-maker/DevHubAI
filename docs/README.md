# DevHub AI — AI Developer Knowledge Hub

> Nền tảng quản lý tri thức cá nhân kết hợp AI cho sinh viên CNTT, lập trình viên và người tự học công nghệ.

**Official implementation target:** [MVP-8W](./17-Revised-MVP-Architecture.md)

## Tài liệu thiết kế

| # | Tài liệu | File |
|---|----------|------|
| 00 | **Use Case Master** (chuẩn UC ID) | [00-Use-Case-Master.md](./00-Use-Case-Master.md) |
| 1 | Software Requirement Specification (SRS) | [01-SRS.md](./01-SRS.md) |
| 2 | Use Case Diagram | [02-Use-Case-Diagram.md](./02-Use-Case-Diagram.md) |
| 3 | Activity Diagram | [03-Activity-Diagram.md](./03-Activity-Diagram.md) |
| 4 | Sequence Diagram | [04-Sequence-Diagram.md](./04-Sequence-Diagram.md) |
| 5 | ERD Crow's Foot | [05-ERD.md](./05-ERD.md) |
| 6 | Database Schema PostgreSQL | [06-Database-Schema.sql](./06-Database-Schema.sql) |
| 7 | API Design FastAPI | [07-API-Design.md](./07-API-Design.md) |
| 8 | Folder Structure Frontend | [08-Frontend-Structure.md](./08-Frontend-Structure.md) |
| 9 | Folder Structure Backend | [09-Backend-Structure.md](./09-Backend-Structure.md) |
| 10 | UI/UX Wireframe | [10-UI-UX-Wireframe.md](./10-UI-UX-Wireframe.md) |
| 11 | System Architecture Diagram | [11-System-Architecture.md](./11-System-Architecture.md) |
| 12 | Data Flow Diagram | [12-Data-Flow-Diagram.md](./12-Data-Flow-Diagram.md) |
| 13 | Complete Development Roadmap | [13-Development-Roadmap.md](./13-Development-Roadmap.md) |
| 14 | **MVP-8W (Official Target)** | [14-MVP-Version.md](./14-MVP-Version.md) |
| 15 | Future Expansion Plan | [15-Future-Expansion.md](./15-Future-Expansion.md) |
| 16 | Architecture Review | [16-Architecture-Review.md](./16-Architecture-Review.md) |
| 17 | **Revised MVP Architecture** | [17-Revised-MVP-Architecture.md](./17-Revised-MVP-Architecture.md) |
| 18 | **Final Production Database** | [18-Final-Database.md](./18-Final-Database.md) |
| 19 | **AI Pipeline** | [19-AI-Pipeline.md](./19-AI-Pipeline.md) |

## MVP-8W at a Glance

| Metric | Value |
|--------|-------|
| Pages | **8** |
| API endpoints | **26** |
| Database tables | **11** |
| Timeline | **8 weeks** |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Vite, TailwindCSS, Shadcn UI, React Router, Axios, React Query |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic, JWT, Refresh Token |
| Database | PostgreSQL (Full-Text Search) |
| AI | Gemini API |
| Deployment | Docker, Nginx |

## Nguyên tắc thiết kế

- **Markdown-first storage** — Lưu trữ nội dung dạng Markdown thay vì Vector DB
- **Source Tracking** — Mọi câu trả lời AI đều có trích dẫn: tên file, trang, dòng
- **Workspace hierarchy** — Workspace → Folder → Documents
- **Scoped AI Chat** — Global / Workspace (MVP); Folder / Document (post-MVP)

## P0 Fixes (v1.1)

- `refresh_tokens` table + UC-A04
- `citations.note_id` + CHECK constraints
- Notes FTS trigger
- Document-folder-workspace validation triggers
- Use Case IDs chuẩn hóa across SRS, UC, API, MVP
