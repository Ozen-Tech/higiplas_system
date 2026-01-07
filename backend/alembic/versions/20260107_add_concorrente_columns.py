"""Adiciona colunas faltantes de concorrente na tabela propostas_detalhadas_itens

Revision ID: add_concorrente_columns
Revises: proposta_itens_concorrentes
Create Date: 2026-01-07 11:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_concorrente_columns"
down_revision: Union[str, Sequence[str], None] = "proposta_itens_concorrentes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona colunas de concorrente faltantes."""
    # Verificar se as colunas já existem antes de adicionar
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('propostas_detalhadas_itens')]
    
    if 'concorrente_quantidade' not in columns:
        op.add_column('propostas_detalhadas_itens', 
                     sa.Column('concorrente_quantidade', sa.Float(), nullable=True))
    
    if 'concorrente_dilucao_numerador' not in columns:
        op.add_column('propostas_detalhadas_itens', 
                     sa.Column('concorrente_dilucao_numerador', sa.Float(), nullable=True))
    
    if 'concorrente_dilucao_denominador' not in columns:
        op.add_column('propostas_detalhadas_itens', 
                     sa.Column('concorrente_dilucao_denominador', sa.Float(), nullable=True))


def downgrade() -> None:
    """Remove colunas de concorrente."""
    op.drop_column('propostas_detalhadas_itens', 'concorrente_dilucao_denominador')
    op.drop_column('propostas_detalhadas_itens', 'concorrente_dilucao_numerador')
    op.drop_column('propostas_detalhadas_itens', 'concorrente_quantidade')

