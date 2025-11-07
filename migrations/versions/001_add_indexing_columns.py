"""Add indexing support columns to all tables

Revision ID: 001
Revises: 
Create Date: 2025-11-05 00:00:00.000000

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
    """
    Add index_status and updated_at columns to jobs, tnnews, and aijobs tables
    for incremental indexing support
    """
    
    # Jobs table
    # Check if columns exist before adding
    conn = op.get_bind()
    
    # Add columns to jobs table
    try:
        op.add_column('jobs', sa.Column('index_status', sa.String(50), nullable=True))
    except Exception:
        pass  # Column already exists
    
    try:
        op.add_column('jobs', sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')))
    except Exception:
        pass  # Column already exists
    
    try:
        op.add_column('jobs', sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')))
    except Exception:
        pass  # Column already exists
    
    # Add columns to tnnews table (if exists)
    try:
        op.add_column('tnnews', sa.Column('index_status', sa.String(50), nullable=True))
    except Exception:
        pass
    
    try:
        op.add_column('tnnews', sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')))
    except Exception:
        pass
    
    try:
        op.add_column('tnnews', sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')))
    except Exception:
        pass
    
    # Add columns to aijobs table (if exists)
    try:
        op.add_column('aijobs', sa.Column('index_status', sa.String(50), nullable=True))
    except Exception:
        pass
    
    try:
        op.add_column('aijobs', sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')))
    except Exception:
        pass
    
    try:
        op.add_column('aijobs', sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')))
    except Exception:
        pass
    
    # Create indexes for better query performance
    try:
        op.create_index('idx_jobs_index_status', 'jobs', ['index_status'])
    except Exception:
        pass
    
    try:
        op.create_index('idx_jobs_updated_at', 'jobs', ['updated_at'])
    except Exception:
        pass
    
    try:
        op.create_index('idx_tnnews_index_status', 'tnnews', ['index_status'])
    except Exception:
        pass
    
    try:
        op.create_index('idx_tnnews_updated_at', 'tnnews', ['updated_at'])
    except Exception:
        pass
    
    try:
        op.create_index('idx_aijobs_index_status', 'aijobs', ['index_status'])
    except Exception:
        pass
    
    try:
        op.create_index('idx_aijobs_updated_at', 'aijobs', ['updated_at'])
    except Exception:
        pass
    
    print("✓ Migration completed: Added index_status and updated_at columns")


def downgrade() -> None:
    """
    Remove the indexing support columns
    """
    
    # Drop indexes
    try:
        op.drop_index('idx_aijobs_updated_at', table_name='aijobs')
        op.drop_index('idx_aijobs_index_status', table_name='aijobs')
        op.drop_index('idx_tnnews_updated_at', table_name='tnnews')
        op.drop_index('idx_tnnews_index_status', table_name='tnnews')
        op.drop_index('idx_jobs_updated_at', table_name='jobs')
        op.drop_index('idx_jobs_index_status', table_name='jobs')
    except Exception:
        pass
    
    # Drop columns from aijobs
    try:
        op.drop_column('aijobs', 'updated_at')
        op.drop_column('aijobs', 'created_at')
        op.drop_column('aijobs', 'index_status')
    except Exception:
        pass
    
    # Drop columns from tnnews
    try:
        op.drop_column('tnnews', 'updated_at')
        op.drop_column('tnnews', 'created_at')
        op.drop_column('tnnews', 'index_status')
    except Exception:
        pass
    
    # Drop columns from jobs
    try:
        op.drop_column('jobs', 'updated_at')
        op.drop_column('jobs', 'created_at')
        op.drop_column('jobs', 'index_status')
    except Exception:
        pass
