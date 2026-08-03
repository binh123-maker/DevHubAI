"""refactor_oauth_google_only

Revision ID: 007_refactor_oauth_google_only
Revises: 006_oauth_accounts
Create Date: 2026-08-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "007_refactor_oauth_google_only"
down_revision: Union[str, None] = "006_oauth_accounts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "oauth_accounts" in tables:
        columns = {c["name"] for c in inspector.get_columns("oauth_accounts")}
        if "is_primary_provider" in columns:
            op.drop_column("oauth_accounts", "is_primary_provider")
        if "provider_status" in columns:
            op.drop_column("oauth_accounts", "provider_status")
        if "last_sync_at" in columns:
            op.drop_column("oauth_accounts", "last_sync_at")
        if "provider_version" in columns:
            op.drop_column("oauth_accounts", "provider_version")

        constraints = {c["name"] for c in inspector.get_check_constraints("oauth_accounts")}
        if "ck_oauth_accounts_provider_google" not in constraints:
            op.create_check_constraint(
                "ck_oauth_accounts_provider_google",
                "oauth_accounts",
                "provider = 'google'"
            )

        indexes = {i["name"] for i in inspector.get_indexes("oauth_accounts")}
        if "ix_oauth_accounts_email" not in indexes:
            op.create_index("ix_oauth_accounts_email", "oauth_accounts", ["email"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "oauth_accounts" in tables:
        indexes = {i["name"] for i in inspector.get_indexes("oauth_accounts")}
        if "ix_oauth_accounts_email" in indexes:
            op.drop_index("ix_oauth_accounts_email", table_name="oauth_accounts")

        constraints = {c["name"] for c in inspector.get_check_constraints("oauth_accounts")}
        if "ck_oauth_accounts_provider_google" in constraints:
            op.drop_constraint("ck_oauth_accounts_provider_google", "oauth_accounts", type_="check")

        columns = {c["name"] for c in inspector.get_columns("oauth_accounts")}
        if "provider_version" not in columns:
            op.add_column("oauth_accounts", sa.Column("provider_version", sa.String(20), server_default="v2", nullable=False))
        if "last_sync_at" not in columns:
            op.add_column("oauth_accounts", sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True))
        if "provider_status" not in columns:
            op.add_column("oauth_accounts", sa.Column("provider_status", sa.String(50), server_default="active", nullable=False))
        if "is_primary_provider" not in columns:
            op.add_column("oauth_accounts", sa.Column("is_primary_provider", sa.Boolean(), server_default=sa.text("false"), nullable=False))
