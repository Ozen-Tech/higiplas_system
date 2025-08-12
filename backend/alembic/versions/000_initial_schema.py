"""Create initial schema

Revision ID: 000_initial_schema
Revises: 
Create Date: 2025-01-11 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '000_initial_schema'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from alembic import context
    
    # Get connection to check if tables exist
    connection = context.get_bind()
    
    # Check if empresas table exists
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'empresas')"
    ))
    empresas_exists = result.scalar()
    
    if not empresas_exists:
        # Create empresas table
        op.create_table('empresas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=True),
        sa.Column('cnpj', sa.String(), nullable=True),
        sa.Column('data_criacao', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_empresas_cnpj'), 'empresas', ['cnpj'], unique=True)
        op.create_index(op.f('ix_empresas_id'), 'empresas', ['id'], unique=False)
        op.create_index(op.f('ix_empresas_nome'), 'empresas', ['nome'], unique=True)
    
    # Check if usuarios table exists
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'usuarios')"
    ))
    usuarios_exists = result.scalar()
    
    if not usuarios_exists:
        # Create usuarios table
        op.create_table('usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('empresa_id', sa.Integer(), nullable=True),
        sa.Column('perfil', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('xp', sa.Integer(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('data_criacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True)
        op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)
        op.create_index(op.f('ix_usuarios_nome'), 'usuarios', ['nome'], unique=False)
    
    # Create fornecedores table if not exists
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'fornecedores')"
    ))
    fornecedores_exists = result.scalar()
    if not fornecedores_exists:
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
    
    # Create produtos table if not exists
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'produtos')"
    ))
    produtos_exists = result.scalar()
    if not produtos_exists:
        op.create_table('produtos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=True),
        sa.Column('codigo', sa.String(), nullable=True),
        sa.Column('categoria', sa.String(), nullable=True),
        sa.Column('descricao', sa.String(), nullable=True),
        sa.Column('preco_custo', sa.Float(), nullable=True),
        sa.Column('preco_venda', sa.Float(), nullable=True),
        sa.Column('unidade_medida', sa.String(), nullable=True),
        sa.Column('estoque_minimo', sa.Integer(), nullable=True),
        sa.Column('data_validade', sa.Date(), nullable=True),
        sa.Column('quantidade_em_estoque', sa.Integer(), nullable=True),
        sa.Column('empresa_id', sa.Integer(), nullable=True),
        sa.Column('fornecedor_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
        sa.ForeignKeyConstraint(['fornecedor_id'], ['fornecedores.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_produtos_categoria'), 'produtos', ['categoria'], unique=False)
        op.create_index(op.f('ix_produtos_codigo'), 'produtos', ['codigo'], unique=True)
        op.create_index(op.f('ix_produtos_id'), 'produtos', ['id'], unique=False)
        op.create_index(op.f('ix_produtos_nome'), 'produtos', ['nome'], unique=False)
    
    # Create vendas_historicas table if not exists
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'vendas_historicas')"
    ))
    vendas_historicas_exists = result.scalar()
    if not vendas_historicas_exists:
        op.create_table('vendas_historicas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ident_antigo', sa.Integer(), nullable=True),
        sa.Column('descricao', sa.String(), nullable=True),
        sa.Column('quantidade_vendida_total', sa.Float(), nullable=True),
        sa.Column('custo_compra_total', sa.Float(), nullable=True),
        sa.Column('valor_vendido_total', sa.Float(), nullable=True),
        sa.Column('lucro_bruto_total', sa.Float(), nullable=True),
        sa.Column('margem_lucro_percentual', sa.Float(), nullable=True),
        sa.Column('produto_atual_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['produto_atual_id'], ['produtos.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_vendas_historicas_descricao'), 'vendas_historicas', ['descricao'], unique=False)
        op.create_index(op.f('ix_vendas_historicas_ident_antigo'), 'vendas_historicas', ['ident_antigo'], unique=True)
        op.create_index(op.f('ix_vendas_historicas_id'), 'vendas_historicas', ['id'], unique=False)
    
    # Create movimentacoes_estoque table if not exists
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'movimentacoes_estoque')"
    ))
    mov_estoque_exists = result.scalar()
    if not mov_estoque_exists:
        op.create_table('movimentacoes_estoque',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('produto_id', sa.Integer(), nullable=True),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('tipo_movimentacao', sa.Enum('ENTRADA', 'SAIDA', name='tipomovimentacao'), nullable=True),
        sa.Column('quantidade', sa.Integer(), nullable=True),
        sa.Column('motivo', sa.String(), nullable=True),
        sa.Column('data_movimentacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_movimentacoes_estoque_id'), 'movimentacoes_estoque', ['id'], unique=False)
    
    # Create clientes table with enums
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE empresa_vinculada_enum AS ENUM ('HIGIPLAS', 'HIGITEC');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE status_pagamento_enum AS ENUM ('BOM_PAGADOR', 'MAU_PAGADOR');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.create_table('clientes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('razao_social', sa.String(), nullable=False),
    sa.Column('cnpj', sa.String(), nullable=True),
    sa.Column('endereco', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('telefone', sa.String(), nullable=True),
    sa.Column('empresa_vinculada', sa.Enum('HIGIPLAS', 'HIGITEC', name='empresa_vinculada_enum'), nullable=False),
    sa.Column('status_pagamento', sa.Enum('BOM_PAGADOR', 'MAU_PAGADOR', name='status_pagamento_enum'), nullable=True),
    sa.Column('data_criacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('empresa_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
    sa.PrimaryKeyConstraint('id')
        )
    op.create_index(op.f('ix_clientes_cnpj'), 'clientes', ['cnpj'], unique=True)
    op.create_index(op.f('ix_clientes_id'), 'clientes', ['id'], unique=False)
    op.create_index(op.f('ix_clientes_razao_social'), 'clientes', ['razao_social'], unique=False)
    
    # Create orcamentos table if not exists
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'orcamentos')"
    ))
    orcamentos_exists = result.scalar()
    if not orcamentos_exists:
        op.create_table('orcamentos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('numero_orcamento', sa.String(), nullable=True),
    sa.Column('data_criacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('data_validade', sa.Date(), nullable=True),
    sa.Column('valor_total', sa.Float(), nullable=True),
    sa.Column('status', sa.Enum('RASCUNHO', 'ENVIADO', 'APROVADO', 'REJEITADO', 'EXPIRADO', name='statusorcamento'), nullable=True),
    sa.Column('observacoes', sa.String(), nullable=True),
    sa.Column('condicao_pagamento', sa.String(), nullable=True),
    sa.Column('preco_minimo', sa.Float(), nullable=True),
    sa.Column('preco_maximo', sa.Float(), nullable=True),
    sa.Column('numero_nf', sa.String(), nullable=True),
    sa.Column('cliente_id', sa.Integer(), nullable=True),
    sa.Column('empresa_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
    sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orcamentos_id'), 'orcamentos', ['id'], unique=False)
    op.create_index(op.f('ix_orcamentos_numero_orcamento'), 'orcamentos', ['numero_orcamento'], unique=True)
    
    # Create historico_pagamentos table
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE status_pagamento_historico_enum AS ENUM ('PENDENTE', 'PAGO', 'ATRASADO');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'historico_pagamentos')"
    ))
    historico_pagamentos_exists = result.scalar()
    if not historico_pagamentos_exists:
        op.create_table('historico_pagamentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('valor', sa.Float(), nullable=False),
        sa.Column('data_vencimento', sa.Date(), nullable=False),
        sa.Column('data_pagamento', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('PENDENTE', 'PAGO', 'ATRASADO', name='status_pagamento_historico_enum'), nullable=True),
        sa.Column('numero_nf', sa.String(), nullable=True),
        sa.Column('observacoes', sa.String(), nullable=True),
        sa.Column('data_criacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('cliente_id', sa.Integer(), nullable=True),
        sa.Column('orcamento_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
        sa.ForeignKeyConstraint(['orcamento_id'], ['orcamentos.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_historico_pagamentos_id'), 'historico_pagamentos', ['id'], unique=False)
    
    # Create produtos_mais_vendidos table if not exists
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'produtos_mais_vendidos')"
    ))
    produtos_mais_vendidos_exists = result.scalar()
    if not produtos_mais_vendidos_exists:
        op.create_table('produtos_mais_vendidos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('produto_id', sa.Integer(), nullable=True),
        sa.Column('ano', sa.Integer(), nullable=False),
        sa.Column('quantidade_vendida', sa.Integer(), nullable=True),
        sa.Column('valor_total_vendido', sa.Float(), nullable=True),
        sa.Column('numero_vendas', sa.Integer(), nullable=True),
        sa.Column('ultima_atualizacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('empresa_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_produtos_mais_vendidos_id'), 'produtos_mais_vendidos', ['id'], unique=False)
    
    # Create ordens_compra table
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ordens_compra')"
    ))
    ordens_compra_exists = result.scalar()
    if not ordens_compra_exists:
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
    
    # Create ordens_compra_itens table
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ordens_compra_itens')"
    ))
    ordens_compra_itens_exists = result.scalar()
    if not ordens_compra_itens_exists:
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


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_ordens_compra_itens_id'), table_name='ordens_compra_itens')
    op.drop_table('ordens_compra_itens')
    op.drop_index(op.f('ix_ordens_compra_id'), table_name='ordens_compra')
    op.drop_table('ordens_compra')
    op.drop_index(op.f('ix_produtos_mais_vendidos_id'), table_name='produtos_mais_vendidos')
    op.drop_table('produtos_mais_vendidos')
    op.drop_index(op.f('ix_historico_pagamentos_id'), table_name='historico_pagamentos')
    op.drop_table('historico_pagamentos')
    op.execute("DROP TYPE status_pagamento_historico_enum")
    op.drop_index(op.f('ix_orcamentos_numero_orcamento'), table_name='orcamentos')
    op.drop_index(op.f('ix_orcamentos_id'), table_name='orcamentos')
    op.drop_table('orcamentos')
    op.drop_index(op.f('ix_clientes_razao_social'), table_name='clientes')
    op.drop_index(op.f('ix_clientes_id'), table_name='clientes')
    op.drop_index(op.f('ix_clientes_cnpj'), table_name='clientes')
    op.drop_table('clientes')
    op.execute("DROP TYPE status_pagamento_enum")
    op.execute("DROP TYPE empresa_vinculada_enum")
    op.drop_index(op.f('ix_movimentacoes_estoque_id'), table_name='movimentacoes_estoque')
    op.drop_table('movimentacoes_estoque')
    op.drop_index(op.f('ix_vendas_historicas_id'), table_name='vendas_historicas')
    op.drop_index(op.f('ix_vendas_historicas_ident_antigo'), table_name='vendas_historicas')
    op.drop_index(op.f('ix_vendas_historicas_descricao'), table_name='vendas_historicas')
    op.drop_table('vendas_historicas')
    op.drop_index(op.f('ix_produtos_nome'), table_name='produtos')
    op.drop_index(op.f('ix_produtos_id'), table_name='produtos')
    op.drop_index(op.f('ix_produtos_codigo'), table_name='produtos')
    op.drop_index(op.f('ix_produtos_categoria'), table_name='produtos')
    op.drop_table('produtos')
    op.drop_index(op.f('ix_fornecedores_nome'), table_name='fornecedores')
    op.drop_index(op.f('ix_fornecedores_id'), table_name='fornecedores')
    op.drop_table('fornecedores')
    op.drop_index(op.f('ix_usuarios_nome'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_id'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_email'), table_name='usuarios')
    op.drop_table('usuarios')
    op.drop_index(op.f('ix_empresas_nome'), table_name='empresas')
    op.drop_index(op.f('ix_empresas_id'), table_name='empresas')
    op.drop_index(op.f('ix_empresas_cnpj'), table_name='empresas')
    op.drop_table('empresas')