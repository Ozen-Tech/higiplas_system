"""add refresh tokens table

Revision ID: add_refresh_tokens
Revises: 227dac4b4f63
Create Date: 2025-01-21 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'add_refresh_tokens'
down_revision = '227dac4b4f63'
branch_labels = None
depends_on = None


def upgrade():
    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('revoked', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index('ix_refresh_tokens_id', 'refresh_tokens', ['id'])
    op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'], unique=True)
    op.create_index('ix_refresh_tokens_usuario_id', 'refresh_tokens', ['usuario_id'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_refresh_tokens_usuario_id', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_token', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_id', table_name='refresh_tokens')
    
    # Drop table
    op.drop_table('refresh_tokens')
