"""create historico preco produto table

Revision ID: 20260121_historico_preco
Revises: merge_approval_fields_and_proposta
Create Date: 2026-01-21 03:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260121_historico_preco'
down_revision = 'merge_approval_proposta'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela historico_preco_produto se não existir
    op.execute("""
        CREATE TABLE IF NOT EXISTS historico_preco_produto (
            id SERIAL PRIMARY KEY,
            produto_id INTEGER NOT NULL REFERENCES produtos(id),
            preco_unitario DOUBLE PRECISION NOT NULL,
            quantidade DOUBLE PRECISION NOT NULL,
            valor_total DOUBLE PRECISION NOT NULL,
            nota_fiscal VARCHAR,
            data_venda TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            empresa_id INTEGER NOT NULL REFERENCES empresas(id),
            cliente_id INTEGER REFERENCES clientes(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Criar índices
    op.execute("CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_produto_id ON historico_preco_produto(produto_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_nota_fiscal ON historico_preco_produto(nota_fiscal);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_data_venda ON historico_preco_produto(data_venda);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_empresa_id ON historico_preco_produto(empresa_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_cliente_id ON historico_preco_produto(cliente_id);")


def downgrade():
    op.drop_table('historico_preco_produto')
