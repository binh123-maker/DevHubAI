# 5. ERD — Crow's Foot Notation

## 5.1 ERD Diagram tổng quan

```mermaid
erDiagram
    users ||--o| user_profiles : has
    users ||--o{ refresh_tokens : has
    users ||--o{ workspaces : owns
    users ||--o{ bookmarks : creates
    users ||--o{ chats : creates

    workspaces ||--o{ folders : contains
    workspaces ||--o{ documents : contains
    workspaces ||--o{ websites : contains
    workspaces ||--o{ notes : contains

    folders ||--o{ documents : contains
    folders ||--o{ websites : contains
    folders ||--o{ notes : contains
    folders }o--o| folders : parent_of

    documents ||--o{ document_chunks : split_into
    documents }o--o{ tags : tagged_with
    documents ||--o{ flashcards : generates
    documents ||--o{ quizzes : generates

    websites ||--o{ website_contents : has

    chats ||--o{ chat_messages : contains
    chat_messages ||--o{ citations : references

    citations }o--o| documents : cites_document
    citations }o--o| document_chunks : cites_chunk
    citations }o--o| websites : cites_website
    citations }o--o| website_contents : cites_content
    citations }o--o| notes : cites_note

    notes }o--o| documents : linked_to
    notes }o--o{ tags : tagged_with

    users {
        uuid id PK
        varchar email UK
        varchar password_hash
        varchar oauth_provider
        varchar oauth_id
        varchar role
        boolean is_active
        varchar reset_token
        timestamp reset_expires
        timestamp created_at
        timestamp updated_at
    }

    user_profiles {
        uuid id PK
        uuid user_id FK
        varchar full_name
        varchar avatar_url
        varchar gender
        timestamp created_at
        timestamp updated_at
    }

    workspaces {
        uuid id PK
        uuid user_id FK
        varchar name
        text description
        varchar color
        varchar icon
        timestamp created_at
        timestamp updated_at
    }

    folders {
        uuid id PK
        uuid workspace_id FK
        uuid parent_id FK
        varchar name
        text description
        int sort_order
        timestamp created_at
        timestamp updated_at
    }

    documents {
        uuid id PK
        uuid user_id FK
        uuid workspace_id FK
        uuid folder_id FK
        varchar title
        text description
        varchar file_name
        varchar file_type
        bigint file_size
        varchar file_path
        varchar status
        int view_count
        timestamp created_at
        timestamp updated_at
    }

    document_chunks {
        uuid id PK
        uuid document_id FK
        int chunk_index
        text content
        text content_markdown
        int page_number
        int line_start
        int line_end
        varchar heading
        tsvector search_vector
        timestamp created_at
    }

    websites {
        uuid id PK
        uuid user_id FK
        uuid workspace_id FK
        uuid folder_id FK
        varchar url "per user: UNIQUE(user_id, url)"
        varchar title
        text description
        varchar status
        int view_count
        timestamp last_crawled_at
        timestamp created_at
        timestamp updated_at
    }

    website_contents {
        uuid id PK
        uuid website_id FK
        int content_index
        varchar heading
        varchar heading_level
        text content
        text content_markdown
        tsvector search_vector
        timestamp created_at
    }

    notes {
        uuid id PK
        uuid user_id FK
        uuid workspace_id FK
        uuid folder_id FK
        uuid document_id FK
        varchar title
        text content
        tsvector search_vector
        timestamp created_at
        timestamp updated_at
    }

    tags {
        uuid id PK
        uuid user_id FK
        varchar name UK
        varchar color
        timestamp created_at
    }

    document_tags {
        uuid document_id FK
        uuid tag_id FK
    }

    note_tags {
        uuid note_id FK
        uuid tag_id FK
    }

    chats {
        uuid id PK
        uuid user_id FK
        uuid workspace_id FK
        uuid folder_id FK
        uuid document_id FK
        varchar title
        varchar chat_mode
        int message_count
        timestamp created_at
        timestamp updated_at
    }

    chat_messages {
        uuid id PK
        uuid chat_id FK
        varchar role
        text content
        int token_count
        timestamp created_at
    }

    citations {
        uuid id PK
        uuid message_id FK
        uuid document_id FK
        uuid chunk_id FK
        uuid website_id FK
        uuid website_content_id FK
        uuid note_id FK
        varchar source_name
        varchar source_type
        int page_number
        int line_start
        int line_end
        varchar url
        text excerpt
        timestamp created_at
    }

    refresh_tokens {
        uuid id PK
        uuid user_id FK
        varchar token_hash UK
        timestamp expires_at
        timestamp revoked_at
        timestamp created_at
    }

    flashcards {
        uuid id PK
        uuid document_id FK
        uuid user_id FK
        text question
        text answer
        int sort_order
        timestamp created_at
    }

    quizzes {
        uuid id PK
        uuid document_id FK
        uuid user_id FK
        text question
        jsonb options
        varchar correct_answer
        text explanation
        int sort_order
        timestamp created_at
    }

    bookmarks {
        uuid id PK
        uuid user_id FK
        varchar entity_type
        uuid entity_id
        timestamp created_at
    }
```

## 5.2 Cardinality Legend (Crow's Foot)

| Ký hiệu | Ý nghĩa |
|---------|---------|
| `\|\|` | Exactly one (bắt buộc) |
| `o\|` | Zero or one (tùy chọn) |
| `\|{` | One or many |
| `o{` | Zero or many |

## 5.3 Quan hệ chính

| Quan hệ | Cardinality | Mô tả |
|---------|-------------|-------|
| users → user_profiles | 1:1 | Mỗi user có 1 profile |
| users → workspaces | 1:N | User sở hữu nhiều workspace |
| workspaces → folders | 1:N | Workspace chứa nhiều folder |
| workspaces → documents | 1:N | Workspace chứa nhiều document |
| folders → documents | 1:N | Folder chứa nhiều document |
| documents → document_chunks | 1:N | Document chia thành nhiều chunk |
| documents ↔ tags | N:M | Document gắn nhiều tag (qua document_tags) |
| websites → website_contents | 1:N | Website có nhiều content section |
| chats → chat_messages | 1:N | Chat có nhiều message |
| chat_messages → citations | 1:N | Message có nhiều citation |
| citations → documents | N:1 | Citation trỏ đến document |
| citations → document_chunks | N:1 | Citation trỏ đến chunk cụ thể |

## 5.4 ERD — Citation System (chi tiết)

```mermaid
erDiagram
    chat_messages ||--o{ citations : has
    citations }o--o| documents : "source: document"
    citations }o--o| document_chunks : "source: page/line"
    citations }o--o| websites : "source: website"
    citations }o--o| website_contents : "source: section"
    citations }o--o| notes : "source: note"

    citations {
        uuid id PK
        uuid message_id FK "chat message chứa citation"
        varchar source_type "document|website|note"
        uuid note_id FK "bắt buộc khi source_type=note"
        varchar source_name "Spring_Boot_Basic.pdf"
        int page_number "Trang 15 — MVP bắt buộc"
        int line_start "Dòng 120 — MVP bắt buộc"
        int line_end "Dòng 145"
        varchar url "react.dev — post-MVP website citation"
        text excerpt "đoạn text được trích dẫn"
    }
```

## 5.5 ERD — Polymorphic Bookmark

```mermaid
erDiagram
    users ||--o{ bookmarks : creates

    bookmarks {
        uuid id PK
        uuid user_id FK
        varchar entity_type "document|website|chat|note"
        uuid entity_id "ID của entity được bookmark"
        timestamp created_at
    }
```

> **Lưu ý:** Bookmark sử dụng polymorphic association (`entity_type` + `entity_id`) thay vì FK riêng cho từng loại, giảm số bảng junction.
