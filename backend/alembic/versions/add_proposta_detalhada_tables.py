"""add_proposta_detalhada_tables

Revision ID: add_proposta_detalhada
Revises: add_historico_vendas_cliente
Create Date: 2025-01-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'add_proposta_detalhada'
down_revision: Union[str, Sequence[str], None] = 'add_historico_vendas_cliente'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Criar tabela fichas_tecnicas
    op.create_table(
        'fichas_tecnicas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('produto_id', sa.Integer(), nullable=True),
        sa.Column('nome_produto', sa.String(), nullable=False),
        sa.Column('dilucao_recomendada', sa.String(), nullable=True),
        sa.Column('dilucao_numerador', sa.Float(), nullable=True),
        sa.Column('dilucao_denominador', sa.Float(), nullable=True),
        sa.Column('rendimento_litro', sa.Float(), nullable=True),
        sa.Column('modo_uso', sa.String(), nullable=True),
        sa.Column('arquivo_pdf_path', sa.String(), nullable=True),
        sa.Column('observacoes', sa.String(), nullable=True),
        sa.Column('data_atualizacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('data_criacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices para fichas_tecnicas
    op.create_index(op.f('ix_fichas_tecnicas_produto_id'), 'fichas_tecnicas', ['produto_id'], unique=False)
    op.create_index(op.f('ix_fichas_tecnicas_nome_produto'), 'fichas_tecnicas', ['nome_produto'], unique=False)
    op.create_index('idx_ficha_produto', 'fichas_tecnicas', ['produto_id'], unique=False)
    op.create_index('idx_ficha_nome', 'fichas_tecnicas', ['nome_produto'], unique=False)
    
    # Criar tabela produtos_concorrentes
    op.create_table(
        'produtos_concorrentes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('marca', sa.String(), nullable=True),
        sa.Column('preco_medio', sa.Float(), nullable=True),
        sa.Column('rendimento_litro', sa.Float(), nullable=True),
        sa.Column('dilucao', sa.String(), nullable=True),
        sa.Column('dilucao_numerador', sa.Float(), nullable=True),
        sa.Column('dilucao_denominador', sa.Float(), nullable=True),
        sa.Column('categoria', sa.String(), nullable=True),
        sa.Column('observacoes', sa.String(), nullable=True),
        sa.Column('ativo', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('data_criacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('data_atualizacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices para produtos_concorrentes
    op.create_index(op.f('ix_produtos_concorrentes_nome'), 'produtos_concorrentes', ['nome'], unique=False)
    op.create_index(op.f('ix_produtos_concorrentes_categoria'), 'produtos_concorrentes', ['categoria'], unique=False)
    op.create_index('idx_concorrente_categoria', 'produtos_concorrentes', ['categoria'], unique=False)
    op.create_index('idx_concorrente_ativo', 'produtos_concorrentes', ['ativo'], unique=False)
    
    # Criar tabela propostas_detalhadas
    op.create_table(
        'propostas_detalhadas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('orcamento_id', sa.Integer(), nullable=True),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('vendedor_id', sa.Integer(), nullable=False),
        sa.Column('produto_id', sa.Integer(), nullable=False),
        sa.Column('ficha_tecnica_id', sa.Integer(), nullable=True),
        sa.Column('quantidade_produto', sa.Float(), nullable=False),
        sa.Column('dilucao_aplicada', sa.String(), nullable=True),
        sa.Column('dilucao_numerador', sa.Float(), nullable=True),
        sa.Column('dilucao_denominador', sa.Float(), nullable=True),
        sa.Column('rendimento_total_litros', sa.Float(), nullable=True),
        sa.Column('preco_produto', sa.Float(), nullable=True),
        sa.Column('custo_por_litro_final', sa.Float(), nullable=True),
        sa.Column('concorrente_id', sa.Integer(), nullable=True),
        sa.Column('economia_vs_concorrente', sa.Float(), nullable=True),
        sa.Column('economia_percentual', sa.Float(), nullable=True),
        sa.Column('economia_valor', sa.Float(), nullable=True),
        sa.Column('observacoes', sa.String(), nullable=True),
        sa.Column('compartilhavel', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.Column('token_compartilhamento', sa.String(), nullable=True),
        sa.Column('data_criacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('data_atualizacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['orcamento_id'], ['orcamentos.id'], ),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
        sa.ForeignKeyConstraint(['vendedor_id'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ),
        sa.ForeignKeyConstraint(['ficha_tecnica_id'], ['fichas_tecnicas.id'], ),
        sa.ForeignKeyConstraint(['concorrente_id'], ['produtos_concorrentes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_compartilhamento')
    )
    
    # Criar índices para propostas_detalhadas
    op.create_index(op.f('ix_propostas_detalhadas_orcamento_id'), 'propostas_detalhadas', ['orcamento_id'], unique=False)
    op.create_index(op.f('ix_propostas_detalhadas_cliente_id'), 'propostas_detalhadas', ['cliente_id'], unique=False)
    op.create_index(op.f('ix_propostas_detalhadas_vendedor_id'), 'propostas_detalhadas', ['vendedor_id'], unique=False)
    op.create_index(op.f('ix_propostas_detalhadas_produto_id'), 'propostas_detalhadas', ['produto_id'], unique=False)
    op.create_index(op.f('ix_propostas_detalhadas_token_compartilhamento'), 'propostas_detalhadas', ['token_compartilhamento'], unique=False)
    op.create_index(op.f('ix_propostas_detalhadas_data_criacao'), 'propostas_detalhadas', ['data_criacao'], unique=False)
    op.create_index('idx_proposta_vendedor_cliente', 'propostas_detalhadas', ['vendedor_id', 'cliente_id'], unique=False)
    op.create_index('idx_proposta_produto', 'propostas_detalhadas', ['produto_id'], unique=False)
    op.create_index('idx_proposta_data', 'propostas_detalhadas', ['data_criacao'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remover índices de propostas_detalhadas
    op.drop_index('idx_proposta_data', table_name='propostas_detalhadas')
    op.drop_index('idx_proposta_produto', table_name='propostas_detalhadas')
    op.drop_index('idx_proposta_vendedor_cliente', table_name='propostas_detalhadas')
    op.drop_index(op.f('ix_propostas_detalhadas_data_criacao'), table_name='propostas_detalhadas')
    op.drop_index(op.f('ix_propostas_detalhadas_token_compartilhamento'), table_name='propostas_detalhadas')
    op.drop_index(op.f('ix_propostas_detalhadas_produto_id'), table_name='propostas_detalhadas')
    op.drop_index(op.f('ix_propostas_detalhadas_vendedor_id'), table_name='propostas_detalhadas')
    op.drop_index(op.f('ix_propostas_detalhadas_cliente_id'), table_name='propostas_detalhadas')
    op.drop_index(op.f('ix_propostas_detalhadas_orcamento_id'), table_name='propostas_detalhadas')
    
    # Remover tabela propostas_detalhadas
    op.drop_table('propostas_detalhadas')
    
    # Remover índices de produtos_concorrentes
    op.drop_index('idx_concorrente_ativo', table_name='produtos_concorrentes')
    op.drop_index('idx_concorrente_categoria', table_name='produtos_concorrentes')
    op.drop_index(op.f('ix_produtos_concorrentes_categoria'), table_name='produtos_concorrentes')
    op.drop_index(op.f('ix_produtos_concorrentes_nome'), table_name='produtos_concorrentes')
    
    # Remover tabela produtos_concorrentes
    op.drop_table('produtos_concorrentes')
    
    # Remover índices de fichas_tecnicas
    op.drop_index('idx_ficha_nome', table_name='fichas_tecnicas')
    op.drop_index('idx_ficha_produto', table_name='fichas_tecnicas')
    op.drop_index(op.f('ix_fichas_tecnicas_nome_produto'), table_name='fichas_tecnicas')
    op.drop_index(op.f('ix_fichas_tecnicas_produto_id'), table_name='fichas_tecnicas')
    
    # Remover tabela fichas_tecnicas
    op.drop_table('fichas_tecnicas')

