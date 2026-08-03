"""create_phase3_tables

Revision ID: 008_create_phase3_tables
Revises: 007_refactor_oauth_google_only
Create Date: 2026-08-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "008_create_phase3_tables"
down_revision: Union[str, None] = "007_refactor_oauth_google_only"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    # 1. Create verification_codes table if it does not exist
    if "verification_codes" not in tables:
        op.create_table(
            "verification_codes",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("purpose", sa.String(50), nullable=False),
            sa.Column("code_hash", sa.String(255), nullable=False),
            sa.Column("token_hash", sa.String(255), nullable=True),
            sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="5"),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_verification_codes_email_purpose", "verification_codes", ["email", "purpose"])
        op.create_index("ix_verification_codes_user_purpose", "verification_codes", ["user_id", "purpose"])
        op.create_index("ix_verification_codes_expires_at", "verification_codes", ["expires_at"])
        op.create_index("ix_verification_codes_created_at", "verification_codes", ["created_at"])
    else:
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("verification_codes")}
        if "ix_verification_codes_email_purpose" not in existing_indexes:
            op.create_index("ix_verification_codes_email_purpose", "verification_codes", ["email", "purpose"])
        if "ix_verification_codes_user_purpose" not in existing_indexes:
            op.create_index("ix_verification_codes_user_purpose", "verification_codes", ["user_id", "purpose"])
        if "ix_verification_codes_expires_at" not in existing_indexes:
            op.create_index("ix_verification_codes_expires_at", "verification_codes", ["expires_at"])
        if "ix_verification_codes_created_at" not in existing_indexes:
            op.create_index("ix_verification_codes_created_at", "verification_codes", ["created_at"])

    # 2. Create password_history table if it does not exist
    if "password_history" not in tables:
        op.create_table(
            "password_history",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("password_hash", sa.String(255), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_password_history_user_created", "password_history", ["user_id", "created_at"])
    else:
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("password_history")}
        if "ix_password_history_user_created" not in existing_indexes:
            op.create_index("ix_password_history_user_created", "password_history", ["user_id", "created_at"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "password_history" in tables:
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("password_history")}
        if "ix_password_history_user_created" in existing_indexes:
            op.drop_index("ix_password_history_user_created", table_name="password_history")
        op.drop_table("password_history")

    if "verification_codes" in tables:
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("verification_codes")}
        for idx_name in [
            "ix_verification_codes_created_at",
            "ix_verification_codes_expires_at",
            "ix_verification_codes_user_purpose",
            "ix_verification_codes_email_purpose",
        ]:
            if idx_name in existing_indexes:
                op.drop_index(idx_name, table_name="verification_codes")
        op.drop_table("verification_codes")
