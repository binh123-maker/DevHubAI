# 11. System Architecture Diagram

## 11.1 High-Level Architecture

```mermaid
graph TB
    subgraph Client Layer
        Browser[React SPA<br/>Vite + TailwindCSS + Shadcn]
    end

    subgraph Gateway Layer
        Nginx[Nginx Reverse Proxy<br/>SSL Termination<br/>Static Files]
    end

    subgraph Application Layer
        API[FastAPI Backend<br/>Uvicorn ASGI]
        Worker[Celery Worker<br/>Background Tasks]
    end

    subgraph Data Layer
        PG[(PostgreSQL 16<br/>Full-Text Search<br/>tsvector)]
        Redis[(Redis<br/>Cache + Queue)]
        FS[File Storage<br/>uploads/]
    end

    subgraph External Services
        Gemini[Google Gemini API]
        Google[Google OAuth]
        Facebook[Facebook OAuth]
        SMTP[SMTP Email Server]
    end

    Browser -->|HTTPS| Nginx
    Nginx -->|/api/*| API
    Nginx -->|/*| Browser
    API --> PG
    API --> Redis
    API --> FS
    API --> Gemini
    API --> Google
    API --> Facebook
    API --> SMTP
    Worker --> PG
    Worker --> FS
    Worker --> Redis
    Redis -->|task queue| Worker
```

## 11.2 Backend Architecture (Layered)

```mermaid
graph TB
    subgraph API Layer
        Routes[FastAPI Routes<br/>/api/v1/*]
        Middleware[Middleware<br/>CORS, Auth, Rate Limit]
        Deps[Dependencies<br/>get_db, get_current_user]
    end

    subgraph Service Layer
        AuthSvc[Auth Service]
        DocSvc[Document Service]
        ChatSvc[Chat Service]
        AISvc[AI Service]
        SearchSvc[Search Service]
        CrawlSvc[Crawl Service]
        CiteSvc[Citation Service]
    end

    subgraph Processing Layer
        Processors[Document Processors<br/>PDF, DOCX, XLSX...]
        Crawler[Web Crawler<br/>BeautifulSoup]
        Chunker[Text Chunker<br/>page/line metadata]
        MDConverter[Markdown Converter]
    end

    subgraph AI Layer
        GeminiClient[Gemini Client]
        PromptBuilder[Prompt Builder]
        ContextBuilder[Context Builder]
        CitationMapper[Citation Mapper]
    end

    subgraph Data Layer
        Models[SQLAlchemy Models]
        DB[(PostgreSQL)]
    end

    Routes --> Middleware --> Deps
    Deps --> AuthSvc & DocSvc & ChatSvc & AISvc & SearchSvc
    DocSvc --> Processors --> Chunker --> MDConverter
    DocSvc --> Models --> DB
    ChatSvc --> SearchSvc --> DB
    ChatSvc --> AISvc --> GeminiClient
    AISvc --> PromptBuilder --> ContextBuilder
    AISvc --> CitationMapper
    CrawlSvc --> Crawler --> MDConverter
```

## 11.3 AI Chat Architecture (Core)

```mermaid
graph LR
    subgraph Input
        Query[User Query]
        Scope[Chat Scope<br/>global/workspace/folder/doc]
    end

    subgraph Retrieval
        FTS[PostgreSQL<br/>Full-Text Search]
        Rank[Relevance Ranking]
        Chunks[Top-K Chunks<br/>with metadata]
    end

    subgraph Generation
        Prompt[System Prompt +<br/>Context + Query]
        Gemini[Gemini API]
        Response[AI Response]
    end

    subgraph Citation
        Map[Map chunks → citations]
        Store[Store citations<br/>in DB]
        Display[Display with<br/>source links]
    end

    Query --> FTS
    Scope --> FTS
    FTS --> Rank --> Chunks
    Chunks --> Prompt
    Query --> Prompt
    Prompt --> Gemini --> Response
    Chunks --> Map
    Response --> Map --> Store --> Display
```

## 11.4 Document Processing Pipeline

```mermaid
graph LR
    Upload[File Upload] --> Validate[Validate<br/>type & size]
    Validate --> Store[Save to<br/>File Storage]
    Store --> Queue[Celery Queue]
    Queue --> Detect[Detect<br/>File Type]
    
    Detect --> PDF[PyMuPDF]
    Detect --> DOCX[python-docx]
    Detect --> XLSX[pandas/openpyxl]
    Detect --> TXT[Text Reader]
    Detect --> HTML[BeautifulSoup]
    
    PDF & DOCX & XLSX & TXT & HTML --> MD[Convert to<br/>Markdown]
    MD --> Split[Split into Chunks<br/>page, line metadata]
    Split --> Index[Create FTS Index<br/>tsvector]
    Index --> Done[Status: processed]
```

## 11.5 Deployment Architecture (Docker)

```mermaid
graph TB
    subgraph Docker Host
        subgraph docker-compose
            NginxC[Nginx Container<br/>:80, :443]
            FEC[Frontend Container<br/>React Build]
            BEC[Backend Container<br/>FastAPI :8000]
            WKC[Worker Container<br/>Celery]
            DBC[PostgreSQL Container<br/>:5432]
            RDC[Redis Container<br/>:6379]
        end
    end

    Internet((Internet)) --> NginxC
    NginxC -->|/api| BEC
    NginxC -->|/| FEC
    BEC --> DBC
    BEC --> RDC
    WKC --> DBC
    WKC --> RDC
    BEC --> Volume[Docker Volume<br/>uploads/]
    WKC --> Volume
    DBC --> DBVol[Docker Volume<br/>pgdata/]
```

## 11.6 Security Architecture

```mermaid
graph TB
    Request[HTTP Request] --> Nginx[Nginx<br/>SSL/TLS]
    Nginx --> RateLimit[Rate Limiter<br/>100 req/min]
    RateLimit --> JWT[JWT Validation]
    JWT --> RBAC{Role Check}
    RBAC -->|user| UserAPI[User APIs<br/>own data only]
    RBAC -->|admin| AdminAPI[Admin APIs<br/>all data]
    UserAPI --> InputVal[Input Validation<br/>Pydantic]
    AdminAPI --> InputVal
    InputVal --> SQLSafe[SQLAlchemy ORM<br/>parameterized queries]
    SQLSafe --> Response[Response]
```

## 11.7 Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | React | 18+ | UI framework |
| Build | Vite | 5+ | Fast dev build |
| Styling | TailwindCSS | 3+ | Utility CSS |
| UI Components | Shadcn UI | latest | Component library |
| State | React Query + Zustand | latest | Server + client state |
| Routing | React Router | 6+ | SPA routing |
| HTTP | Axios | latest | API client |
| Backend | FastAPI | 0.100+ | Async API framework |
| ORM | SQLAlchemy | 2.0+ | Database ORM |
| Validation | Pydantic | 2.0+ | Schema validation |
| Auth | python-jose + passlib | latest | JWT + bcrypt |
| Database | PostgreSQL | 16 | Primary database |
| Queue | Celery + Redis | latest | Background tasks |
| AI | google-generativeai | latest | Gemini API |
| PDF | PyMuPDF (fitz) | latest | PDF extraction |
| DOCX | python-docx | latest | Word extraction |
| Web | BeautifulSoup4 | latest | HTML parsing |
| Proxy | Nginx | latest | Reverse proxy |
| Container | Docker + Compose | latest | Deployment |
