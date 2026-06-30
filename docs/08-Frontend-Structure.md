# 8. Folder Structure — Frontend

> **Official target:** MVP-8W — [14-MVP-Version.md](./14-MVP-Version.md)

## MVP-8W Route Map (8 pages)

| Route | Page | UC |
|-------|------|-----|
| `/login` | LoginPage | UC-A02 |
| `/register` | RegisterPage | UC-A01 |
| `/workspaces` | WorkspaceListPage | UC-W01 |
| `/workspaces/:id` | WorkspaceDetailPage | UC-W03, UC-F01, UC-K02 |
| `/documents/:id` | DocumentViewerPage | UC-K03, UC-K04 |
| `/chat`, `/chat/:id` | ChatPage | UC-C01~C07 |
| `/profile` | ProfilePage | UC-P01, UC-P02 |
| `/` | LandingPage (optional) | — |

**MVP Sidebar:** Workspaces, Chat, Profile, Logout  
**Loại bỏ khỏi MVP:** Dashboard, Websites, Notes, Bookmarks, Statistics, Admin, Global Search

---

## Full Product Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   └── logo.svg
│
├── src/
│   ├── main.tsx                          # Entry point
│   ├── App.tsx                           # Root component + Router
│   ├── vite-env.d.ts
│   │
│   ├── api/                              # API layer
│   │   ├── axios.ts                      # Axios instance + interceptors
│   │   ├── auth.api.ts
│   │   ├── user.api.ts
│   │   ├── workspace.api.ts
│   │   ├── folder.api.ts
│   │   ├── document.api.ts
│   │   ├── website.api.ts
│   │   ├── chat.api.ts
│   │   ├── ai.api.ts
│   │   ├── note.api.ts
│   │   ├── bookmark.api.ts
│   │   ├── search.api.ts
│   │   ├── statistics.api.ts
│   │   └── admin.api.ts
│   │
│   ├── components/                       # Shared components
│   │   ├── ui/                           # Shadcn UI components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── card.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── toast.tsx
│   │   │   ├── avatar.tsx
│   │   │   ├── skeleton.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx             # Main layout (sidebar + content)
│   │   │   ├── Sidebar.tsx               # Navigation sidebar
│   │   │   ├── Header.tsx                # Top bar + global search
│   │   │   ├── AuthLayout.tsx            # Layout cho login/register
│   │   │   └── AdminLayout.tsx           # Admin layout
│   │   │
│   │   ├── common/
│   │   │   ├── GlobalSearch.tsx          # Global search bar
│   │   │   ├── ThemeToggle.tsx           # Dark/Light mode toggle
│   │   │   ├── ConfirmDialog.tsx         # Popup xác nhận (logout, delete)
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── Pagination.tsx
│   │   │   ├── FileUpload.tsx            # Drag & drop upload
│   │   │   └── TagInput.tsx              # Tag selector
│   │   │
│   │   ├── chat/
│   │   │   ├── ChatWindow.tsx            # Main chat interface
│   │   │   ├── ChatMessage.tsx           # Single message bubble
│   │   │   ├── ChatInput.tsx             # Message input
│   │   │   ├── ChatSidebar.tsx           # Chat history list
│   │   │   ├── CitationList.tsx          # Citation display
│   │   │   ├── CitationCard.tsx          # Single citation card
│   │   │   └── ChatModeSelector.tsx      # Global/WS/Folder/Doc selector
│   │   │
│   │   ├── document/
│   │   │   ├── DocumentViewer.tsx        # PDF/MD viewer
│   │   │   ├── DocumentCard.tsx
│   │   │   ├── DocumentList.tsx
│   │   │   ├── DocumentUpload.tsx
│   │   │   └── PdfViewer.tsx             # PDF with page jump
│   │   │
│   │   ├── ai/
│   │   │   ├── SummaryPanel.tsx
│   │   │   ├── FlashcardDeck.tsx         # Flip card UI
│   │   │   ├── QuizPanel.tsx
│   │   │   ├── KeywordTags.tsx
│   │   │   └── MindmapViewer.tsx
│   │   │
│   │   ├── editor/
│   │   │   ├── MarkdownEditor.tsx        # Note markdown editor
│   │   │   └── MarkdownPreview.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   ├── StatsCard.tsx
│   │   │   ├── DocumentChart.tsx
│   │   │   ├── AIUsageChart.tsx
│   │   │   └── RecentItems.tsx
│   │   │
│   │   └── charts/
│   │       ├── LineChart.tsx
│   │       ├── BarChart.tsx
│   │       └── PieChart.tsx
│   │
│   ├── pages/                            # Route pages
│   │   ├── public/
│   │   │   ├── LandingPage.tsx           # 1. Landing Page
│   │   │   ├── LoginPage.tsx             # 2. Login
│   │   │   ├── RegisterPage.tsx          # 3. Register
│   │   │   └── ForgotPasswordPage.tsx    # 4. Forgot Password
│   │   │
│   │   ├── user/
│   │   │   ├── DashboardPage.tsx         # 5. Dashboard
│   │   │   ├── WorkspaceListPage.tsx     # 6. Workspace List
│   │   │   ├── WorkspaceDetailPage.tsx   # 7. Workspace Detail
│   │   │   ├── FolderDetailPage.tsx      # 8. Folder Detail
│   │   │   ├── DocumentListPage.tsx      # 9. Document List
│   │   │   ├── DocumentViewerPage.tsx    # 10. Document Viewer
│   │   │   ├── WebsitePage.tsx           # 11. Website Knowledge
│   │   │   ├── ChatPage.tsx              # 12. AI Chat
│   │   │   ├── ChatHistoryPage.tsx       # 13. Chat History
│   │   │   ├── NotesPage.tsx             # 14. Notes
│   │   │   ├── BookmarkPage.tsx          # 15. Bookmark
│   │   │   ├── StatisticsPage.tsx        # 16. Statistics
│   │   │   └── ProfilePage.tsx           # 17. Profile
│   │   │
│   │   └── admin/
│   │       ├── AdminDashboardPage.tsx    # 18. Admin Dashboard
│   │       ├── UserManagementPage.tsx    # 19. User Management
│   │       ├── DataManagementPage.tsx    # 20. Data Management
│   │       └── SystemStatsPage.tsx       # 21. System Statistics
│   │
│   ├── hooks/                            # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useTheme.ts
│   │   ├── useDebounce.ts
│   │   ├── useChat.ts
│   │   ├── useDocument.ts
│   │   └── useSearch.ts
│   │
│   ├── stores/                           # State management
│   │   ├── authStore.ts                  # Zustand auth store
│   │   └── themeStore.ts
│   │
│   ├── types/                            # TypeScript types
│   │   ├── auth.types.ts
│   │   ├── user.types.ts
│   │   ├── workspace.types.ts
│   │   ├── document.types.ts
│   │   ├── website.types.ts
│   │   ├── chat.types.ts
│   │   ├── citation.types.ts
│   │   ├── note.types.ts
│   │   └── api.types.ts
│   │
│   ├── utils/                            # Utility functions
│   │   ├── format.ts                     # Date, file size formatting
│   │   ├── validation.ts
│   │   ├── constants.ts
│   │   └── cn.ts                         # Tailwind class merge
│   │
│   ├── routes/
│   │   ├── index.tsx                     # Route definitions
│   │   ├── ProtectedRoute.tsx            # Auth guard
│   │   └── AdminRoute.tsx                # Admin guard
│   │
│   └── styles/
│       ├── globals.css                   # Tailwind imports + custom CSS
│       └── themes.css                    # Dark/Light theme variables
│
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── components.json                       # Shadcn config
├── .env.example
└── Dockerfile
```

## Full Product Route Map (Post-MVP)

> MVP-8W dùng route map ở đầu tài liệu.
