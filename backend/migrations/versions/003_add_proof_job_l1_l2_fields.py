"""Add L2/L1 verification fields to proof_jobs

Revision ID: 003
Revises: 002
Create Date: 2025-12-12 02:30:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('proof_jobs', sa.Column('l2_fact_hash', sa.String(), nullable=True))
    op.add_column('proof_jobs', sa.Column('l2_verified_at', sa.DateTime(), nullable=True))
    op.add_column('proof_jobs', sa.Column('l2_block_number', sa.Integer(), nullable=True))
    op.add_column('proof_jobs', sa.Column('l1_settlement_enabled', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('proof_jobs', sa.Column('atlantic_query_id', sa.String(), nullable=True))
    op.add_column('proof_jobs', sa.Column('l1_fact_hash', sa.String(), nullable=True))
    op.add_column('proof_jobs', sa.Column('l1_verified_at', sa.DateTime(), nullable=True))
    op.add_column('proof_jobs', sa.Column('l1_block_number', sa.Integer(), nullable=True))
    op.add_column('proof_jobs', sa.Column('network', sa.String(), nullable=True, server_default='sepolia'))

    op.create_index('ix_proof_jobs_l2_fact_hash', 'proof_jobs', ['l2_fact_hash'])
    op.create_index('ix_proof_jobs_l1_settlement_enabled', 'proof_jobs', ['l1_settlement_enabled'])
    op.create_index('ix_proof_jobs_atlantic_query_id', 'proof_jobs', ['atlantic_query_id'])
    op.create_index('ix_proof_jobs_l1_fact_hash', 'proof_jobs', ['l1_fact_hash'])
    op.create_index('ix_proof_jobs_network', 'proof_jobs', ['network'])


def downgrade() -> None:
    op.drop_index('ix_proof_jobs_network', table_name='proof_jobs')
    op.drop_index('ix_proof_jobs_l1_fact_hash', table_name='proof_jobs')
    op.drop_index('ix_proof_jobs_atlantic_query_id', table_name='proof_jobs')
    op.drop_index('ix_proof_jobs_l1_settlement_enabled', table_name='proof_jobs')
    op.drop_index('ix_proof_jobs_l2_fact_hash', table_name='proof_jobs')

    op.drop_column('proof_jobs', 'network')
    op.drop_column('proof_jobs', 'l1_block_number')
    op.drop_column('proof_jobs', 'l1_verified_at')
    op.drop_column('proof_jobs', 'l1_fact_hash')
    op.drop_column('proof_jobs', 'atlantic_query_id')
    op.drop_column('proof_jobs', 'l1_settlement_enabled')
    op.drop_column('proof_jobs', 'l2_block_number')
    op.drop_column('proof_jobs', 'l2_verified_at')
    op.drop_column('proof_jobs', 'l2_fact_hash')
