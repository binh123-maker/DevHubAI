# 4. Sequence Diagram

## 4.1 Sequence Diagram — Đăng ký Email

```mermaid
sequenceDiagram
    actor User
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant Mail as SMTP Server

    User->>FE: Nhập email, password, họ tên
    FE->>FE: Validate form (client-side)
    FE->>API: POST /api/v1/auth/register
    API->>API: Validate input (Pydantic)
    API->>DB: SELECT user WHERE email = ?
    DB-->>API: null (not exists)
    API->>API: bcrypt.hash(password)
    API->>DB: INSERT INTO users
    API->>DB: INSERT INTO user_profiles
    DB-->>API: user_id
    API->>API: create_jwt_token(user_id)
    API-->>FE: 201 { access_token, user }
    FE->>FE: Store JWT in localStorage
    FE-->>User: Redirect to Dashboard
```

## 4.2 Sequence Diagram — Upload Document

```mermaid
sequenceDiagram
    actor User
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant Queue as Background Worker
    participant Storage as File Storage
    participant DB as PostgreSQL

    User->>FE: Chọn file + workspace/folder
    FE->>API: POST /api/v1/documents/upload (multipart)
    API->>API: Validate file type & size
    API->>Storage: Save original file
    Storage-->>API: file_path
    API->>DB: INSERT documents (status=processing)
    DB-->>API: document_id
    API->>Queue: Enqueue processing job
    API-->>FE: 202 { document_id, status: processing }
    FE-->>User: Hiển thị progress

    Queue->>Storage: Read file
    Queue->>Queue: Extract text (PyMuPDF/docx/...)
    Queue->>Queue: Convert to Markdown
    Queue->>Queue: Split into chunks (page, line)
    Queue->>DB: INSERT document_chunks (batch)
    Queue->>DB: UPDATE documents SET status=processed
    Queue-->>FE: WebSocket/Polling notification
    FE-->>User: Thông báo hoàn thành
```

## 4.3 Sequence Diagram — AI Chat với Citation (Core Flow)

```mermaid
sequenceDiagram
    actor User
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant Search as Search Service
    participant DB as PostgreSQL
    participant Gemini as Gemini API

    User->>FE: Nhập câu hỏi + chọn scope
    FE->>API: POST /api/v1/chats/{chat_id}/messages
    Note over API: scope: global|workspace|folder|document

    API->>DB: INSERT chat_messages (role=user)
    API->>Search: search_knowledge(query, scope, user_id)
    Search->>DB: SELECT ... WHERE to_tsvector(content) @@ plainto_tsquery(query)
    DB-->>Search: ranked chunks with metadata
    Search-->>API: context_chunks[]

    alt Có kết quả tìm kiếm
        API->>API: build_prompt(query, context_chunks)
        API->>Gemini: generate_content(prompt)
        Gemini-->>API: AI response text
        API->>API: map_response_to_citations(chunks)
        API->>DB: INSERT chat_messages (role=assistant)
        API->>DB: INSERT citations (batch)
        API-->>FE: 200 { message, citations[] }
        FE-->>User: Hiển thị answer + nguồn trích dẫn
    else Không có kết quả
        API->>DB: INSERT chat_messages (role=assistant, no_source)
        API-->>FE: 200 { message: "Không tìm thấy...", citations: [] }
        FE-->>User: Hiển thị thông báo
    end

    User->>FE: Click "Mở tài liệu gốc"
    FE->>API: GET /api/v1/documents/{id}?page=15
    API->>DB: SELECT document + chunk
    DB-->>API: document data
    API-->>FE: Document viewer data
    FE-->>User: Mở viewer, scroll đến page 15
```

## 4.4 Sequence Diagram — Google OAuth Login

```mermaid
sequenceDiagram
    actor User
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant Google as Google OAuth
    participant DB as PostgreSQL

    User->>FE: Click "Đăng nhập Google"
    FE->>API: GET /api/v1/auth/google/login
    API-->>FE: Redirect URL
    FE->>Google: Redirect to Google consent
    User->>Google: Authorize
    Google->>API: GET /api/v1/auth/google/callback?code=xxx
    API->>Google: Exchange code for tokens
    Google-->>API: { access_token, id_token }
    API->>Google: GET userinfo
    Google-->>API: { email, name, picture }
    API->>DB: SELECT user WHERE email = ?
    
    alt User chưa tồn tại
        API->>DB: INSERT users (oauth_provider=google)
        API->>DB: INSERT user_profiles
    end
    
    API->>API: create_jwt_token(user_id)
    API-->>FE: Redirect with token
    FE->>FE: Store JWT
    FE-->>User: Redirect Dashboard
```

## 4.5 Sequence Diagram — Crawl Website

```mermaid
sequenceDiagram
    actor User
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant Crawler as Web Crawler Service
    participant DB as PostgreSQL

    User->>FE: Nhập URL + workspace
    FE->>API: POST /api/v1/websites
    API->>API: Validate URL format
    API->>Crawler: crawl_url(url)
    Crawler->>Crawler: HTTP GET + BeautifulSoup parse
    Crawler->>Crawler: Extract headings & paragraphs
    Crawler->>Crawler: Convert to Markdown
    Crawler-->>API: { title, markdown, sections[] }
    API->>DB: INSERT websites
    API->>DB: INSERT website_contents (batch)
    API->>DB: Create FTS index
    DB-->>API: website_id
    API-->>FE: 201 { website, contents }
    FE-->>User: Hiển thị preview nội dung
```

## 4.6 Sequence Diagram — Quên mật khẩu

```mermaid
sequenceDiagram
    actor User
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant Mail as SMTP Server

    User->>FE: Nhập email
    FE->>API: POST /api/v1/auth/forgot-password
    API->>DB: SELECT user WHERE email = ?
    DB-->>API: user (or null)
    API->>API: generate_reset_token()
    API->>DB: UPDATE users SET reset_token, reset_expires
    API->>Mail: Send reset email with link
    Mail-->>User: Email với link reset
    API-->>FE: 200 { message: "Email đã gửi" }

    User->>FE: Click link trong email
    FE->>FE: Hiển thị form nhập password mới
    User->>FE: Nhập password mới
    FE->>API: POST /api/v1/auth/reset-password
    API->>DB: SELECT user WHERE reset_token = ?
    API->>API: Validate token expiry
    API->>API: bcrypt.hash(new_password)
    API->>DB: UPDATE password, clear reset_token
    API-->>FE: 200 { message: "Đổi mật khẩu thành công" }
    FE-->>User: Redirect Login
```

## 4.7 Sequence Diagram — Global Search

```mermaid
sequenceDiagram
    actor User
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant DB as PostgreSQL

    User->>FE: Nhập từ khóa vào Global Search
    FE->>API: GET /api/v1/search?q=react&type=all
    par Parallel search
        API->>DB: Search documents
        API->>DB: Search websites
        API->>DB: Search notes
        API->>DB: Search workspaces
        API->>DB: Search chats
    end
    DB-->>API: Combined results
    API->>API: Rank & group by type
    API-->>FE: 200 { results: { documents[], websites[], notes[], ... } }
    FE-->>User: Hiển thị kết quả phân loại
```
