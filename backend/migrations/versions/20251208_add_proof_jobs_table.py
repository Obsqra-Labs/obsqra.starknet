"""Add proof_jobs table for SHARP verification tracking

Revision ID: 001
Revises: 
Create Date: 2025-12-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create proof_jobs table
    op.create_table(
        'proof_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tx_hash', sa.String(), nullable=True),
        sa.Column('proof_hash', sa.String(), nullable=False),
        sa.Column('sharp_job_id', sa.String(), nullable=True),
        sa.Column('fact_hash', sa.String(), nullable=True),
        sa.Column('status', sa.Enum(
            'GENERATING', 'GENERATED', 'SUBMITTED', 'VERIFYING', 'VERIFIED', 'FAILED', 'TIMEOUT',
            name='proofstatus'
        ), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('metrics', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('proof_data', sa.LargeBinary(), nullable=True),
        sa.Column('error', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for common queries
    op.create_index('ix_proof_jobs_tx_hash', 'proof_jobs', ['tx_hash'])
    op.create_index('ix_proof_jobs_proof_hash', 'proof_jobs', ['proof_hash'])
    op.create_index('ix_proof_jobs_sharp_job_id', 'proof_jobs', ['sharp_job_id'])
    op.create_index('ix_proof_jobs_status', 'proof_jobs', ['status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_proof_jobs_status', table_name='proof_jobs')
    op.drop_index('ix_proof_jobs_sharp_job_id', table_name='proof_jobs')
    op.drop_index('ix_proof_jobs_proof_hash', table_name='proof_jobs')
    op.drop_index('ix_proof_jobs_tx_hash', table_name='proof_jobs')
    
    # Drop table
    op.drop_table('proof_jobs')
    
    # Drop enum type
    sa.Enum(name='proofstatus').drop(op.get_bind(), checkfirst=False)

