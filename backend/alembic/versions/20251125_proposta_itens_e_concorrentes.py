"""Cria tabelas de itens e concorrentes manuais para propostas detalhadas

Revision ID: proposta_itens_concorrentes
Revises: merge_approval_proposta
Create Date: 2025-11-25 10:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = "proposta_itens_concorrentes"
down_revision: Union[str, Sequence[str], None] = "merge_approval_proposta"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria tabelas auxiliares e migra dados existentes."""
    op.create_table(
        "propostas_detalhadas_itens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("proposta_id", sa.Integer(), sa.ForeignKey("propostas_detalhadas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("produto_id", sa.Integer(), sa.ForeignKey("produtos.id"), nullable=False),
        sa.Column("quantidade_produto", sa.Float(), nullable=False),
        sa.Column("dilucao_aplicada", sa.String(), nullable=True),
        sa.Column("dilucao_numerador", sa.Float(), nullable=True),
        sa.Column("dilucao_denominador", sa.Float(), nullable=True),
        sa.Column("rendimento_total_litros", sa.Float(), nullable=True),
        sa.Column("preco_produto", sa.Float(), nullable=True),
        sa.Column("custo_por_litro_final", sa.Float(), nullable=True),
        sa.Column("observacoes", sa.String(), nullable=True),
        sa.Column("ordem", sa.Integer(), nullable=True),
        sa.Column("concorrente_nome_manual", sa.String(), nullable=True),
        sa.Column("concorrente_rendimento_manual", sa.Float(), nullable=True),
        sa.Column("concorrente_custo_por_litro_manual", sa.Float(), nullable=True),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("data_atualizacao", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_propostas_itens_proposta", "propostas_detalhadas_itens", ["proposta_id"])
    op.create_index("ix_propostas_itens_produto", "propostas_detalhadas_itens", ["produto_id"])
    op.create_index("idx_proposta_item_produto", "propostas_detalhadas_itens", ["proposta_id", "produto_id"])

    op.create_table(
        "propostas_detalhadas_concorrentes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("proposta_id", sa.Integer(), sa.ForeignKey("propostas_detalhadas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("rendimento_litro", sa.Float(), nullable=True),
        sa.Column("custo_por_litro", sa.Float(), nullable=True),
        sa.Column("observacoes", sa.String(), nullable=True),
        sa.Column("ordem", sa.Integer(), nullable=True),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("data_atualizacao", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_propostas_concorrentes_proposta", "propostas_detalhadas_concorrentes", ["proposta_id"])
    op.create_index("idx_proposta_concorrente_manual", "propostas_detalhadas_concorrentes", ["proposta_id", "nome"])

    # Migrar dados existentes para a tabela de itens
    bind = op.get_bind()
    metadata = sa.MetaData()
    propostas = sa.Table("propostas_detalhadas", metadata, autoload_with=bind)
    itens = sa.Table("propostas_detalhadas_itens", metadata, autoload_with=bind)

    propostas_existentes = bind.execute(sa.select(propostas)).fetchall()
    if propostas_existentes:
        insert_payload = []
        now = datetime.utcnow()
        for registro in propostas_existentes:
            insert_payload.append(
                {
                    "proposta_id": registro.id,
                    "produto_id": registro.produto_id,
                    "quantidade_produto": registro.quantidade_produto,
                    "dilucao_aplicada": registro.dilucao_aplicada,
                    "dilucao_numerador": registro.dilucao_numerador,
                    "dilucao_denominador": registro.dilucao_denominador,
                    "rendimento_total_litros": registro.rendimento_total_litros,
                    "preco_produto": registro.preco_produto,
                    "custo_por_litro_final": registro.custo_por_litro_final,
                    "observacoes": registro.observacoes,
                    "ordem": 1,
                    "data_criacao": now,
                    "data_atualizacao": now,
                }
            )

        if insert_payload:
            bind.execute(sa.insert(itens), insert_payload)


def downgrade() -> None:
    """Reverte criação das tabelas auxiliares."""
    op.drop_index("idx_proposta_concorrente_manual", table_name="propostas_detalhadas_concorrentes")
    op.drop_index("ix_propostas_concorrentes_proposta", table_name="propostas_detalhadas_concorrentes")
    op.drop_table("propostas_detalhadas_concorrentes")

    op.drop_index("idx_proposta_item_produto", table_name="propostas_detalhadas_itens")
    op.drop_index("ix_propostas_itens_produto", table_name="propostas_detalhadas_itens")
    op.drop_index("ix_propostas_itens_proposta", table_name="propostas_detalhadas_itens")
    op.drop_table("propostas_detalhadas_itens")


