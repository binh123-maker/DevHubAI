# 13. Complete Development Roadmap

> **Official MVP target:** [MVP-8W — 8 tuần](./14-MVP-Version.md) | [Revised Architecture](./17-Revised-MVP-Architecture.md)  
> Roadmap dưới đây mô tả **full product (20 tuần)**. Triển khai sinh viên năm 3: **chỉ làm MVP-8W trước**.

## Tổng quan

| Phase | Tên | Thời gian | Modules |
|-------|-----|-----------|---------|
| **MVP-8W** | **Official Target** | **8 tuần** | Auth, Profile, WS, Folder, Doc, Chat, Citation |
| Phase 2 | Knowledge Expansion | 4 tuần | Website, Notes, Search |
| Phase 3 | AI Features | 3 tuần | Summary, Flashcard, Quiz |
| Phase 4 | Analytics & Admin | 3 tuần | Dashboard, Statistics, Admin |
| Phase 5 | Polish & Deploy | 2 tuần | Production deploy |
| **Full Total** | | **~20 tuần** (post-MVP) | |

---

## Phase 0: Setup & Foundation (Tuần 1-2)

### Tuần 1: Project Setup

| Task | Mô tả | Output |
|------|-------|--------|
| Init monorepo | Tạo cấu trúc frontend + backend | Git repo, folder structure |
| Frontend scaffold | Vite + React + TailwindCSS + Shadcn | Running dev server |
| Backend scaffold | FastAPI + SQLAlchemy + Alembic | Running API server |
| Docker setup | docker-compose (PG, Redis, API) | `docker-compose up` works |
| CI/CD basic | GitHub Actions lint + test | Pipeline green |
| DB migration | Chạy schema từ `06-Database-Schema.sql` | Tables created |

### Tuần 2: Core Infrastructure

| Task | Mô tả | Output |
|------|-------|--------|
| Auth backend | Register, Login, JWT | `/auth/*` endpoints |
| Auth frontend | Login, Register pages | Working auth flow |
| Layout system | Sidebar, Header, Theme toggle | App shell ready |
| API client | Axios + interceptors + React Query | API layer ready |
| Error handling | Global error boundary + toast | UX error handling |
| Protected routes | Auth guard + redirect | Route protection |

**Milestone 0:** User có thể đăng ký, đăng nhập, thấy layout chính.

---

## Phase 1: MVP Core (Tuần 3-8)

### Tuần 3: User Profile & Workspace

| Task | Mô tả |
|------|-------|
| Profile CRUD | Avatar upload, update info, change password |
| Profile page UI | Form cập nhật, avatar preview |
| Workspace CRUD | Backend + Frontend |
| Workspace List page | Card grid, search, create dialog |
| Workspace Detail page | Folder list, tabs |

### Tuần 4: Folder & Document Upload

| Task | Mô tả |
|------|-------|
| Folder CRUD | Backend + Frontend |
| Document upload API | Multipart upload, validation |
| File storage | Local storage với path management |
| Document List page | Table view, filters, tags |
| Upload UI | Drag & drop, progress bar |

### Tuần 5: Document Processing

| Task | Mô tả |
|------|-------|
| PDF processor | PyMuPDF extraction |
| DOCX processor | python-docx extraction |
| TXT/MD processor | Direct read |
| Markdown converter | Unified markdown output |
| Text chunker | Split with page/line metadata |
| Celery worker setup | Background processing queue |
| FTS index | PostgreSQL tsvector triggers |

### Tuần 6: Document Viewer & Management

| Task | Mô tả |
|------|-------|
| Document metadata CRUD | Rename, description, tags |
| Document Viewer page | PDF viewer, MD renderer |
| Tag system | Create, assign, filter by tag |
| Document search | Full-text search API |

### Tuần 7-8: AI Chat (Core Feature)

| Task | Mô tả |
|------|-------|
| Gemini client | API wrapper, error handling |
| Search service | FTS across chunks + website contents |
| Context builder | Build prompt with source metadata |
| Chat CRUD | Create, list, rename, delete chats |
| Chat message flow | Send message → search → AI → response |
| Citation system | Extract, store, display citations |
| Chat UI | Perplexity-style chat interface |
| Chat mode selector | Global / Workspace / Folder / Document |

**Milestone 1 (MVP):** User upload tài liệu, chat AI với citations.

---

## Phase 2: Knowledge Expansion (Tuần 9-12)

### Tuần 9: Website Collector

| Task | Mô tả |
|------|-------|
| Web crawler | BeautifulSoup fetch + parse |
| Content extractor | Headings, paragraphs → Markdown |
| Website CRUD API | Add, list, delete, recrawl |
| Website page UI | URL input, content preview |
| Website search | FTS on website_contents |

### Tuần 10: Notes & Bookmark

| Task | Mô tả |
|------|-------|
| Notes CRUD | Markdown editor (MD editor component) |
| Note linking | Link to workspace, folder, document |
| Bookmark system | Polymorphic bookmark API |
| Bookmark page | List bookmarked items |
| Auto-save notes | Debounced save every 30s |

### Tuần 11: Global Search

| Task | Mô tả |
|------|-------|
| Unified search API | Cross-entity search |
| Search result grouping | Group by type |
| Global search UI | Header search bar + results dropdown |
| Search page | Full results with filters |

### Tuần 12: Citation Enhancement

| Task | Mô tả |
|------|-------|
| "Open source" feature | Jump to page/line in document viewer |
| PDF page navigation | Auto-scroll to cited page |
| Citation card UI | Clickable source cards |
| Citation in chat history | Persist citations in history |

**Milestone 2:** Full knowledge management + search + citation navigation.

---

## Phase 3: AI Features (Tuần 13-15)

### Tuần 13: AI Document Summary & Keywords

| Task | Mô tả |
|------|-------|
| Summary API | Gemini summarize document |
| Summary UI panel | Side panel in document viewer |
| Keyword extraction | AI extract + display as tags |
| AI Notes generation | Generate study notes from document |

### Tuần 14: Flashcard & Quiz

| Task | Mô tả |
|------|-------|
| Flashcard generation API | AI generate Q&A pairs |
| Flashcard UI | Flip card deck interface |
| Quiz generation API | AI generate multiple choice |
| Quiz UI | Interactive quiz with scoring |
| Save & retrieve | Store in DB, reload later |

### Tuần 15: Mindmap (Optional)

| Task | Mô tả |
|------|-------|
| Mindmap generation | AI generate tree structure |
| Mindmap viewer | Tree/graph visualization |
| Export mindmap | PNG/SVG export |

**Milestone 3:** Full AI document assistant features.

---

## Phase 4: Analytics & Admin (Tuần 16-18)

### Tuần 16: Dashboard & Statistics

| Task | Mô tả |
|------|-------|
| Dashboard stats API | Aggregation queries |
| Stats cards UI | Count widgets |
| Chart components | Line, Bar, Pie charts (recharts) |
| Recent items widget | Latest documents, websites |
| Statistics page | Detailed analytics |

### Tuần 17: OAuth & Password Reset

| Task | Mô tả |
|------|-------|
| Google OAuth | Full flow backend + frontend |
| Facebook OAuth | Full flow backend + frontend |
| Forgot password | Email reset flow |
| Logout confirmation | Popup dialog |

### Tuần 18: Admin Panel

| Task | Mô tả |
|------|-------|
| Admin middleware | Role-based access control |
| User management | List, lock, delete users |
| Data management | View all documents/websites |
| System statistics | Total users, data, AI queries |
| Admin dashboard UI | Admin-specific layout |

**Milestone 4:** Complete analytics + admin + OAuth.

---

## Phase 5: Polish & Deploy (Tuần 19-20)

### Tuần 19: UI/UX Polish

| Task | Mô tả |
|------|-------|
| Dark mode refinement | Theme consistency check |
| Responsive testing | Mobile, tablet layouts |
| Loading states | Skeleton loaders everywhere |
| Empty states | Friendly empty state illustrations |
| Animation | Smooth transitions |
| Accessibility | ARIA labels, keyboard navigation |

### Tuần 20: Testing & Deployment

| Task | Mô tả |
|------|-------|
| Backend tests | pytest coverage > 70% |
| Frontend tests | Key flow E2E tests |
| Docker production | Multi-stage builds, nginx config |
| Environment config | .env production setup |
| SSL setup | Let's Encrypt / cert config |
| Documentation | API docs (Swagger), README |
| Performance test | Load test critical endpoints |

**Milestone 5 (Release):** Production-ready deployment.

---

## Gantt Chart Overview

```
Tuần:  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20
       ├──┤
       P0 Setup
          ├──────────────┤
          P1 MVP Core
                         ├──────────────┤
                         P2 Knowledge
                                        ├─────────┤
                                        P3 AI Features
                                                  ├─────────┤
                                                  P4 Analytics
                                                            ├──┤
                                                            P5 Deploy
       ▲              ▲                    ▲              ▲    ▲
       M0             M1                   M2             M4   M5
```

## Team Allocation (Đề xuất)

| Role | Số người | Phases chính |
|------|----------|--------------|
| Backend Developer | 2 | P0-P5 |
| Frontend Developer | 2 | P0-P5 |
| UI/UX Designer | 1 | P0, P5 |
| DevOps | 1 (part-time) | P0, P5 |
| QA | 1 (part-time) | P1, P3, P5 |

## Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Gemini API rate limits | High | Implement caching, queue, fallback messages |
| Large file processing slow | Medium | Background workers, progress feedback |
| FTS search quality | High | Tune tsvector config, add trigram index |
| OAuth integration complexity | Medium | Start with Google only, add Facebook later |
| Citation accuracy | High | Strict prompt engineering, source metadata validation |
