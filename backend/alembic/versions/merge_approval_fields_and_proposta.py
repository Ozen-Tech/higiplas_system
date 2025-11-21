"""merge_approval_fields_and_proposta

Revision ID: merge_approval_proposta
Revises: merge_proposta_fornecedor, approval_fields_001
Create Date: 2025-01-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'merge_approval_proposta'
down_revision: Union[str, Sequence[str], None] = ('merge_proposta_fornecedor', 'approval_fields_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

