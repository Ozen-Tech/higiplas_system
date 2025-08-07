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
    
    # Comentamos a criação das tabelas que já existem.
    # op.create_table('empresas', ...)
    # op.create_table('usuarios', ...)
    # op.create_table('produtos', ...) # Também comentado, pois só queremos alterá-la
    # op.create_table('vendas_historicas', ...)
    
    # 1. Cria as tabelas realmente NOVAS
    op.create_table('fornecedores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('cnpj', sa.String(), nullable=True),
        sa.Column('contato_email', sa.String(), nullable=True),
        sa.Column('contato_telefone', sa.String(), nullable=True),
        sa.Column('empresa_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fornecedores_id'), 'fornecedores', ['id'], unique=False)
    op.create_index(op.f('ix_fornecedores_nome'), 'fornecedores', ['nome'], unique=True)
    
    op.create_table('ordens_compra',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fornecedor_id', sa.Integer(), nullable=True),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('data_criacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('data_recebimento', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['fornecedor_id'], ['fornecedores.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ordens_compra_id'), 'ordens_compra', ['id'], unique=False)

    # Precisamos criar ordens_compra ANTES que produtos tente criar uma FK para ela. 
    # E produtos precisa existir antes de ordens_compra_itens. A ordem importa.
    # Primeiro, apenas adicionamos a coluna a 'produtos'.
    op.add_column('produtos', sa.Column('fornecedor_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_produtos_fornecedores_fornecedor_id', 'produtos', 'fornecedores', ['fornecedor_id'], ['id'])
    
    op.create_table('ordens_compra_itens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ordem_id', sa.Integer(), nullable=True),
        sa.Column('produto_id', sa.Integer(), nullable=True),
        sa.Column('quantidade_solicitada', sa.Integer(), nullable=False),
        sa.Column('custo_unitario_registrado', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['ordem_id'], ['ordens_compra.id'], ),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ordens_compra_itens_id'), 'ordens_compra_itens', ['id'], unique=False)

    # 2. Comenta a criação de TODOS os índices que já existem
    # op.create_index(op.f('ix_empresas_cnpj'), 'empresas', ['cnpj'], unique=True)
    # op.create_index(op.f('ix_empresas_id'), 'empresas', ['id'], unique=False)
    # op.create_index(op.f('ix_empresas_nome'), 'empresas', ['nome'], unique=True)
    # op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True)
    # op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)
    # op.create_index(op.f('ix_usuarios_nome'), 'usuarios', ['nome'], unique=False)
    # op.create_index(op.f('ix_produtos_categoria'), 'produtos', ['categoria'], unique=False)
    # op.create_index(op.f('ix_produtos_codigo'), 'produtos', ['codigo'], unique=True)
    # op.create_index(op.f('ix_produtos_id'), 'produtos', ['id'], unique=False)
    # op.create_index(op.f('ix_produtos_nome'), 'produtos', ['nome'], unique=False)
    
    # ### end Alembic commands ###


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