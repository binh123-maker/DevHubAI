"""add source_url to documents

Revision ID: 003_add_source_url_documents
Revises: 002_add_icon_color_folders
Create Date: 2026-07-03 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_add_source_url_documents'
down_revision: Union[str, None] = '002_add_icon_color_folders'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add source_url column to documents
    op.add_column('documents', sa.Column('source_url', sa.String(length=2000), nullable=True))


def downgrade() -> None:
    op.drop_column('documents', 'source_url')
