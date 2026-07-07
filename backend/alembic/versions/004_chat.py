"""add chat is_favorite and status

Revision ID: 004_chat
Revises: 003_add_source_url_documents
Create Date: 2026-07-03 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '004_chat'
down_revision: Union[str, None] = '003_add_source_url_documents'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update chat_mode enum to include 'website'
    op.execute("ALTER TYPE chat_mode ADD VALUE IF NOT EXISTS 'website'")
    
    # 2. Create chat_status enum
    chat_status = postgresql.ENUM('active', 'generating', 'failed', 'completed', name='chat_status')
    chat_status.create(op.get_bind(), checkfirst=True)

    # 3. Add columns to chats
    op.add_column('chats', sa.Column('is_favorite', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('chats', sa.Column('status', chat_status, server_default='completed', nullable=False))


def downgrade() -> None:
    op.drop_column('chats', 'status')
    op.drop_column('chats', 'is_favorite')
    op.execute("DROP TYPE IF EXISTS chat_status")
    # Note: postgres doesn't support dropping enum values easily, so we leave 'website' in chat_mode
