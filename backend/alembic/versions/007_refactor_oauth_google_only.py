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
    # Drop obsolete columns
    op.drop_column("oauth_accounts", "is_primary_provider")
    op.drop_column("oauth_accounts", "provider_status")
    op.drop_column("oauth_accounts", "last_sync_at")
    op.drop_column("oauth_accounts", "provider_version")

    # Add CHECK constraint for provider = 'google'
    op.create_check_constraint(
        "ck_oauth_accounts_provider_google",
        "oauth_accounts",
        "provider = 'google'"
    )

    # Add index on email
    op.create_index("ix_oauth_accounts_email", "oauth_accounts", ["email"])


def downgrade() -> None:
    op.drop_index("ix_oauth_accounts_email", table_name="oauth_accounts")
    op.drop_constraint("ck_oauth_accounts_provider_google", "oauth_accounts", type_="check")

    op.add_column("oauth_accounts", sa.Column("provider_version", sa.String(20), server_default="v2", nullable=False))
    op.add_column("oauth_accounts", sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("oauth_accounts", sa.Column("provider_status", sa.String(50), server_default="active", nullable=False))
    op.add_column("oauth_accounts", sa.Column("is_primary_provider", sa.Boolean(), server_default=sa.text("false"), nullable=False))
