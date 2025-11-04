"""Add KPI models for dashboard

Revision ID: 001_add_kpi_models
Revises: 
Create Date: 2025-11-03 22:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_kpi_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create kpi_metrics table
    op.create_table(
        'kpi_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kpi_id', sa.String(50), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('target', sa.Float(), nullable=False),
        sa.Column('threshold_warning', sa.Float(), nullable=False),
        sa.Column('threshold_critical', sa.Float(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('period', sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for kpi_metrics
    op.create_index('idx_kpi_metrics_project_id', 'kpi_metrics', ['project_id'])
    op.create_index('idx_kpi_metrics_kpi_id', 'kpi_metrics', ['kpi_id'])
    op.create_index('idx_kpi_metrics_recorded_at', 'kpi_metrics', ['recorded_at'])
    op.create_index('idx_kpi_metrics_project_kpi', 'kpi_metrics', ['project_id', 'kpi_id'])
    
    # Create kpi_history table
    op.create_table(
        'kpi_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kpi_id', sa.String(50), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('target', sa.Float(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for kpi_history
    op.create_index('idx_kpi_history_project_id', 'kpi_history', ['project_id'])
    op.create_index('idx_kpi_history_kpi_id', 'kpi_history', ['kpi_id'])
    op.create_index('idx_kpi_history_recorded_at', 'kpi_history', ['recorded_at'])
    op.create_index('idx_kpi_history_project_kpi_date', 'kpi_history', ['project_id', 'kpi_id', 'recorded_at'])
    
    # Create dashboard_alerts table
    op.create_table(
        'dashboard_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kpi_id', sa.String(50), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('message', sa.String(500), nullable=False),
        sa.Column('acknowledged', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('acknowledged_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['acknowledged_by'], ['users.id'], ondelete='SET NULL'),
    )
    
    # Create indexes for dashboard_alerts
    op.create_index('idx_dashboard_alerts_kpi_id', 'dashboard_alerts', ['kpi_id'])
    op.create_index('idx_dashboard_alerts_acknowledged', 'dashboard_alerts', ['acknowledged'])
    op.create_index('idx_dashboard_alerts_created_at', 'dashboard_alerts', ['created_at'])
    op.create_index('idx_dashboard_alerts_kpi_acknowledged', 'dashboard_alerts', ['kpi_id', 'acknowledged'])


def downgrade() -> None:
    # Drop dashboard_alerts table and indexes
    op.drop_index('idx_dashboard_alerts_kpi_acknowledged', table_name='dashboard_alerts')
    op.drop_index('idx_dashboard_alerts_created_at', table_name='dashboard_alerts')
    op.drop_index('idx_dashboard_alerts_acknowledged', table_name='dashboard_alerts')
    op.drop_index('idx_dashboard_alerts_kpi_id', table_name='dashboard_alerts')
    op.drop_table('dashboard_alerts')
    
    # Drop kpi_history table and indexes
    op.drop_index('idx_kpi_history_project_kpi_date', table_name='kpi_history')
    op.drop_index('idx_kpi_history_recorded_at', table_name='kpi_history')
    op.drop_index('idx_kpi_history_kpi_id', table_name='kpi_history')
    op.drop_index('idx_kpi_history_project_id', table_name='kpi_history')
    op.drop_table('kpi_history')
    
    # Drop kpi_metrics table and indexes
    op.drop_index('idx_kpi_metrics_project_kpi', table_name='kpi_metrics')
    op.drop_index('idx_kpi_metrics_recorded_at', table_name='kpi_metrics')
    op.drop_index('idx_kpi_metrics_kpi_id', table_name='kpi_metrics')
    op.drop_index('idx_kpi_metrics_project_id', table_name='kpi_metrics')
    op.drop_table('kpi_metrics')
