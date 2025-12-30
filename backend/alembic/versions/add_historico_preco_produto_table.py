"""add historico_preco_produto table

Revision ID: add_historico_preco_produto
Revises: preco_cliente_produto_001
Create Date: 2025-01-29

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_historico_preco_produto'
down_revision = 'preco_cliente_produto_001'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela historico_preco_produto se não existir
    op.execute("""
        CREATE TABLE IF NOT EXISTS historico_preco_produto (
            id SERIAL PRIMARY KEY,
            produto_id INTEGER NOT NULL REFERENCES produtos(id),
            preco_unitario FLOAT NOT NULL,
            quantidade FLOAT NOT NULL,
            valor_total FLOAT NOT NULL,
            nota_fiscal VARCHAR,
            data_venda TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            empresa_id INTEGER NOT NULL REFERENCES empresas(id),
            cliente_id INTEGER REFERENCES clientes(id),
            data_criacao TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_produto_id 
            ON historico_preco_produto(produto_id);
        CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_nota_fiscal 
            ON historico_preco_produto(nota_fiscal);
        CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_data_venda 
            ON historico_preco_produto(data_venda);
        CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_empresa_id 
            ON historico_preco_produto(empresa_id);
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS historico_preco_produto CASCADE;")

