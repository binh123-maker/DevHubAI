"""add document kanban status

Revision ID: 005_add_document_kanban_status
Revises: b8bbf963889e
Create Date: 2026-07-26 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '005_add_document_kanban_status'
down_revision: Union[str, None] = 'b8bbf963889e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    kanban_enum = postgresql.ENUM('new', 'learning', 'completed', 'archived', name='kanban_status')
    kanban_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'documents',
        sa.Column(
            'kanban_status',
            sa.Enum('new', 'learning', 'completed', 'archived', name='kanban_status'),
            server_default='new',
            nullable=False,
        )
    )
    op.add_column(
        'documents',
        sa.Column(
            'kanban_updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        )
    )


def downgrade() -> None:
    op.drop_column('documents', 'kanban_updated_at')
    op.drop_column('documents', 'kanban_status')
    kanban_enum = postgresql.ENUM('new', 'learning', 'completed', 'archived', name='kanban_status')
    kanban_enum.drop(op.get_bind(), checkfirst=True)
