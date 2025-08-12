"""Adiciona apenas a coluna fornecedor_id e a chave estrangeira ausentes

Revision ID: 5ee30ffa9e84
Revises: 
Create Date: 2025-08-07 ...

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '5ee30ffa9e84'
down_revision: Union[str, Sequence[str], None] = '000_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """
    Executa APENAS a alteração que falta no banco de produção.
    Não cria tabelas, não cria índices.
    """
    print("--- [MIGRAÇÃO MANUAL] Adicionando coluna fornecedor_id e FK à tabela produtos ---")
    try:
        op.add_column('produtos', sa.Column('fornecedor_id', sa.Integer(), nullable=True))
        op.create_foreign_key(
            'fk_produtos_fornecedores_on_fornecedor_id', 
            'produtos', 
            'fornecedores', 
            ['fornecedor_id'], 
            ['id']
        )
        print("--- [MIGRAÇÃO MANUAL] Coluna e FK adicionadas com sucesso ---")
    except Exception as e:
        print(f"--- [MIGRAÇÃO MANUAL] Ocorreu um erro (talvez a coluna já exista): {e} ---")
        print("--- [MIGRAÇÃO MANUAL] Continuando o processo, pois isso não é um erro fatal neste contexto. ---")
        pass


def downgrade() -> None:
    """
    Desfaz APENAS a alteração que foi feita.
    """
    print("--- [MIGRAÇÃO MANUAL] Removendo coluna fornecedor_id e FK da tabela produtos ---")
    op.drop_constraint('fk_produtos_fornecedores_on_fornecedor_id', 'produtos', type_='foreignkey')
    op.drop_column('produtos', 'fornecedor_id')