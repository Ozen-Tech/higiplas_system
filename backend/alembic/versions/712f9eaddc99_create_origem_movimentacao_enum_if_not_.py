"""create_origem_movimentacao_enum_if_not_exists

Revision ID: 712f9eaddc99
Revises: bffb357ac77f
Create Date: 2025-10-30 22:43:55.204475

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '712f9eaddc99'
down_revision: Union[str, Sequence[str], None] = 'bffb357ac77f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Criar o tipo ENUM se não existir
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE origem_movimentacao_enum AS ENUM (
                'VENDA',
                'DEVOLUCAO',
                'CORRECAO_MANUAL',
                'COMPRA',
                'AJUSTE',
                'OUTRO'
            );
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # Verificar se a coluna origem existe como VARCHAR e alterar seu tipo para o ENUM
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'movimentacoes_estoque'
                  AND column_name = 'origem'
                  AND (data_type = 'character varying' OR data_type = 'varchar')
            ) THEN
                -- Alterar o tipo da coluna para o enum, fazendo cast dos valores existentes
                ALTER TABLE movimentacoes_estoque
                ALTER COLUMN origem TYPE origem_movimentacao_enum
                USING origem::origem_movimentacao_enum;
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                -- Se ocorrer qualquer erro, não interromper a migração aqui.
                -- Possíveis causas: valores existentes incompatíveis com o enum.
                RAISE NOTICE 'Não foi possível converter a coluna movimentacoes_estoque.origem para origem_movimentacao_enum: %', SQLERRM;
        END $$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Não reverter automaticamente o tipo para evitar perda de dados.
    # Caso seja necessário reverter, isso deve ser feito manualmente com cuidado.
    pass
