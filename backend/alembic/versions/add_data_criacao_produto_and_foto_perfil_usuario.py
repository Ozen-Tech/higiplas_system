"""add data_criacao to produtos and foto_perfil to usuarios

Revision ID: add_data_criacao_foto_perfil_001
Revises: add_token_orcamento_001
Create Date: 2025-12-03 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_data_criacao_foto_perfil_001'
down_revision: Union[str, Sequence[str], None] = 'add_token_orcamento_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Adicionar coluna data_criacao à tabela produtos
    op.add_column('produtos', 
        sa.Column('data_criacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True)
    )
    
    # Adicionar coluna foto_perfil à tabela usuarios
    op.add_column('usuarios', 
        sa.Column('foto_perfil', sa.String(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remover coluna foto_perfil
    op.drop_column('usuarios', 'foto_perfil')
    # Remover coluna data_criacao
    op.drop_column('produtos', 'data_criacao')


