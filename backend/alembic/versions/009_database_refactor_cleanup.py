"""database_refactor_cleanup

Revision ID: 009_database_refactor_cleanup
Revises: 008_create_phase3_tables
Create Date: 2026-08-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "009_database_refactor_cleanup"
down_revision: Union[str, None] = "008_create_phase3_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    # 1. Foreign keys on chats table
    if "chats" in tables:
        fks = inspector.get_foreign_keys("chats")
        fk_names = {fk["name"] for fk in fks if fk.get("name")}
        
        if "fk_chats_folder_id" not in fk_names:
            op.create_foreign_key(
                "fk_chats_folder_id",
                "chats",
                "folders",
                ["folder_id"],
                ["id"],
                ondelete="SET NULL",
            )
        if "fk_chats_document_id" not in fk_names:
            op.create_foreign_key(
                "fk_chats_document_id",
                "chats",
                "documents",
                ["document_id"],
                ["id"],
                ondelete="SET NULL",
            )

    # 2. Unique constraint on document_versions(document_id, version_number)
    if "document_versions" in tables:
        unique_constraints = {uc["name"] for uc in inspector.get_unique_constraints("document_versions")}
        if "uq_document_version_number" not in unique_constraints:
            op.create_unique_constraint(
                "uq_document_version_number",
                "document_versions",
                ["document_id", "version_number"],
            )

    # 3. Add AI execution telemetry columns to chat_messages
    if "chat_messages" in tables:
        chat_msg_columns = {c["name"] for c in inspector.get_columns("chat_messages")}
        if "provider" not in chat_msg_columns:
            op.add_column("chat_messages", sa.Column("provider", sa.String(50), nullable=True))
        if "model_name" not in chat_msg_columns:
            op.add_column("chat_messages", sa.Column("model_name", sa.String(100), nullable=True))
        if "prompt_tokens" not in chat_msg_columns:
            op.add_column("chat_messages", sa.Column("prompt_tokens", sa.Integer(), nullable=True))
        if "completion_tokens" not in chat_msg_columns:
            op.add_column("chat_messages", sa.Column("completion_tokens", sa.Integer(), nullable=True))
        if "total_tokens" not in chat_msg_columns:
            op.add_column("chat_messages", sa.Column("total_tokens", sa.Integer(), nullable=True))
        if "latency_ms" not in chat_msg_columns:
            op.add_column("chat_messages", sa.Column("latency_ms", sa.Integer(), nullable=True))
        if "finish_reason" not in chat_msg_columns:
            op.add_column("chat_messages", sa.Column("finish_reason", sa.String(50), nullable=True))

    # 4. Performance Indexes
    if "document_chunks" in tables:
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("document_chunks")}
        if "ix_document_chunks_version_index" not in existing_indexes:
            op.create_index(
                "ix_document_chunks_version_index",
                "document_chunks",
                ["document_version_id", "chunk_index"],
            )

    if "documents" in tables:
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("documents")}
        if "ix_documents_workspace_folder" not in existing_indexes:
            op.create_index(
                "ix_documents_workspace_folder",
                "documents",
                ["workspace_id", "folder_id"],
            )

    # 5. Safely drop legacy columns on users table if present
    if "users" in tables:
        user_columns = {c["name"] for c in inspector.get_columns("users")}
        for col_name in ["oauth_provider", "oauth_id", "reset_token", "reset_expires"]:
            if col_name in user_columns:
                op.drop_column("users", col_name)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "users" in tables:
        user_columns = {c["name"] for c in inspector.get_columns("users")}
        if "reset_expires" not in user_columns:
            op.add_column("users", sa.Column("reset_expires", sa.DateTime(timezone=True), nullable=True))
        if "reset_token" not in user_columns:
            op.add_column("users", sa.Column("reset_token", sa.String(255), nullable=True))
        if "oauth_id" not in user_columns:
            op.add_column("users", sa.Column("oauth_id", sa.String(255), nullable=True))

    if "documents" in tables:
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("documents")}
        if "ix_documents_workspace_folder" in existing_indexes:
            op.drop_index("ix_documents_workspace_folder", table_name="documents")

    if "document_chunks" in tables:
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("document_chunks")}
        if "ix_document_chunks_version_index" in existing_indexes:
            op.drop_index("ix_document_chunks_version_index", table_name="document_chunks")

    if "chat_messages" in tables:
        chat_msg_columns = {c["name"] for c in inspector.get_columns("chat_messages")}
        for col in ["finish_reason", "latency_ms", "total_tokens", "completion_tokens", "prompt_tokens", "model_name", "provider"]:
            if col in chat_msg_columns:
                op.drop_column("chat_messages", col)

    if "document_versions" in tables:
        unique_constraints = {uc["name"] for uc in inspector.get_unique_constraints("document_versions")}
        if "uq_document_version_number" in unique_constraints:
            op.drop_constraint("uq_document_version_number", "document_versions", type_="unique")

    if "chats" in tables:
        fks = inspector.get_foreign_keys("chats")
        fk_names = {fk["name"] for fk in fks if fk.get("name")}
        if "fk_chats_document_id" in fk_names:
            op.drop_constraint("fk_chats_document_id", "chats", type_="foreignkey")
        if "fk_chats_folder_id" in fk_names:
            op.drop_constraint("fk_chats_folder_id", "chats", type_="foreignkey")
