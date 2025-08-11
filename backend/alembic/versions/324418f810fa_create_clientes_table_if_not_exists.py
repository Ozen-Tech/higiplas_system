"""Create clientes table if not exists

Revision ID: 324418f810fa
Revises: 07af028af52e
Create Date: 2025-08-11 20:45:00.379579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '324418f810fa'
down_revision: Union[str, Sequence[str], None] = '07af028af52e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    from alembic import context
    
    # Get connection to check if tables exist
    connection = context.get_bind()
    
    # Check if clientes table exists
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'clientes')"
    ))
    clientes_exists = result.scalar()
    
    if not clientes_exists:
        print("Creating clientes table...")
        # Create enums first
        op.execute("CREATE TYPE empresa_vinculada_enum AS ENUM ('HIGIPLAS', 'HIGITEC')")
        op.execute("CREATE TYPE status_pagamento_enum AS ENUM ('BOM_PAGADOR', 'MAU_PAGADOR')")
        
        # Create clientes table
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
        op.create_index(op.f('ix_clientes_id'), 'clientes', ['id'], unique=False)
        op.create_index(op.f('ix_clientes_razao_social'), 'clientes', ['razao_social'], unique=False)
        op.create_index(op.f('ix_clientes_cnpj'), 'clientes', ['cnpj'], unique=True)
        print("Clientes table created successfully!")
    else:
        print("Clientes table already exists, skipping creation.")
    
    # Check if historico_pagamentos table exists
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'historico_pagamentos')"
    ))
    historico_exists = result.scalar()
    
    if not historico_exists:
        print("Creating historico_pagamentos table...")
        # Create enum for historico_pagamentos if it doesn't exist
        op.execute("CREATE TYPE IF NOT EXISTS status_pagamento_historico_enum AS ENUM ('PAGO', 'PENDENTE', 'ATRASADO')")
        
        # Create historico_pagamentos table
        op.create_table('historico_pagamentos',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('cliente_id', sa.Integer(), nullable=False),
            sa.Column('data_pagamento', sa.Date(), nullable=False),
            sa.Column('valor', sa.Float(), nullable=False),
            sa.Column('status', sa.Enum('PAGO', 'PENDENTE', 'ATRASADO', name='status_pagamento_historico_enum'), nullable=False),
            sa.Column('observacoes', sa.String(), nullable=True),
            sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        print("Historico_pagamentos table created successfully!")
    else:
        print("Historico_pagamentos table already exists, skipping creation.")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop historico_pagamentos table
    op.drop_table('historico_pagamentos')
    
    # Drop clientes table
    op.drop_index(op.f('ix_clientes_cnpj'), table_name='clientes')
    op.drop_index(op.f('ix_clientes_razao_social'), table_name='clientes')
    op.drop_index(op.f('ix_clientes_id'), table_name='clientes')
    op.drop_table('clientes')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS empresa_vinculada_enum')
    op.execute('DROP TYPE IF EXISTS status_pagamento_enum')
    op.execute('DROP TYPE IF EXISTS status_pagamento_historico_enum')
