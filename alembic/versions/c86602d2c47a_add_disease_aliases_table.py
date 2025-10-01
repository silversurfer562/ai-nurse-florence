"""add_disease_aliases_table

Revision ID: c86602d2c47a
Revises: 1f5df51a2c0f
Create Date: 2025-10-01 02:55:53.515823

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c86602d2c47a'
down_revision: Union[str, None] = '1f5df51a2c0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create disease_aliases table
    op.create_table(
        'disease_aliases',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('alias', sa.String(length=500), nullable=False),
        sa.Column('alias_display', sa.String(length=500), nullable=False),
        sa.Column('mondo_id', sa.String(length=100), nullable=False),
        sa.Column('canonical_name', sa.String(length=500), nullable=False),
        sa.Column('alias_type', sa.String(length=50), nullable=False),
        sa.Column('search_weight', sa.Integer(), nullable=False),
        sa.Column('is_preferred', sa.Boolean(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for fast lookups
    op.create_index('ix_disease_aliases_alias', 'disease_aliases', ['alias'])
    op.create_index('ix_disease_aliases_mondo_id', 'disease_aliases', ['mondo_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_disease_aliases_mondo_id', table_name='disease_aliases')
    op.drop_index('ix_disease_aliases_alias', table_name='disease_aliases')

    # Drop table
    op.drop_table('disease_aliases')
