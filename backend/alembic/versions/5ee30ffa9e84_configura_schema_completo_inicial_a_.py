"""Configura schema completo inicial a partir dos modelos

Revision ID: 5ee30ffa9e84
Revises: 
Create Date: 2025-08-07 01:38:57.347229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ee30ffa9e84'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### Comandos Modificados Manualmente para Deploy em Produção ###
    
    # --- As tabelas 'fornecedores', 'ordens_compra' e 'ordens_compra_itens' PARECEM já existir no DB ---
    # --- Vamos comentar a criação delas também para sermos 100% seguros ---

    # op.create_table('fornecedores', ... ) # <-- COMENTADO
    # op.create_index(op.f('ix_fornecedores_id'), 'fornecedores', ['id'], unique=False) # <-- COMENTADO
    # op.create_index(op.f('ix_fornecedores_nome'), 'fornecedores', ['nome'], unique=True) # <-- COMENTADO
    
    # op.create_table('ordens_compra', ... ) # <-- COMENTADO (Por segurança)
    # op.create_index(op.f('ix_ordens_compra_id'), 'ordens_compra', ['id'], unique=False) # <-- COMENTADO
    
    # op.create_table('ordens_compra_itens', ... ) # <-- COMENTADO (Por segurança)
    # op.create_index(op.f('ix_ordens_compra_itens_id'), 'ordens_compra_itens', ['id'], unique=False) # <-- COMENTADO


    # A ÚNICA ALTERAÇÃO REAL QUE PRECISAMOS APLICAR É ESTA:
    # Adicionar a coluna que falta na tabela 'produtos' existente.
    op.add_column('produtos', sa.Column('fornecedor_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_produtos_fornecedores_on_fornecedor_id', # Nome explícito para a constraint
        'produtos', 
        'fornecedores', 
        ['fornecedor_id'], 
        ['id']
    )

    # Vamos tentar garantir que os índices existam. `exist_ok=True` previne erros se eles já foram criados.
    op.create_index(op.f('ix_empresas_cnpj'), 'empresas', ['cnpj'], unique=True, exist_ok=True)
    op.create_index(op.f('ix_empresas_id'), 'empresas', ['id'], unique=False, exist_ok=True)
    op.create_index(op.f('ix_empresas_nome'), 'empresas', ['nome'], unique=True, exist_ok=True)
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True, exist_ok=True)
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False, exist_ok=True)
    op.create_index(op.f('ix_usuarios_nome'), 'usuarios', ['nome'], unique=False, exist_ok=True)
    op.create_index(op.f('ix_produtos_categoria'), 'produtos', ['categoria'], unique=False, exist_ok=True)
    op.create_index(op.f('ix_produtos_codigo'), 'produtos', ['codigo'], unique=True, exist_ok=True)
    op.create_index(op.f('ix_produtos_id'), 'produtos', ['id'], unique=False, exist_ok=True)
    op.create_index(op.f('ix_produtos_nome'), 'produtos', ['nome'], unique=False, exist_ok=True)


def downgrade() -> None:
    """Downgrade schema."""
    # ### Comandos Modificados Manualmente para Deploy em Produção ###

    # 1. Remove a coluna e a chave estrangeira da tabela 'produtos'.
    op.drop_constraint('fk_produtos_fornecedores_fornecedor_id', 'produtos', type_='foreignkey')
    op.drop_column('produtos', 'fornecedor_id')

    # 2. Remove as tabelas novas.
    #op.drop_index(op.f('ix_ordens_compra_itens_id'), table_name='ordens_compra_itens')
    #op.drop_table('ordens_compra_itens')
    #op.drop_index(op.f('ix_ordens_compra_id'), table_name='ordens_compra')
    #op.drop_table('ordens_compra')
    #op.drop_index(op.f('ix_fornecedores_nome'), table_name='fornecedores')
    #op.drop_index(op.f('ix_fornecedores_id'), table_name='fornecedores')
    #op.drop_table('fornecedores')

    # NÃO iremos remover as tabelas antigas que já existiam, por segurança.
    # ### end Alembic commands ###