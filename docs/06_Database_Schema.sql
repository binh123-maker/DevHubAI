-- ============================================================
--  DevHub AI — PostgreSQL Database Schema
--  File    : 06_Database_Schema.sql
--  Version : 1.0.0
--  Date    : 2026-06-23
--  Engine  : PostgreSQL 15+
-- ============================================================
--
--  Table of Contents
--  -----------------
--  00. Extensions & Utility
--  01. Trigger Function  – auto updated_at
--  02. IDENTITY & AUTH
--       users
--       user_profiles
--       password_reset_tokens
--  03. KNOWLEDGE ORGANIZATION
--       workspaces
--       folders
--       documents
--       document_chunks
--       websites
--       website_contents
--  04. TAGGING & BOOKMARKS
--       tags
--       document_tags
--       bookmarks
--  05. AI INTERACTION
--       notes
--       chats
--       chat_messages
--       citations
--  06. LEARNING TOOLS
--       flashcards
--       quizzes
--  07. INDEXES
--  08. POST-CREATION COMMENTS
-- ============================================================


-- ============================================================
--  00. EXTENSIONS
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- for gen_random_uuid() on PG < 13


-- ============================================================
--  01. TRIGGER FUNCTION — auto-update updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Helper macro to attach the trigger to any table
-- Usage: SELECT attach_updated_at_trigger('table_name');
CREATE OR REPLACE FUNCTION attach_updated_at_trigger(tbl TEXT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format(
        'CREATE TRIGGER trg_%s_updated_at
         BEFORE UPDATE ON %I
         FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();',
        tbl, tbl
    );
END;
$$;


-- ============================================================
--  02. IDENTITY & AUTH
-- ============================================================

-- ------------------------------------------------------------
--  users
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              UUID            NOT NULL DEFAULT gen_random_uuid(),
    email           VARCHAR(320)    NOT NULL,
    password_hash   VARCHAR(255)    NULL,        -- NULL for OAuth-only accounts
    google_id       VARCHAR(255)    NULL,
    facebook_id     VARCHAR(255)    NULL,
    role            VARCHAR(20)     NOT NULL DEFAULT 'user',
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    last_login      TIMESTAMPTZ     NULL,

    CONSTRAINT pk_users                 PRIMARY KEY (id),
    CONSTRAINT uq_users_email           UNIQUE      (email),
    CONSTRAINT uq_users_google_id       UNIQUE      (google_id),
    CONSTRAINT uq_users_facebook_id     UNIQUE      (facebook_id),
    CONSTRAINT chk_users_role           CHECK       (role IN ('user', 'admin', 'moderator')),
    CONSTRAINT chk_users_email_format   CHECK       (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$')
);

SELECT attach_updated_at_trigger('users');


-- ------------------------------------------------------------
--  user_profiles
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_profiles (
    id              UUID            NOT NULL DEFAULT gen_random_uuid(),
    user_id         UUID            NOT NULL,
    full_name       VARCHAR(255)    NOT NULL,
    avatar_url      TEXT            NULL,
    gender          VARCHAR(20)     NOT NULL DEFAULT 'prefer_not',
    bio             TEXT            NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_user_profiles             PRIMARY KEY (id),
    CONSTRAINT uq_user_profiles_user_id     UNIQUE      (user_id),
    CONSTRAINT fk_user_profiles_user_id     FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT chk_user_profiles_gender     CHECK (gender IN ('male', 'female', 'other', 'prefer_not'))
);

SELECT attach_updated_at_trigger('user_profiles');


-- ------------------------------------------------------------
--  password_reset_tokens
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id              UUID            NOT NULL DEFAULT gen_random_uuid(),
    user_id         UUID            NOT NULL,
    token_hash      VARCHAR(64)     NOT NULL,   -- SHA-256 hex digest of raw token
    expires_at      TIMESTAMPTZ     NOT NULL,
    is_used         BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_password_reset_tokens             PRIMARY KEY (id),
    CONSTRAINT uq_password_reset_tokens_hash        UNIQUE      (token_hash),
    CONSTRAINT fk_password_reset_tokens_user_id     FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- ============================================================
--  03. KNOWLEDGE ORGANIZATION
-- ============================================================

-- ------------------------------------------------------------
--  workspaces
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS workspaces (
    id              UUID            NOT NULL DEFAULT gen_random_uuid(),
    user_id         UUID            NOT NULL,
    name            VARCHAR(255)    NOT NULL,
    description     TEXT            NULL,
    icon            VARCHAR(100)    NULL,    -- emoji character or icon identifier
    color           VARCHAR(7)      NULL,    -- hex color e.g. #3B82F6
    is_default      BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_workspaces            PRIMARY KEY (id),
    CONSTRAINT fk_workspaces_user_id    FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT chk_workspaces_color     CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'),
    CONSTRAINT uq_workspaces_user_name  UNIQUE (user_id, name)
);

SELECT attach_updated_at_trigger('workspaces');

-- Ensure at most one default workspace per user
CREATE UNIQUE INDEX IF NOT EXISTS uix_workspaces_default_per_user
    ON workspaces (user_id)
    WHERE is_default = TRUE;


-- ------------------------------------------------------------
--  folders
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS folders (
    id                  UUID            NOT NULL DEFAULT gen_random_uuid(),
    workspace_id        UUID            NOT NULL,
    user_id             UUID            NOT NULL,
    name                VARCHAR(255)    NOT NULL,
    description         TEXT            NULL,
    parent_folder_id    UUID            NULL,    -- self-referential; NULL = root folder
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_folders                       PRIMARY KEY (id),
    CONSTRAINT fk_folders_workspace_id          FOREIGN KEY (workspace_id)
        REFERENCES workspaces (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_folders_user_id              FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_folders_parent_folder_id     FOREIGN KEY (parent_folder_id)
        REFERENCES folders (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT chk_folders_no_self_parent      CHECK (id <> parent_folder_id)
);

SELECT attach_updated_at_trigger('folders');


-- ------------------------------------------------------------
--  documents
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
    id                  UUID            NOT NULL DEFAULT gen_random_uuid(),
    user_id             UUID            NOT NULL,
    workspace_id        UUID            NOT NULL,
    folder_id           UUID            NULL,
    original_filename   VARCHAR(500)    NOT NULL,
    stored_filename     VARCHAR(500)    NOT NULL,   -- UUID-based path on storage
    file_type           VARCHAR(20)     NOT NULL,   -- pdf | docx | txt | md | etc.
    file_size           BIGINT          NOT NULL DEFAULT 0,  -- bytes
    mime_type           VARCHAR(127)    NOT NULL,
    content_markdown    TEXT            NULL,       -- extracted after processing
    description         TEXT            NULL,
    is_processed        BOOLEAN         NOT NULL DEFAULT FALSE,
    view_count          INTEGER         NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_documents                 PRIMARY KEY (id),
    CONSTRAINT uq_documents_stored_filename UNIQUE      (stored_filename),
    CONSTRAINT fk_documents_user_id         FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_documents_workspace_id    FOREIGN KEY (workspace_id)
        REFERENCES workspaces (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_documents_folder_id       FOREIGN KEY (folder_id)
        REFERENCES folders (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT chk_documents_file_size      CHECK (file_size >= 0),
    CONSTRAINT chk_documents_view_count     CHECK (view_count >= 0)
);

SELECT attach_updated_at_trigger('documents');


-- ------------------------------------------------------------
--  document_chunks
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS document_chunks (
    id              UUID            NOT NULL DEFAULT gen_random_uuid(),
    document_id     UUID            NOT NULL,
    chunk_index     INTEGER         NOT NULL,   -- zero-based ordering within document
    content         TEXT            NOT NULL,
    page_number     INTEGER         NULL,
    line_start      INTEGER         NULL,
    line_end        INTEGER         NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_document_chunks               PRIMARY KEY (id),
    CONSTRAINT fk_document_chunks_document_id   FOREIGN KEY (document_id)
        REFERENCES documents (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT uq_document_chunks_index         UNIQUE (document_id, chunk_index),
    CONSTRAINT chk_document_chunks_index        CHECK (chunk_index >= 0),
    CONSTRAINT chk_document_chunks_page         CHECK (page_number IS NULL OR page_number >= 1),
    CONSTRAINT chk_document_chunks_lines        CHECK (
        line_start IS NULL OR
        line_end   IS NULL OR
        line_end   >= line_start
    )
);


-- ------------------------------------------------------------
--  websites
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS websites (
    id              UUID            NOT NULL DEFAULT gen_random_uuid(),
    user_id         UUID            NOT NULL,
    workspace_id    UUID            NOT NULL,
    folder_id       UUID            NULL,
    url             TEXT            NOT NULL,
    title           VARCHAR(500)    NULL,
    description     TEXT            NULL,
    favicon_url     TEXT            NULL,
    is_crawled      BOOLEAN         NOT NULL DEFAULT FALSE,
    crawled_at      TIMESTAMPTZ     NULL,
    view_count      INTEGER         NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_websites              PRIMARY KEY (id),
    CONSTRAINT fk_websites_user_id      FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_websites_workspace_id FOREIGN KEY (workspace_id)
        REFERENCES workspaces (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_websites_folder_id    FOREIGN KEY (folder_id)
        REFERENCES folders (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT chk_websites_url         CHECK (url ~ '^https?://'),
    CONSTRAINT chk_websites_view_count  CHECK (view_count >= 0)
);

SELECT attach_updated_at_trigger('websites');


-- ------------------------------------------------------------
--  website_contents
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS website_contents (
    id              UUID            NOT NULL DEFAULT gen_random_uuid(),
    website_id      UUID            NOT NULL,
    content_type    VARCHAR(20)     NOT NULL,
    content         TEXT            NOT NULL,
    heading_level   INTEGER         NULL,   -- 1-6; only valid when content_type = 'heading'
    sequence_order  INTEGER         NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_website_contents              PRIMARY KEY (id),
    CONSTRAINT fk_website_contents_website_id   FOREIGN KEY (website_id)
        REFERENCES websites (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT chk_website_contents_type        CHECK (content_type IN ('heading', 'paragraph', 'code', 'list')),
    CONSTRAINT chk_website_contents_heading_lvl CHECK (
        heading_level IS NULL OR
        heading_level BETWEEN 1 AND 6
    ),
    CONSTRAINT chk_website_contents_heading_req CHECK (
        content_type <> 'heading' OR heading_level IS NOT NULL
    ),
    CONSTRAINT chk_website_contents_seq         CHECK (sequence_order >= 0)
);


-- ============================================================
--  04. TAGGING & BOOKMARKS
-- ============================================================

-- ------------------------------------------------------------
--  tags
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tags (
    id          UUID            NOT NULL DEFAULT gen_random_uuid(),
    user_id     UUID            NOT NULL,
    name        VARCHAR(100)    NOT NULL,
    color       VARCHAR(7)      NOT NULL DEFAULT '#6B7280',  -- tailwind gray-500
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_tags              PRIMARY KEY (id),
    CONSTRAINT fk_tags_user_id      FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT uq_tags_user_name    UNIQUE (user_id, name),
    CONSTRAINT chk_tags_color       CHECK (color ~ '^#[0-9A-Fa-f]{6}$')
);


-- ------------------------------------------------------------
--  document_tags  (many-to-many join)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS document_tags (
    document_id     UUID    NOT NULL,
    tag_id          UUID    NOT NULL,

    CONSTRAINT pk_document_tags             PRIMARY KEY (document_id, tag_id),
    CONSTRAINT fk_document_tags_document    FOREIGN KEY (document_id)
        REFERENCES documents (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_document_tags_tag         FOREIGN KEY (tag_id)
        REFERENCES tags (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- ------------------------------------------------------------
--  bookmarks  (polymorphic)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bookmarks (
    id          UUID            NOT NULL DEFAULT gen_random_uuid(),
    user_id     UUID            NOT NULL,
    item_type   VARCHAR(20)     NOT NULL,
    item_id     UUID            NOT NULL,   -- polymorphic; no DB-level FK
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_bookmarks                 PRIMARY KEY (id),
    CONSTRAINT fk_bookmarks_user_id         FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT chk_bookmarks_item_type      CHECK (item_type IN ('document', 'website', 'chat', 'note')),
    CONSTRAINT uq_bookmarks_user_item       UNIQUE (user_id, item_type, item_id)
);


-- ============================================================
--  05. AI INTERACTION
-- ============================================================

-- ------------------------------------------------------------
--  notes
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notes (
    id                  UUID            NOT NULL DEFAULT gen_random_uuid(),
    user_id             UUID            NOT NULL,
    workspace_id        UUID            NULL,
    folder_id           UUID            NULL,
    document_id         UUID            NULL,
    title               VARCHAR(500)    NOT NULL,
    content_markdown    TEXT            NOT NULL DEFAULT '',
    is_ai_generated     BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_notes                 PRIMARY KEY (id),
    CONSTRAINT fk_notes_user_id         FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_notes_workspace_id    FOREIGN KEY (workspace_id)
        REFERENCES workspaces (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_notes_folder_id       FOREIGN KEY (folder_id)
        REFERENCES folders (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_notes_document_id     FOREIGN KEY (document_id)
        REFERENCES documents (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

SELECT attach_updated_at_trigger('notes');


-- ------------------------------------------------------------
--  chats
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chats (
    id              UUID            NOT NULL DEFAULT gen_random_uuid(),
    user_id         UUID            NOT NULL,
    title           VARCHAR(500)    NOT NULL DEFAULT 'New Chat',
    chat_mode       VARCHAR(20)     NOT NULL DEFAULT 'global',
    scope_id        UUID            NULL,    -- polymorphic ref to workspace/folder/document
    message_count   INTEGER         NOT NULL DEFAULT 0,
    is_bookmarked   BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_chats                 PRIMARY KEY (id),
    CONSTRAINT fk_chats_user_id         FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT chk_chats_mode           CHECK (chat_mode IN ('global', 'workspace', 'folder', 'document')),
    CONSTRAINT chk_chats_scope          CHECK (
        (chat_mode = 'global'    AND scope_id IS NULL) OR
        (chat_mode <> 'global'   AND scope_id IS NOT NULL)
    ),
    CONSTRAINT chk_chats_message_count  CHECK (message_count >= 0)
);

SELECT attach_updated_at_trigger('chats');


-- ------------------------------------------------------------
--  chat_messages
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_messages (
    id              UUID            NOT NULL DEFAULT gen_random_uuid(),
    chat_id         UUID            NOT NULL,
    role            VARCHAR(20)     NOT NULL,
    content         TEXT            NOT NULL,
    tokens_used     INTEGER         NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_chat_messages             PRIMARY KEY (id),
    CONSTRAINT fk_chat_messages_chat_id     FOREIGN KEY (chat_id)
        REFERENCES chats (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT chk_chat_messages_role       CHECK (role IN ('user', 'assistant')),
    CONSTRAINT chk_chat_messages_tokens     CHECK (tokens_used IS NULL OR tokens_used >= 0)
);


-- ------------------------------------------------------------
--  citations
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS citations (
    id                  UUID            NOT NULL DEFAULT gen_random_uuid(),
    chat_message_id     UUID            NOT NULL,
    document_id         UUID            NULL,
    website_id          UUID            NULL,
    page_number         INTEGER         NULL,
    line_start          INTEGER         NULL,
    line_end            INTEGER         NULL,
    relevance_score     NUMERIC(4, 3)   NOT NULL DEFAULT 0,  -- 0.000 – 1.000
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_citations                         PRIMARY KEY (id),
    CONSTRAINT fk_citations_chat_message_id         FOREIGN KEY (chat_message_id)
        REFERENCES chat_messages (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_citations_document_id             FOREIGN KEY (document_id)
        REFERENCES documents (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_citations_website_id              FOREIGN KEY (website_id)
        REFERENCES websites (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT chk_citations_source                 CHECK (
        (document_id IS NOT NULL AND website_id IS NULL) OR
        (document_id IS NULL     AND website_id IS NOT NULL)
    ),
    CONSTRAINT chk_citations_relevance_score        CHECK (relevance_score BETWEEN 0 AND 1),
    CONSTRAINT chk_citations_line_range             CHECK (
        line_start IS NULL OR
        line_end   IS NULL OR
        line_end   >= line_start
    ),
    CONSTRAINT chk_citations_page                   CHECK (page_number IS NULL OR page_number >= 1)
);


-- ============================================================
--  06. LEARNING TOOLS
-- ============================================================

-- ------------------------------------------------------------
--  flashcards
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS flashcards (
    id              UUID            NOT NULL DEFAULT gen_random_uuid(),
    user_id         UUID            NOT NULL,
    document_id     UUID            NULL,
    question        TEXT            NOT NULL,
    answer          TEXT            NOT NULL,
    difficulty      VARCHAR(10)     NOT NULL DEFAULT 'medium',
    review_count    INTEGER         NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_flashcards                PRIMARY KEY (id),
    CONSTRAINT fk_flashcards_user_id        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_flashcards_document_id    FOREIGN KEY (document_id)
        REFERENCES documents (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT chk_flashcards_difficulty    CHECK (difficulty IN ('easy', 'medium', 'hard')),
    CONSTRAINT chk_flashcards_review_count  CHECK (review_count >= 0)
);

SELECT attach_updated_at_trigger('flashcards');


-- ------------------------------------------------------------
--  quizzes
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quizzes (
    id              UUID            NOT NULL DEFAULT gen_random_uuid(),
    user_id         UUID            NOT NULL,
    document_id     UUID            NULL,
    question        TEXT            NOT NULL,
    option_a        TEXT            NOT NULL,
    option_b        TEXT            NOT NULL,
    option_c        TEXT            NOT NULL,
    option_d        TEXT            NOT NULL,
    correct_answer  VARCHAR(1)      NOT NULL,   -- 'a' | 'b' | 'c' | 'd'
    explanation     TEXT            NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_quizzes                   PRIMARY KEY (id),
    CONSTRAINT fk_quizzes_user_id           FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_quizzes_document_id       FOREIGN KEY (document_id)
        REFERENCES documents (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT chk_quizzes_correct_answer   CHECK (correct_answer IN ('a', 'b', 'c', 'd'))
);


-- ============================================================
--  07. INDEXES
-- ============================================================

-- users
CREATE INDEX IF NOT EXISTS idx_users_email          ON users           (email);
CREATE INDEX IF NOT EXISTS idx_users_google_id      ON users           (google_id)       WHERE google_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_facebook_id    ON users           (facebook_id)     WHERE facebook_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_role           ON users           (role);
CREATE INDEX IF NOT EXISTS idx_users_is_active      ON users           (is_active);
CREATE INDEX IF NOT EXISTS idx_users_last_login     ON users           (last_login DESC) WHERE last_login IS NOT NULL;

-- user_profiles
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id    ON user_profiles   (user_id);

-- password_reset_tokens
CREATE INDEX IF NOT EXISTS idx_prt_user_id              ON password_reset_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_prt_token_hash           ON password_reset_tokens (token_hash);
CREATE INDEX IF NOT EXISTS idx_prt_expires_at           ON password_reset_tokens (expires_at) WHERE is_used = FALSE;

-- workspaces
CREATE INDEX IF NOT EXISTS idx_workspaces_user_id       ON workspaces      (user_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_is_default    ON workspaces      (user_id, is_default);

-- folders
CREATE INDEX IF NOT EXISTS idx_folders_workspace_id     ON folders         (workspace_id);
CREATE INDEX IF NOT EXISTS idx_folders_user_id          ON folders         (user_id);
CREATE INDEX IF NOT EXISTS idx_folders_parent           ON folders         (parent_folder_id) WHERE parent_folder_id IS NOT NULL;

-- documents
CREATE INDEX IF NOT EXISTS idx_documents_user_id        ON documents       (user_id);
CREATE INDEX IF NOT EXISTS idx_documents_workspace_id   ON documents       (workspace_id);
CREATE INDEX IF NOT EXISTS idx_documents_folder_id      ON documents       (folder_id)        WHERE folder_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_documents_is_processed   ON documents       (is_processed);
CREATE INDEX IF NOT EXISTS idx_documents_file_type      ON documents       (file_type);
CREATE INDEX IF NOT EXISTS idx_documents_created_at     ON documents       (created_at DESC);

-- document_chunks
CREATE INDEX IF NOT EXISTS idx_document_chunks_doc_id   ON document_chunks (document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_index    ON document_chunks (document_id, chunk_index);

-- websites
CREATE INDEX IF NOT EXISTS idx_websites_user_id         ON websites        (user_id);
CREATE INDEX IF NOT EXISTS idx_websites_workspace_id    ON websites        (workspace_id);
CREATE INDEX IF NOT EXISTS idx_websites_folder_id       ON websites        (folder_id)        WHERE folder_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_websites_is_crawled      ON websites        (is_crawled);
CREATE INDEX IF NOT EXISTS idx_websites_created_at      ON websites        (created_at DESC);

-- website_contents
CREATE INDEX IF NOT EXISTS idx_website_contents_site_id     ON website_contents (website_id);
CREATE INDEX IF NOT EXISTS idx_website_contents_type        ON website_contents (website_id, content_type);
CREATE INDEX IF NOT EXISTS idx_website_contents_seq         ON website_contents (website_id, sequence_order);

-- tags
CREATE INDEX IF NOT EXISTS idx_tags_user_id             ON tags            (user_id);

-- document_tags
CREATE INDEX IF NOT EXISTS idx_document_tags_tag_id     ON document_tags   (tag_id);
CREATE INDEX IF NOT EXISTS idx_document_tags_doc_id     ON document_tags   (document_id);

-- bookmarks
CREATE INDEX IF NOT EXISTS idx_bookmarks_user_id        ON bookmarks       (user_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_item           ON bookmarks       (user_id, item_type);
CREATE INDEX IF NOT EXISTS idx_bookmarks_item_id        ON bookmarks       (item_id);

-- notes
CREATE INDEX IF NOT EXISTS idx_notes_user_id            ON notes           (user_id);
CREATE INDEX IF NOT EXISTS idx_notes_workspace_id       ON notes           (workspace_id)     WHERE workspace_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_notes_folder_id          ON notes           (folder_id)        WHERE folder_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_notes_document_id        ON notes           (document_id)      WHERE document_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_notes_is_ai_generated    ON notes           (is_ai_generated);
CREATE INDEX IF NOT EXISTS idx_notes_created_at         ON notes           (created_at DESC);

-- chats
CREATE INDEX IF NOT EXISTS idx_chats_user_id            ON chats           (user_id);
CREATE INDEX IF NOT EXISTS idx_chats_chat_mode          ON chats           (chat_mode);
CREATE INDEX IF NOT EXISTS idx_chats_scope_id           ON chats           (scope_id)         WHERE scope_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_chats_is_bookmarked      ON chats           (user_id, is_bookmarked);
CREATE INDEX IF NOT EXISTS idx_chats_created_at         ON chats           (created_at DESC);

-- chat_messages
CREATE INDEX IF NOT EXISTS idx_chat_messages_chat_id    ON chat_messages   (chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_role       ON chat_messages   (chat_id, role);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages   (created_at);

-- citations
CREATE INDEX IF NOT EXISTS idx_citations_message_id     ON citations       (chat_message_id);
CREATE INDEX IF NOT EXISTS idx_citations_document_id    ON citations       (document_id)      WHERE document_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_citations_website_id     ON citations       (website_id)       WHERE website_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_citations_relevance      ON citations       (relevance_score DESC);

-- flashcards
CREATE INDEX IF NOT EXISTS idx_flashcards_user_id       ON flashcards      (user_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_document_id   ON flashcards      (document_id)      WHERE document_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_flashcards_difficulty    ON flashcards      (user_id, difficulty);

-- quizzes
CREATE INDEX IF NOT EXISTS idx_quizzes_user_id          ON quizzes         (user_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_document_id      ON quizzes         (document_id)      WHERE document_id IS NOT NULL;


-- ============================================================
--  08. TABLE & COLUMN COMMENTS
-- ============================================================

-- ── users ───────────────────────────────────────────────────
COMMENT ON TABLE  users                     IS 'Core authentication records. Supports local email/password and OAuth (Google, Facebook) strategies.';
COMMENT ON COLUMN users.id                  IS 'Primary key — UUID v4 generated by gen_random_uuid().';
COMMENT ON COLUMN users.email               IS 'Unique email address; used as login identifier for local strategy.';
COMMENT ON COLUMN users.password_hash       IS 'bcrypt hash of the password. NULL for pure-OAuth accounts.';
COMMENT ON COLUMN users.google_id           IS 'Google OAuth subject identifier. NULL if not linked.';
COMMENT ON COLUMN users.facebook_id         IS 'Facebook OAuth user ID. NULL if not linked.';
COMMENT ON COLUMN users.role                IS 'Authorization role. Allowed: user | admin | moderator.';
COMMENT ON COLUMN users.is_active           IS 'Soft-disable flag. Inactive users cannot log in.';
COMMENT ON COLUMN users.last_login          IS 'Timestamp of most recent successful authentication.';

-- ── user_profiles ───────────────────────────────────────────
COMMENT ON TABLE  user_profiles             IS 'Extended profile data linked 1-to-1 with a user record.';
COMMENT ON COLUMN user_profiles.user_id     IS 'FK to users.id — one-to-one enforced by UNIQUE constraint.';
COMMENT ON COLUMN user_profiles.gender      IS 'Self-identified gender. Allowed: male | female | other | prefer_not.';
COMMENT ON COLUMN user_profiles.avatar_url  IS 'Absolute URL to the avatar image (CDN, S3, etc.).';

-- ── password_reset_tokens ───────────────────────────────────
COMMENT ON TABLE  password_reset_tokens         IS 'Short-lived single-use tokens for the forgot-password flow.';
COMMENT ON COLUMN password_reset_tokens.token_hash IS 'SHA-256 hex digest of the raw URL-safe token sent to the user. Never store the raw value.';
COMMENT ON COLUMN password_reset_tokens.is_used  IS 'Set to TRUE after the token is consumed; subsequent use is rejected.';

-- ── workspaces ──────────────────────────────────────────────
COMMENT ON TABLE  workspaces                IS 'Top-level organizational container owned by a single user.';
COMMENT ON COLUMN workspaces.icon           IS 'Emoji character or icon library key (e.g., "📚" or "heroicons/book").';
COMMENT ON COLUMN workspaces.color          IS 'Six-digit hex accent color (e.g., #3B82F6).';
COMMENT ON COLUMN workspaces.is_default     IS 'Exactly one workspace per user can be the default; enforced by partial unique index.';

-- ── folders ─────────────────────────────────────────────────
COMMENT ON TABLE  folders                           IS 'Recursive folder hierarchy within a workspace.';
COMMENT ON COLUMN folders.parent_folder_id          IS 'Self-referential FK. NULL indicates a root-level folder within the workspace.';

-- ── documents ───────────────────────────────────────────────
COMMENT ON TABLE  documents                         IS 'Uploaded files; metadata plus extracted Markdown content for AI indexing.';
COMMENT ON COLUMN documents.original_filename       IS 'Filename as provided by the user at upload time.';
COMMENT ON COLUMN documents.stored_filename         IS 'UUID-based filename used on disk/object-storage to avoid collisions.';
COMMENT ON COLUMN documents.content_markdown        IS 'Full text extracted and converted to Markdown after AI processing.';
COMMENT ON COLUMN documents.is_processed            IS 'FALSE until text extraction and chunking are complete.';
COMMENT ON COLUMN documents.view_count              IS 'Denormalized counter incremented on each document view.';

-- ── document_chunks ─────────────────────────────────────────
COMMENT ON TABLE  document_chunks                   IS 'Fixed-size text segments produced during AI ingestion for vector retrieval.';
COMMENT ON COLUMN document_chunks.chunk_index       IS 'Zero-based position of this chunk within the parent document.';
COMMENT ON COLUMN document_chunks.page_number       IS 'Source PDF/DOCX page (1-based). NULL for plain-text files.';
COMMENT ON COLUMN document_chunks.line_start        IS 'First line of the chunk within the source file (1-based).';
COMMENT ON COLUMN document_chunks.line_end          IS 'Last line of the chunk within the source file (inclusive, 1-based).';

-- ── websites ────────────────────────────────────────────────
COMMENT ON TABLE  websites                          IS 'Saved web URLs optionally crawled for AI context.';
COMMENT ON COLUMN websites.is_crawled               IS 'TRUE after content has been successfully extracted.';
COMMENT ON COLUMN websites.crawled_at               IS 'Timestamp of most recent successful crawl.';
COMMENT ON COLUMN websites.view_count               IS 'Denormalized counter incremented on each website view.';

-- ── website_contents ────────────────────────────────────────
COMMENT ON TABLE  website_contents                      IS 'Structured content blocks extracted from a crawled website.';
COMMENT ON COLUMN website_contents.content_type         IS 'Block type. Allowed: heading | paragraph | code | list.';
COMMENT ON COLUMN website_contents.heading_level        IS 'HTML heading depth 1-6. Required when content_type = heading.';
COMMENT ON COLUMN website_contents.sequence_order       IS 'Ordinal position of this block within the crawled page.';

-- ── tags ────────────────────────────────────────────────────
COMMENT ON TABLE  tags                              IS 'User-defined labels with hex color codes for document organization.';
COMMENT ON COLUMN tags.color                        IS 'Six-digit hex color (e.g., #FF5733). Used for UI badge rendering.';

-- ── document_tags ───────────────────────────────────────────
COMMENT ON TABLE  document_tags                     IS 'Many-to-many join table between documents and tags.';

-- ── bookmarks ───────────────────────────────────────────────
COMMENT ON TABLE  bookmarks                         IS 'Polymorphic saved-items list. item_type identifies which table item_id references.';
COMMENT ON COLUMN bookmarks.item_type               IS 'Discriminator. Allowed: document | website | chat | note.';
COMMENT ON COLUMN bookmarks.item_id                 IS 'UUID of the bookmarked entity in the table identified by item_type. No DB-level FK.';

-- ── notes ───────────────────────────────────────────────────
COMMENT ON TABLE  notes                             IS 'User-authored or AI-generated Markdown notes, optionally scoped to workspace/folder/document.';
COMMENT ON COLUMN notes.is_ai_generated             IS 'TRUE when the note was produced by the AI assistant rather than manually written.';

-- ── chats ───────────────────────────────────────────────────
COMMENT ON TABLE  chats                             IS 'AI conversation sessions. chat_mode + scope_id define the retrieval context.';
COMMENT ON COLUMN chats.chat_mode                   IS 'Context scope. Allowed: global | workspace | folder | document.';
COMMENT ON COLUMN chats.scope_id                    IS 'Polymorphic UUID referencing workspace, folder, or document. NULL for global mode.';
COMMENT ON COLUMN chats.message_count               IS 'Denormalized counter for quick listing. Updated by application logic.';

-- ── chat_messages ───────────────────────────────────────────
COMMENT ON TABLE  chat_messages                     IS 'Individual turns within a chat session.';
COMMENT ON COLUMN chat_messages.role                IS 'Speaker identifier. Allowed: user | assistant.';
COMMENT ON COLUMN chat_messages.tokens_used         IS 'LLM token count for this message; NULL if not tracked.';

-- ── citations ───────────────────────────────────────────────
COMMENT ON TABLE  citations                         IS 'Source references cited in an AI assistant message.';
COMMENT ON COLUMN citations.relevance_score         IS 'Cosine similarity or relevance score between 0.000 and 1.000.';
COMMENT ON COLUMN citations.document_id             IS 'References documents.id. Mutually exclusive with website_id.';
COMMENT ON COLUMN citations.website_id              IS 'References websites.id. Mutually exclusive with document_id.';

-- ── flashcards ──────────────────────────────────────────────
COMMENT ON TABLE  flashcards                        IS 'Question/answer pairs for spaced-repetition study sessions.';
COMMENT ON COLUMN flashcards.difficulty             IS 'Self-assessed or AI-assigned difficulty. Allowed: easy | medium | hard.';
COMMENT ON COLUMN flashcards.review_count           IS 'Total number of times this card has been reviewed.';

-- ── quizzes ─────────────────────────────────────────────────
COMMENT ON TABLE  quizzes                           IS 'Multiple-choice questions for assessment, optionally generated from a source document.';
COMMENT ON COLUMN quizzes.correct_answer            IS 'Key of the correct option. Allowed: a | b | c | d.';
COMMENT ON COLUMN quizzes.explanation               IS 'Optional rationale explaining why the correct answer is correct.';


-- ============================================================
--  END OF SCHEMA
-- ============================================================
