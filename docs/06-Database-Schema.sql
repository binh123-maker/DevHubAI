-- ============================================================
-- DevHub AI — PostgreSQL Database Schema
-- Version: 1.1 (P0 fixes applied — MVP-8W aligned)
-- ============================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================
-- ENUMS
-- ============================================================

CREATE TYPE user_role AS ENUM ('user', 'admin');
CREATE TYPE gender_type AS ENUM ('male', 'female', 'other', 'prefer_not_to_say');
CREATE TYPE oauth_provider AS ENUM ('local', 'google', 'facebook');
CREATE TYPE document_status AS ENUM ('uploading', 'processing', 'processed', 'failed');
CREATE TYPE website_status AS ENUM ('pending', 'crawling', 'crawled', 'failed');
CREATE TYPE chat_mode AS ENUM ('global', 'workspace', 'folder', 'document');
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');
CREATE TYPE citation_source_type AS ENUM ('document', 'website', 'note');
CREATE TYPE bookmark_entity_type AS ENUM ('document', 'website', 'chat', 'note');

-- ============================================================
-- USERS & PROFILES
-- ============================================================

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255),
    oauth_provider  oauth_provider NOT NULL DEFAULT 'local',
    oauth_id        VARCHAR(255),
    role            user_role NOT NULL DEFAULT 'user',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    reset_token     VARCHAR(255),
    reset_expires   TIMESTAMPTZ,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_oauth ON users(oauth_provider, oauth_id);
CREATE INDEX idx_users_reset_token ON users(reset_token) WHERE reset_token IS NOT NULL;
CREATE UNIQUE INDEX idx_users_oauth_unique
    ON users(oauth_provider, oauth_id)
    WHERE oauth_id IS NOT NULL;

CREATE TABLE user_profiles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    full_name       VARCHAR(255) NOT NULL,
    avatar_url      VARCHAR(500),
    gender          gender_type DEFAULT 'prefer_not_to_say',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- P0: Refresh token support (NFR-02.1, UC-A04)
CREATE TABLE refresh_tokens (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash      VARCHAR(255) NOT NULL UNIQUE,
    expires_at      TIMESTAMPTZ NOT NULL,
    revoked_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash) WHERE revoked_at IS NULL;

-- ============================================================
-- WORKSPACES & FOLDERS
-- ============================================================

CREATE TABLE workspaces (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    color           VARCHAR(7) DEFAULT '#3B82F6',
    icon            VARCHAR(50) DEFAULT 'folder',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, name)
);

CREATE INDEX idx_workspaces_user ON workspaces(user_id);

CREATE TABLE folders (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    parent_id       UUID REFERENCES folders(id) ON DELETE SET NULL,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    sort_order      INT NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(workspace_id, name, parent_id)
);

CREATE INDEX idx_folders_workspace ON folders(workspace_id);
CREATE INDEX idx_folders_parent ON folders(parent_id);

-- ============================================================
-- TAGS (Post-MVP — not used in MVP-8W)
-- ============================================================

CREATE TABLE tags (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    color           VARCHAR(7) DEFAULT '#6B7280',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, name)
);

CREATE INDEX idx_tags_user ON tags(user_id);

-- ============================================================
-- DOCUMENTS & CHUNKS
-- ============================================================

CREATE TABLE documents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    folder_id       UUID REFERENCES folders(id) ON DELETE SET NULL,
    title           VARCHAR(500) NOT NULL,
    description     TEXT,
    file_name       VARCHAR(500) NOT NULL,
    file_type       VARCHAR(50) NOT NULL,
    file_size       BIGINT NOT NULL DEFAULT 0,
    file_path       VARCHAR(1000) NOT NULL,
    status          document_status NOT NULL DEFAULT 'uploading',
    view_count      INT NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_documents_user ON documents(user_id);
CREATE INDEX idx_documents_workspace ON documents(workspace_id);
CREATE INDEX idx_documents_folder ON documents(folder_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_file_type ON documents(file_type);

CREATE TABLE document_chunks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index     INT NOT NULL,
    content         TEXT NOT NULL,
    content_markdown TEXT NOT NULL,
    page_number     INT,
    line_start      INT,
    line_end        INT,
    heading         VARCHAR(500),
    search_vector   TSVECTOR,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

CREATE INDEX idx_chunks_document ON document_chunks(document_id);
CREATE INDEX idx_chunks_search ON document_chunks USING GIN(search_vector);
CREATE INDEX idx_chunks_page ON document_chunks(document_id, page_number);

CREATE TABLE document_tags (
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tag_id          UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (document_id, tag_id)
);

-- P0: Document-folder-workspace consistency
CREATE OR REPLACE FUNCTION validate_document_folder_workspace()
RETURNS TRIGGER AS $$
DECLARE
    folder_ws_id UUID;
BEGIN
    IF NEW.folder_id IS NOT NULL THEN
        SELECT workspace_id INTO folder_ws_id FROM folders WHERE id = NEW.folder_id;
        IF folder_ws_id IS NULL THEN
            RAISE EXCEPTION 'Folder % does not exist', NEW.folder_id;
        END IF;
        IF folder_ws_id <> NEW.workspace_id THEN
            RAISE EXCEPTION 'Folder % does not belong to workspace %', NEW.folder_id, NEW.workspace_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_document_folder_workspace
    BEFORE INSERT OR UPDATE OF workspace_id, folder_id ON documents
    FOR EACH ROW EXECUTE FUNCTION validate_document_folder_workspace();

-- P0: Cascade workspace_id when folder moves between workspaces
CREATE OR REPLACE FUNCTION cascade_folder_workspace_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.workspace_id IS DISTINCT FROM NEW.workspace_id THEN
        UPDATE documents
        SET workspace_id = NEW.workspace_id, updated_at = NOW()
        WHERE folder_id = NEW.id;

        UPDATE websites
        SET workspace_id = NEW.workspace_id, updated_at = NOW()
        WHERE folder_id = NEW.id;

        UPDATE notes
        SET workspace_id = NEW.workspace_id, updated_at = NOW()
        WHERE folder_id = NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cascade_folder_workspace
    AFTER UPDATE OF workspace_id ON folders
    FOR EACH ROW EXECUTE FUNCTION cascade_folder_workspace_change();

-- Trigger: auto-update search_vector on document_chunks
CREATE OR REPLACE FUNCTION update_chunk_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('simple', COALESCE(NEW.heading, '') || ' ' || NEW.content);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_chunk_search_vector
    BEFORE INSERT OR UPDATE ON document_chunks
    FOR EACH ROW EXECUTE FUNCTION update_chunk_search_vector();

-- ============================================================
-- WEBSITES (Post-MVP)
-- ============================================================

CREATE TABLE websites (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    folder_id       UUID REFERENCES folders(id) ON DELETE SET NULL,
    url             VARCHAR(2000) NOT NULL,
    title           VARCHAR(500),
    description     TEXT,
    status          website_status NOT NULL DEFAULT 'pending',
    view_count      INT NOT NULL DEFAULT 0,
    last_crawled_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, url)
);

CREATE INDEX idx_websites_user ON websites(user_id);
CREATE INDEX idx_websites_workspace ON websites(workspace_id);

CREATE TABLE website_contents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    website_id      UUID NOT NULL REFERENCES websites(id) ON DELETE CASCADE,
    content_index   INT NOT NULL,
    heading         VARCHAR(500),
    heading_level   VARCHAR(5),
    content         TEXT NOT NULL,
    content_markdown TEXT NOT NULL,
    search_vector   TSVECTOR,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_webcontent_website ON website_contents(website_id);
CREATE INDEX idx_webcontent_search ON website_contents USING GIN(search_vector);

CREATE OR REPLACE FUNCTION update_webcontent_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('simple', COALESCE(NEW.heading, '') || ' ' || NEW.content);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_webcontent_search_vector
    BEFORE INSERT OR UPDATE ON website_contents
    FOR EACH ROW EXECUTE FUNCTION update_webcontent_search_vector();

-- ============================================================
-- NOTES (Post-MVP)
-- ============================================================

CREATE TABLE notes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    folder_id       UUID REFERENCES folders(id) ON DELETE SET NULL,
    document_id     UUID REFERENCES documents(id) ON DELETE SET NULL,
    title           VARCHAR(500) NOT NULL,
    content         TEXT NOT NULL DEFAULT '',
    search_vector   TSVECTOR,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notes_user ON notes(user_id);
CREATE INDEX idx_notes_workspace ON notes(workspace_id);
CREATE INDEX idx_notes_search ON notes USING GIN(search_vector);

CREATE TABLE note_tags (
    note_id         UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    tag_id          UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (note_id, tag_id)
);

-- P0: Notes FTS trigger
CREATE OR REPLACE FUNCTION update_note_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('simple', COALESCE(NEW.title, '') || ' ' || NEW.content);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_note_search_vector
    BEFORE INSERT OR UPDATE ON notes
    FOR EACH ROW EXECUTE FUNCTION update_note_search_vector();

-- ============================================================
-- CHATS & MESSAGES & CITATIONS
-- ============================================================

CREATE TABLE chats (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    folder_id       UUID REFERENCES folders(id) ON DELETE SET NULL,
    document_id     UUID REFERENCES documents(id) ON DELETE SET NULL,
    title           VARCHAR(500) NOT NULL DEFAULT 'Cuộc trò chuyện mới',
    chat_mode       chat_mode NOT NULL DEFAULT 'global',
    message_count   INT NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_chat_workspace_mode
        CHECK (chat_mode <> 'workspace' OR workspace_id IS NOT NULL),
    CONSTRAINT chk_chat_folder_mode
        CHECK (chat_mode <> 'folder' OR folder_id IS NOT NULL),
    CONSTRAINT chk_chat_document_mode
        CHECK (chat_mode <> 'document' OR document_id IS NOT NULL)
);

CREATE INDEX idx_chats_user ON chats(user_id);
CREATE INDEX idx_chats_mode ON chats(chat_mode);

CREATE TABLE chat_messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id         UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    role            message_role NOT NULL,
    content         TEXT NOT NULL,
    token_count     INT DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_chat ON chat_messages(chat_id);
CREATE INDEX idx_messages_created ON chat_messages(created_at);

-- P0: Citations schema — note_id added, MVP uses document fields only
CREATE TABLE citations (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id          UUID NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    document_id         UUID REFERENCES documents(id) ON DELETE SET NULL,
    chunk_id            UUID REFERENCES document_chunks(id) ON DELETE SET NULL,
    website_id          UUID REFERENCES websites(id) ON DELETE SET NULL,
    website_content_id  UUID REFERENCES website_contents(id) ON DELETE SET NULL,
    note_id             UUID REFERENCES notes(id) ON DELETE SET NULL,
    source_name         VARCHAR(500) NOT NULL,
    source_type         citation_source_type NOT NULL,
    page_number         INT,
    line_start          INT,
    line_end            INT,
    url                 VARCHAR(2000),
    excerpt             TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_citation_document
        CHECK (source_type <> 'document' OR document_id IS NOT NULL),
    CONSTRAINT chk_citation_website
        CHECK (source_type <> 'website' OR website_id IS NOT NULL),
    CONSTRAINT chk_citation_note
        CHECK (source_type <> 'note' OR note_id IS NOT NULL)
);

CREATE INDEX idx_citations_message ON citations(message_id);
CREATE INDEX idx_citations_document ON citations(document_id);
CREATE INDEX idx_citations_note ON citations(note_id);

-- ============================================================
-- AI GENERATED CONTENT (Post-MVP)
-- ============================================================

CREATE TABLE flashcards (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question        TEXT NOT NULL,
    answer          TEXT NOT NULL,
    sort_order      INT NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_flashcards_document ON flashcards(document_id);

CREATE TABLE quizzes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question        TEXT NOT NULL,
    options         JSONB NOT NULL,
    correct_answer  VARCHAR(10) NOT NULL,
    explanation     TEXT,
    sort_order      INT NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_quizzes_document ON quizzes(document_id);

-- ============================================================
-- BOOKMARKS (Post-MVP)
-- ============================================================

CREATE TABLE bookmarks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entity_type     bookmark_entity_type NOT NULL,
    entity_id       UUID NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, entity_type, entity_id)
);

CREATE INDEX idx_bookmarks_user ON bookmarks(user_id);
CREATE INDEX idx_bookmarks_entity ON bookmarks(entity_type, entity_id);

-- ============================================================
-- AI USAGE TRACKING
-- ============================================================

CREATE TABLE ai_usage_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action_type     VARCHAR(50) NOT NULL,
    token_count     INT DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ai_usage_user ON ai_usage_logs(user_id);
CREATE INDEX idx_ai_usage_created ON ai_usage_logs(created_at);

-- ============================================================
-- UPDATED_AT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_profiles_updated BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_workspaces_updated BEFORE UPDATE ON workspaces FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_folders_updated BEFORE UPDATE ON folders FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_documents_updated BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_websites_updated BEFORE UPDATE ON websites FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_notes_updated BEFORE UPDATE ON notes FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_chats_updated BEFORE UPDATE ON chats FOR EACH ROW EXECUTE FUNCTION update_updated_at();
