"""add_disease_ontology_and_collection_progress_tables

Revision ID: 1f5df51a2c0f
Revises: 3f5aacf09e0d
Create Date: 2025-09-30 00:34:21.679273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f5df51a2c0f'
down_revision: Union[str, None] = '3f5aacf09e0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create disease_ontology table for comprehensive disease storage with synonyms
    op.create_table(
        'disease_ontology',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('mondo_id', sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column('label', sa.String(length=500), nullable=False, index=True),
        sa.Column('synonyms', sa.JSON(), nullable=True),
        sa.Column('definition', sa.Text(), nullable=True),
        sa.Column('xrefs', sa.JSON(), nullable=True),
        sa.Column('snomed_code', sa.String(length=100), nullable=True, index=True),
        sa.Column('icd10_code', sa.String(length=100), nullable=True, index=True),
        sa.Column('icd11_code', sa.String(length=100), nullable=True, index=True),
        sa.Column('source', sa.String(length=100), nullable=False, default='mondo_api'),
        sa.Column('is_obsolete', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('last_verified_at', sa.DateTime(), nullable=True)
    )

    # Create disease_collection_progress table for tracking pagination
    op.create_table(
        'disease_collection_progress',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('total_fetched', sa.Integer(), nullable=False, default=0),
        sa.Column('current_offset', sa.Integer(), nullable=False, default=0),
        sa.Column('batch_size', sa.Integer(), nullable=False, default=1000),
        sa.Column('is_complete', sa.Boolean(), nullable=False, default=False),
        sa.Column('total_available', sa.Integer(), nullable=True),
        sa.Column('last_fetch_status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('last_error_message', sa.Text(), nullable=True),
        sa.Column('consecutive_errors', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('last_fetch_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('disease_collection_progress')
    op.drop_table('disease_ontology')
