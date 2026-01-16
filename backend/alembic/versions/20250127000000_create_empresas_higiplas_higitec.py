"""create_empresas_higiplas_higitec

Revision ID: create_empresas_higiplas_higitec
Revises: preco_cliente_produto_001
Create Date: 2025-01-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = 'create_empresas_higiplas_higitec'
down_revision: Union[str, Sequence[str], None] = 'preco_cliente_produto_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Garante que empresas HIGIPLAS e HIGITEC existem."""
    connection = op.get_bind()
    
    # Verificar e criar HIGIPLAS
    result = connection.execute(text(
        "SELECT id FROM empresas WHERE nome ILIKE '%HIGIPLAS%' LIMIT 1"
    ))
    higiplas = result.first()
    
    if not higiplas:
        connection.execute(text(
            """
            INSERT INTO empresas (nome, cnpj, data_criacao)
            VALUES ('HIGIPLAS', '22.599.389/0001-76', NOW())
            """
        ))
        print("✓ Empresa HIGIPLAS criada")
    else:
        # Atualizar CNPJ se não estiver definido
        connection.execute(text(
            """
            UPDATE empresas 
            SET cnpj = '22.599.389/0001-76' 
            WHERE id = :id AND (cnpj IS NULL OR cnpj = '')
            """
        ), {"id": higiplas[0]})
        print("✓ Empresa HIGIPLAS verificada")
    
    # Verificar e criar HIGITEC
    result = connection.execute(text(
        "SELECT id FROM empresas WHERE nome ILIKE '%HIGITEC%' LIMIT 1"
    ))
    higitec = result.first()
    
    if not higitec:
        connection.execute(text(
            """
            INSERT INTO empresas (nome, cnpj, data_criacao)
            VALUES ('HIGITEC', '44.874.126/0001-60', NOW())
            """
        ))
        print("✓ Empresa HIGITEC criada")
    else:
        # Atualizar CNPJ se não estiver definido
        connection.execute(text(
            """
            UPDATE empresas 
            SET cnpj = '44.874.126/0001-60' 
            WHERE id = :id AND (cnpj IS NULL OR cnpj = '')
            """
        ), {"id": higitec[0]})
        print("✓ Empresa HIGITEC verificada")
    
    connection.commit()


def downgrade() -> None:
    """Downgrade schema - Não remove as empresas, apenas documenta."""
    # Não removemos as empresas no downgrade para evitar problemas de integridade
    # Se necessário remover manualmente, usar: DELETE FROM empresas WHERE nome IN ('HIGIPLAS', 'HIGITEC')
    pass
