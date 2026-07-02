"""add icon and color to folders

Revision ID: 002_add_icon_color_folders
Revises: 001_initial_mvp_schema
Create Date: 2026-07-02 16:22:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_icon_color_folders'
down_revision: Union[str, None] = '001_initial_mvp_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add color and icon columns to folders with default values
    op.add_column('folders', sa.Column('color', sa.String(length=7), server_default='#3B82F6', nullable=False))
    op.add_column('folders', sa.Column('icon', sa.String(length=50), server_default='folder', nullable=False))


def downgrade() -> None:
    op.drop_column('folders', 'icon')
    op.drop_column('folders', 'color')
