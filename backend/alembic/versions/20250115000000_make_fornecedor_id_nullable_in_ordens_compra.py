"""make_fornecedor_id_nullable_in_ordens_compra

Revision ID: make_fornecedor_nullable
Revises: add_historico_vendas_cliente
Create Date: 2025-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'make_fornecedor_nullable'
down_revision: Union[str, Sequence[str], None] = 'add_historico_vendas_cliente'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Torna o campo fornecedor_id nullable na tabela ordens_compra"""
    # Verificar se a coluna existe e se não é nullable
    op.execute("""
        DO $$ 
        BEGIN
            -- Tornar a coluna nullable se ela existir e não for nullable
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'ordens_compra' 
                AND column_name = 'fornecedor_id'
                AND is_nullable = 'NO'
            ) THEN
                ALTER TABLE ordens_compra 
                ALTER COLUMN fornecedor_id DROP NOT NULL;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Reverte o campo fornecedor_id para NOT NULL (pode falhar se houver valores NULL)"""
    # ATENÇÃO: Isso pode falhar se houver ordens de compra com fornecedor_id NULL
    op.execute("""
        DO $$ 
        BEGIN
            -- Verificar se há valores NULL antes de tornar NOT NULL
            IF EXISTS (
                SELECT 1 
                FROM ordens_compra 
                WHERE fornecedor_id IS NULL
            ) THEN
                RAISE EXCEPTION 'Não é possível tornar fornecedor_id NOT NULL pois existem ordens de compra com fornecedor_id NULL. Atualize ou delete essas ordens primeiro.';
            END IF;
            
            -- Tornar a coluna NOT NULL se ela existir e for nullable
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'ordens_compra' 
                AND column_name = 'fornecedor_id'
                AND is_nullable = 'YES'
            ) THEN
                ALTER TABLE ordens_compra 
                ALTER COLUMN fornecedor_id SET NOT NULL;
            END IF;
        END $$;
    """)

