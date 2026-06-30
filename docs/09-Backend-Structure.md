# 9. Folder Structure — Backend

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                           # FastAPI app entry + CORS + middleware
│   │
│   ├── core/                             # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py                     # Settings (Pydantic BaseSettings)
│   │   ├── security.py                   # JWT, password hashing, OAuth
│   │   ├── dependencies.py              # FastAPI dependencies (get_db, get_current_user)
│   │   └── exceptions.py                # Custom exception handlers
│   │
│   ├── db/                               # Database layer
│   │   ├── __init__.py
│   │   ├── base.py                       # SQLAlchemy Base
│   │   ├── session.py                    # Database session factory
│   │   └── init_db.py                    # Seed data, migrations helper
│   │
│   ├── models/                           # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                       # User, UserProfile
│   │   ├── workspace.py                  # Workspace
│   │   ├── folder.py                     # Folder
│   │   ├── document.py                   # Document, DocumentChunk
│   │   ├── website.py                    # Website, WebsiteContent
│   │   ├── note.py                       # Note
│   │   ├── tag.py                        # Tag, DocumentTag, NoteTag
│   │   ├── chat.py                       # Chat, ChatMessage
│   │   ├── citation.py                   # Citation
│   │   ├── flashcard.py                  # Flashcard
│   │   ├── quiz.py                       # Quiz
│   │   ├── bookmark.py                   # Bookmark
│   │   └── ai_usage.py                   # AIUsageLog
│   │
│   ├── schemas/                          # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── workspace.py
│   │   ├── folder.py
│   │   ├── document.py
│   │   ├── website.py
│   │   ├── chat.py
│   │   ├── citation.py
│   │   ├── ai.py
│   │   ├── note.py
│   │   ├── bookmark.py
│   │   ├── search.py
│   │   ├── statistics.py
│   │   ├── admin.py
│   │   └── common.py                     # Pagination, ErrorResponse
│   │
│   ├── api/                              # API routes
│   │   ├── __init__.py
│   │   ├── router.py                     # Main API router (include all v1 routes)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py                   # /auth/*
│   │       ├── users.py                  # /users/*
│   │       ├── dashboard.py              # /dashboard/*
│   │       ├── workspaces.py             # /workspaces/*
│   │       ├── folders.py                # /folders/*
│   │       ├── documents.py              # /documents/*
│   │       ├── websites.py               # /websites/*
│   │       ├── chats.py                  # /chats/*
│   │       ├── ai.py                     # /ai/*
│   │       ├── notes.py                  # /notes/*
│   │       ├── bookmarks.py              # /bookmarks/*
│   │       ├── search.py                 # /search
│   │       ├── statistics.py             # /statistics/*
│   │       ├── tags.py                   # /tags/*
│   │       └── admin.py                  # /admin/*
│   │
│   ├── services/                         # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py               # Register, login, OAuth, reset password
│   │   ├── user_service.py               # Profile CRUD
│   │   ├── workspace_service.py
│   │   ├── folder_service.py
│   │   ├── document_service.py           # Upload, CRUD, metadata
│   │   ├── website_service.py            # Crawl, CRUD
│   │   ├── chat_service.py               # Chat CRUD, message handling
│   │   ├── ai_service.py                 # Gemini integration
│   │   ├── search_service.py             # Full-text search across entities
│   │   ├── citation_service.py           # Citation extraction & mapping
│   │   ├── statistics_service.py         # Aggregation queries
│   │   ├── bookmark_service.py
│   │   ├── note_service.py
│   │   ├── tag_service.py
│   │   └── admin_service.py
│   │
│   ├── processors/                       # Document processing
│   │   ├── __init__.py
│   │   ├── base.py                       # BaseProcessor abstract class
│   │   ├── pdf_processor.py              # PyMuPDF
│   │   ├── docx_processor.py             # python-docx
│   │   ├── excel_processor.py          # openpyxl + pandas
│   │   ├── pptx_processor.py             # python-pptx
│   │   ├── text_processor.py             # TXT, MD
│   │   ├── html_processor.py             # BeautifulSoup4
│   │   ├── json_processor.py
│   │   └── markdown_converter.py         # Convert any format → Markdown
│   │
│   ├── crawlers/                         # Web crawling
│   │   ├── __init__.py
│   │   ├── web_crawler.py                # URL fetch + parse
│   │   └── content_extractor.py          # Heading/paragraph extraction
│   │
│   ├── ai/                               # AI integration
│   │   ├── __init__.py
│   │   ├── gemini_client.py              # Gemini API wrapper
│   │   ├── prompts.py                    # System prompts templates
│   │   ├── context_builder.py            # Build context from search results
│   │   └── response_parser.py            # Parse AI response + citations
│   │
│   ├── workers/                          # Background tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py                 # Celery configuration
│   │   ├── document_tasks.py             # Async document processing
│   │   └── crawl_tasks.py                # Async website crawling
│   │
│   └── utils/                            # Utilities
│       ├── __init__.py
│       ├── email.py                      # SMTP email sender
│       ├── file.py                       # File validation, storage
│       ├── chunking.py                   # Text chunking with metadata
│       └── pagination.py                 # Pagination helper
│
├── alembic/                              # Database migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│
├── uploads/                              # File storage (gitignored)
│   ├── documents/
│   └── avatars/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                       # Pytest fixtures
│   ├── test_auth.py
│   ├── test_documents.py
│   ├── test_chat.py
│   ├── test_search.py
│   └── test_ai.py
│
├── requirements.txt
├── Dockerfile
├── .env.example
└── pyproject.toml
```

## Docker Compose Structure

```
docker-compose.yml
├── services:
│   ├── frontend (nginx + react build)
│   ├── backend (fastapi + uvicorn)
│   ├── db (postgresql:16)
│   ├── redis (celery broker)
│   └── worker (celery worker)
```

## Key Design Patterns

| Pattern | Áp dụng |
|---------|---------|
| **Repository Pattern** | `services/` tách biệt business logic khỏi API routes |
| **Strategy Pattern** | `processors/` — mỗi file type có processor riêng |
| **Dependency Injection** | FastAPI `Depends()` cho DB session, current user |
| **Background Tasks** | Celery workers cho document processing & crawling |
| **Factory Pattern** | `processors/base.py` → factory chọn processor theo file type |
