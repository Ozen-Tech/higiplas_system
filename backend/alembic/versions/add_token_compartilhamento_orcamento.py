"""add token_compartilhamento to orcamentos

Revision ID: add_token_orcamento_001
Revises: preco_cliente_produto_001
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_token_orcamento_001'
down_revision: Union[str, Sequence[str], None] = 'preco_cliente_produto_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Adicionar coluna token_compartilhamento à tabela orcamentos
    op.add_column('orcamentos', 
        sa.Column('token_compartilhamento', sa.String(), nullable=True)
    )
    # Criar índice único para o token
    op.create_index('ix_orcamentos_token_compartilhamento', 'orcamentos', ['token_compartilhamento'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Remover índice
    op.drop_index('ix_orcamentos_token_compartilhamento', table_name='orcamentos')
    # Remover coluna
    op.drop_column('orcamentos', 'token_compartilhamento')

