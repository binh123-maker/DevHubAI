# 12. Data Flow Diagram (DFD)

## 12.1 DFD Level 0 — Context Diagram

```mermaid
graph TB
    User([👤 User])
    Admin([👤 Admin])
    Google([Google OAuth])
    Facebook([Facebook OAuth])
    Gemini([Gemini API])
    SMTP([SMTP Server])

    System[DevHub AI System]

    User -->|Đăng ký, đăng nhập, upload, chat, quản lý| System
    System -->|Dashboard, câu trả lời AI, citations, tài liệu| User

    Admin -->|Quản lý user, dữ liệu| System
    System -->|Thống kê hệ thống| Admin

    System <-->|OAuth flow| Google
    System <-->|OAuth flow| Facebook
    System -->|Prompt + context| Gemini
    Gemini -->|AI response| System
    System -->|Reset password email| SMTP
```

## 12.2 DFD Level 1 — Main Processes

```mermaid
graph TB
    User([User])

    subgraph DevHub AI
        P1[1.0<br/>Authentication<br/>& Profile]
        P2[2.0<br/>Knowledge<br/>Management]
        P3[3.0<br/>AI Chat<br/>& Citation]
        P4[4.0<br/>AI Document<br/>Assistant]
        P5[5.0<br/>Search<br/>& Analytics]
        P6[6.0<br/>Admin<br/>Management]

        D1[(D1: Users<br/>& Profiles)]
        D2[(D2: Workspaces<br/>& Folders)]
        D3[(D3: Documents<br/>& Chunks)]
        D4[(D4: Websites<br/>& Contents)]
        D5[(D5: Chats<br/>Messages & Citations)]
        D6[(D6: Notes<br/>Bookmarks & Tags)]
        D7[(D7: AI Generated<br/>Flashcards & Quizzes)]
        D8[(D8: File<br/>Storage)]
    end

    Gemini([Gemini API])

    User --> P1
    P1 --> D1
  User --> P2
    P2 --> D2
    P2 --> D3
    P2 --> D4
    P2 --> D6
    P2 --> D8
    User --> P3
    P3 --> D3
    P3 --> D4
    P3 --> D5
    P3 <--> Gemini
    User --> P4
    P4 --> D3
    P4 --> D7
    P4 <--> Gemini
    User --> P5
    P5 --> D1
    P5 --> D3
    P5 --> D4
    P5 --> D5
    User --> P6
    P6 --> D1
    P6 --> D3
```

## 12.3 DFD Level 2 — AI Chat Process (3.0)

```mermaid
graph TB
    User([User])

    subgraph "3.0 AI Chat & Citation"
        P31[3.1<br/>Receive<br/>Query]
        P32[3.2<br/>Determine<br/>Scope]
        P33[3.3<br/>Search<br/>Knowledge Base]
        P34[3.4<br/>Build AI<br/>Context]
        P35[3.5<br/>Generate<br/>Response]
        P36[3.6<br/>Extract<br/>Citations]
        P37[3.7<br/>Store &<br/>Return]

        D3[(D3: Documents<br/>& Chunks)]
        D4[(D4: Websites<br/>& Contents)]
        D5[(D5: Chats<br/>& Citations)]
    end

    Gemini([Gemini API])

    User -->|câu hỏi + scope| P31
    P31 --> P32
    P32 -->|scope filter| P33
    P33 -->|FTS query| D3
    P33 -->|FTS query| D4
    D3 -->|ranked chunks| P34
    D4 -->|ranked contents| P34
    P34 -->|prompt| P35
    P35 <-->|generate| Gemini
    Gemini -->|response| P35
    P35 --> P36
    P34 -->|source metadata| P36
    P36 -->|citations| P37
    P37 -->|save| D5
    P37 -->|answer + citations| User
```

## 12.4 DFD Level 2 — Document Processing (2.0)

```mermaid
graph TB
    User([User])

    subgraph "2.0 Knowledge Management"
        P21[2.1<br/>Upload<br/>Document]
        P22[2.2<br/>Validate &<br/>Store File]
        P23[2.3<br/>Extract<br/>Content]
        P24[2.4<br/>Convert to<br/>Markdown]
        P25[2.5<br/>Create<br/>Chunks]
        P26[2.6<br/>Index for<br/>Search]

        D3[(D3: Documents<br/>& Chunks)]
        D8[(D8: File<br/>Storage)]
    end

    User -->|file + metadata| P21
    P21 --> P22
    P22 -->|save| D8
    P22 -->|metadata| D3
    P22 --> P23
    P23 -->|read| D8
    P23 --> P24
    P24 --> P25
    P25 -->|chunks| D3
    P25 --> P26
    P26 -->|FTS index| D3
    P26 -->|status: processed| User
```

## 12.5 DFD Level 2 — Website Crawling

```mermaid
graph TB
    User([User])

    subgraph "2.0 Website Collection"
        P27[2.7<br/>Submit URL]
        P28[2.8<br/>Fetch &<br/>Parse HTML]
        P29[2.9<br/>Extract<br/>Content]
        P210[2.10<br/>Convert &<br/>Store]

        D4[(D4: Websites<br/>& Contents)]
    end

    Web([Target Website])

    User -->|URL + workspace| P27
    P27 --> P28
    P28 -->|HTTP GET| Web
    Web -->|HTML| P28
    P28 --> P29
    P29 -->|headings, paragraphs| P210
    P210 -->|markdown content| D4
    P210 -->|preview| User
```

## 12.6 Data Flow — Authentication

```mermaid
sequenceDiagram
    participant U as User
    participant A as Auth Process
    participant D as D1: Users DB
    participant E as External OAuth

    U->>A: Register (email, password)
    A->>D: Check email exists
    A->>A: Hash password
    A->>D: Create user + profile
    A->>U: JWT token

    U->>A: Login (email, password)
    A->>D: Verify credentials
    A->>U: JWT token

    U->>A: Google OAuth
    A->>E: OAuth flow
    E->>A: User info
    A->>D: Create/find user
    A->>U: JWT token
```

## 12.7 Data Store Dictionary

| ID | Tên | Mô tả | Entities |
|----|-----|-------|----------|
| D1 | Users & Profiles | Thông tin tài khoản | users, user_profiles |
| D2 | Workspaces & Folders | Cấu trúc tổ chức | workspaces, folders |
| D3 | Documents & Chunks | Tài liệu và nội dung đã xử lý | documents, document_chunks |
| D4 | Websites & Contents | Website đã crawl | websites, website_contents |
| D5 | Chats & Citations | Hội thoại AI và trích dẫn | chats, chat_messages, citations |
| D6 | Notes & Bookmarks | Ghi chú và đánh dấu | notes, bookmarks, tags |
| D7 | AI Generated | Nội dung AI sinh ra | flashcards, quizzes |
| D8 | File Storage | File gốc upload | uploads/documents/, uploads/avatars/ |

## 12.8 Data Flow Summary Table

| Process | Input | Output | Data Stores |
|---------|-------|--------|-------------|
| 1.0 Auth | email, password, OAuth token | JWT, user profile | D1 |
| 2.1 Upload Doc | file, workspace_id | document metadata | D3, D8 |
| 2.3 Extract | file from storage | text content | D8 → D3 |
| 2.7 Crawl Web | URL | markdown content | D4 |
| 3.3 Search KB | query, scope | ranked chunks | D3, D4 |
| 3.5 AI Generate | prompt + context | AI response | Gemini → D5 |
| 3.6 Citation | response + chunks | citation records | D5 |
| 4.0 AI Doc Assist | document_id, action | summary/flashcard/quiz | D3 → D7 |
| 5.0 Search | query, filters | grouped results | D1-D6 |
| 6.0 Admin | admin commands | system stats | D1-D5 |
