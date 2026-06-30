# 10. UI/UX Wireframe

**Design System:** Notion + NotebookLM + ChatGPT + Perplexity  
**Theme:** Dark Mode / Light Mode  
**Framework:** TailwindCSS + Shadcn UI

---

## 10.1 Design Tokens

| Token | Light | Dark |
|-------|-------|------|
| Background | `#FFFFFF` | `#0F0F0F` |
| Surface | `#F9FAFB` | `#1A1A1A` |
| Border | `#E5E7EB` | `#2D2D2D` |
| Primary | `#3B82F6` | `#60A5FA` |
| Text Primary | `#111827` | `#F9FAFB` |
| Text Secondary | `#6B7280` | `#9CA3AF` |
| Accent | `#8B5CF6` | `#A78BFA` |
| Success | `#10B981` | `#34D399` |
| Citation BG | `#EFF6FF` | `#1E293B` |

---

## 10.2 Landing Page

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo DevHub AI]          Features  Pricing  Login  [Đăng ký]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│         Quản lý tri thức cá nhân                                │
│         kết hợp AI thông minh                                   │
│                                                                 │
│    Lưu trữ tài liệu, website, ghi chú.                         │
│    Hỏi đáp AI với trích dẫn nguồn chính xác.                   │
│                                                                 │
│         [Bắt đầu miễn phí →]    [Xem demo]                     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 📄 Upload │  │ 🌐 Website│  │ 💬 AI    │  │ 📊 Stats │       │
│  │ Tài liệu  │  │ Crawler  │  │ Chat     │  │ Dashboard│       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
├─────────────────────────────────────────────────────────────────┤
│  "Mọi câu trả lời AI đều có nguồn trích dẫn"                  │
│  [Screenshot AI Chat với Citations]                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10.3 Login Page

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    [Logo DevHub AI]                              │
│                                                                 │
│              ┌─────────────────────────┐                      │
│              │     Đăng nhập             │                      │
│              │                           │                      │
│              │  Email                    │                      │
│              │  [___________________]    │                      │
│              │                           │                      │
│              │  Mật khẩu                 │                      │
│              │  [___________________] 👁  │                      │
│              │                           │                      │
│              │  [Quên mật khẩu?]         │                      │
│              │                           │                      │
│              │  [    Đăng nhập    ]      │                      │
│              │                           │                      │
│              │  ─── hoặc ───             │                      │
│              │                           │                      │
│              │  [G Google]  [f Facebook] │                      │
│              │                           │                      │
│              │  Chưa có tài khoản?       │                      │
│              │  [Đăng ký]                │                      │
│              └─────────────────────────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10.4 Main App Layout (Dashboard / All Pages)

```
┌──────┬──────────────────────────────────────────────────────────┐
│      │  🔍 [Tìm kiếm toàn hệ thống...]     🌙  🔔  [Avatar ▼] │
│ SIDE │──────────────────────────────────────────────────────────│
│ BAR  │                                                          │
│      │                    MAIN CONTENT                          │
│ 📊   │                                                          │
│ Dash │                                                          │
│      │                                                          │
│ 📁   │                                                          │
│ Work │                                                          │
│      │                                                          │
│ 📄   │                                                          │
│ Docs │                                                          │
│      │                                                          │
│ 🌐   │                                                          │
│ Web  │                                                          │
│      │                                                          │
│ 💬   │                                                          │
│ Chat │                                                          │
│      │                                                          │
│ 📝   │                                                          │
│ Note │                                                          │
│      │                                                          │
│ ⭐   │                                                          │
│ Book │                                                          │
│      │                                                          │
│ 📈   │                                                          │
│ Stat │                                                          │
│      │                                                          │
│──────│                                                          │
│ 👤   │                                                          │
│ Prof │                                                          │
│ 🚪   │                                                          │
│ Log  │                                                          │
└──────┴──────────────────────────────────────────────────────────┘

Sidebar: 240px (collapsible → 64px icon-only)
Header: 56px fixed
```

---

## 10.5 Dashboard Page

```
┌──────────────────────────────────────────────────────────────────┐
│  Dashboard                                                       │
│                                                                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │
│  │   5    │ │  12    │ │  45    │ │   8    │ │  23    │       │
│  │Workspac│ │ Folder │ │  Docs  │ │  Web   │ │ Notes  │       │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘       │
│  ┌────────┐ ┌────────┐                                          │
│  │  15    │ │  120   │                                          │
│  │ Chats  │ │AI Query│                                          │
│  └────────┘ └────────┘                                          │
│                                                                  │
│  ┌─────────────────────────┐  ┌─────────────────────────┐       │
│  │  📊 Tài liệu theo tháng │  │  📊 Sử dụng AI          │       │
│  │  [Bar Chart]            │  │  [Line Chart]           │       │
│  │                         │  │                         │       │
│  └─────────────────────────┘  └─────────────────────────┘       │
│                                                                  │
│  ┌─────────────────────────┐  ┌─────────────────────────┐       │
│  │  📄 Tài liệu gần đây    │  │  🌐 Website gần đây     │       │
│  │  • Spring_Boot.pdf      │  │  • react.dev            │       │
│  │  • React_Guide.md       │  │  • fastapi.tiangolo.com │       │
│  │  • Python_Cheatsheet    │  │  • docs.python.org      │       │
│  └─────────────────────────┘  └─────────────────────────┘       │
└──────────────────────────────────────────────────────────────────┘
```

---

## 10.6 AI Chat Page (Core UI — Perplexity Style)

```
┌──────────────────────────────────────────────────────────────────┐
│  AI Chat Assistant                                               │
├──────────────┬───────────────────────────────────────────────────┤
│  Chat History│                                                   │
│              │  Mode: [Global ▼] [Workspace ▼] [Folder ▼]       │
│  🔍 Search   │                                                   │
│              │  ┌─────────────────────────────────────────┐     │
│  > React     │  │ 👤 useEffect hoạt động như thế nào?     │     │
│    Hooks     │  └─────────────────────────────────────────┘     │
│              │                                                   │
│    Python    │  ┌─────────────────────────────────────────┐     │
│    OOP       │  │ 🤖 useEffect là một React Hook cho      │     │
│              │  │ phép bạn đồng bộ component với hệ       │     │
│    Docker    │  │ thống bên ngoài. Nó nhận 2 tham số:    │     │
│    Setup     │  │ setup function và dependencies array.    │     │
│              │  │                                          │     │
│              │  │ 📎 Nguồn:                                │     │
│              │  │ ┌────────────────────────────────────┐  │     │
│              │  │ │ 📄 React_Documentation.md          │  │     │
│              │  │ │    Dòng 120-145  [Mở tài liệu →]  │  │     │
│              │  │ ├────────────────────────────────────┤  │     │
│              │  │ │ 🌐 react.dev                       │  │     │
│              │  │ │    useEffect reference [Mở →]      │  │     │
│              │  │ └────────────────────────────────────┘  │     │
│              │  └─────────────────────────────────────────┘     │
│              │                                                   │
│  [+ New Chat]│  ┌───────────────────────────────────┐ [Gửi ➤]  │
│              │  │ Nhập câu hỏi của bạn...           │          │
│              │  └───────────────────────────────────┘          │
└──────────────┴───────────────────────────────────────────────────┘
```

---

## 10.7 Document Viewer Page

```
┌──────────────────────────────────────────────────────────────────┐
│  ← Back    Spring_Boot_Basic.pdf    [✏️ Edit] [🤖 AI] [⭐] [🗑️] │
├────────────────────────────────────┬─────────────────────────────┤
│                                    │  AI Assistant Panel         │
│                                    │                             │
│   ┌────────────────────────┐      │  [Tóm tắt] [Flashcard]     │
│   │                        │      │  [Quiz] [Từ khóa]          │
│   │   PDF Viewer           │      │                             │
│   │                        │      │  ─────────────────          │
│   │   Page 15 / 120        │      │                             │
│   │                        │      │  📋 Tóm tắt:               │
│   │   [Highlighted text    │      │  Spring Boot là framework  │
│   │    from citation]      │      │  giúp tạo ứng dụng Java    │
│   │                        │      │  nhanh chóng với cấu hình  │
│   │                        │      │  tự động...                │
│   │                        │      │                             │
│   └────────────────────────┘      │  ─────────────────          │
│                                    │                             │
│   [◀ Prev]  Page [15] / 120 [▶]  │  🃏 Flashcards (10)        │
│                                    │  [Flip card UI]             │
└────────────────────────────────────┴─────────────────────────────┘
```

---

## 10.8 Workspace Detail Page

```
┌──────────────────────────────────────────────────────────────────┐
│  📁 Python                                    [✏️] [🗑️] [+ Folder]│
│  Tài liệu và ghi chú về Python                                   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 📁 Django    │  │ 📁 Flask     │  │ 📁 FastAPI   │          │
│  │ 5 docs       │  │ 3 docs       │  │ 8 docs       │          │
│  │ 2 websites   │  │ 1 website    │  │ 4 websites   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  Tabs: [Tài liệu] [Website] [Ghi chú]                           │
│  ─────────────────────────────────────────                       │
│  🔍 [Tìm kiếm...]  Filter: [All ▼] [Tag ▼]    [+ Upload]       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ 📄 Python_Cheatsheet.pdf    PDF   2.1MB   23/06/2025    │   │
│  │    Tags: python, cheatsheet                              │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │ 📄 Django_Tutorial.md       MD    45KB    20/06/2025    │   │
│  │    Tags: django, tutorial                                │   │
│  └────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 10.9 Logout Confirmation Dialog

```
┌─────────────────────────────────────┐
│                                     │
│   ⚠️  Đăng xuất                    │
│                                     │
│   Bạn có chắc chắn muốn đăng xuất? │
│                                     │
│        [Hủy]        [Đăng xuất]    │
│                                     │
└─────────────────────────────────────┘
```

---

## 10.10 Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 768px | Sidebar hidden (hamburger menu), stacked cards |
| Tablet | 768px - 1024px | Collapsed sidebar (icons only) |
| Desktop | > 1024px | Full sidebar + content |

---

## 10.11 Component Library Mapping (Shadcn UI)

| UI Element | Shadcn Component |
|------------|------------------|
| Buttons | `Button` |
| Forms | `Input`, `Label`, `Form` |
| Dialogs | `Dialog`, `AlertDialog` |
| Navigation | `NavigationMenu`, `Sidebar` |
| Cards | `Card` |
| Tables | `Table` |
| Tabs | `Tabs` |
| Dropdowns | `DropdownMenu`, `Select` |
| Toast | `Toast`, `Sonner` |
| Avatar | `Avatar` |
| Badge/Tags | `Badge` |
| Charts | `recharts` integration |
| Markdown | `@uiw/react-md-editor` |
