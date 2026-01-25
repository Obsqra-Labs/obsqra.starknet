"""Add proof_source column to proof_jobs

Revision ID: 004
Revises: 003
Create Date: 2026-01-26 01:40:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('proof_jobs', sa.Column('proof_source', sa.String(), nullable=True))
    op.create_index('ix_proof_jobs_proof_source', 'proof_jobs', ['proof_source'])


def downgrade() -> None:
    op.drop_index('ix_proof_jobs_proof_source', table_name='proof_jobs')
    op.drop_column('proof_jobs', 'proof_source')
