# /backend/app/routers/dashboard_kpis.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta, date
from app.db.connection import get_db
from app.db import models
from app.dependencies import get_current_user
from app.core.logger import api_logger as logger
from app.core.constants import OrcamentoStatus, OrigemMovimentacao, TipoMovimentacao

router = APIRouter(prefix="/kpis", tags=["Dashboard KPIs"])

@router.get("/")
def get_dashboard_kpis(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna KPIs completos do dashboard incluindo:
    - Estoque: total produtos, baixo estoque, valor total
    - Vendedores: total vendedores, orçamentos pendentes, vendas do mês
    - Vendas: total vendido, orçamentos confirmados, ticket médio
    """
    try:
        empresa_id = current_user.empresa_id
        hoje = date.today()
        inicio_mes = date(hoje.year, hoje.month, 1)
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        
        # ============= ESTOQUE =============
        total_produtos = db.query(func.count(models.Produto.id)).filter(
            models.Produto.empresa_id == empresa_id
        ).scalar() or 0
        
        produtos_baixo_estoque = db.query(func.count(models.Produto.id)).filter(
            models.Produto.empresa_id == empresa_id,
            models.Produto.quantidade_em_estoque <= models.Produto.estoque_minimo,
            models.Produto.estoque_minimo > 0
        ).scalar() or 0
        
        produtos_sem_estoque = db.query(func.count(models.Produto.id)).filter(
            models.Produto.empresa_id == empresa_id,
            models.Produto.quantidade_em_estoque == 0
        ).scalar() or 0

        valor_total_estoque = db.query(
            func.sum(models.Produto.quantidade_em_estoque * models.Produto.preco_custo)
        ).filter(
            models.Produto.empresa_id == empresa_id,
            models.Produto.preco_custo.isnot(None)
        ).scalar() or 0
        
        valor_total_estoque_venda = db.query(
            func.sum(models.Produto.quantidade_em_estoque * models.Produto.preco_venda)
        ).filter(
            models.Produto.empresa_id == empresa_id
        ).scalar() or 0

        # ============= VENDEDORES =============
        total_vendedores = db.query(func.count(models.Usuario.id)).filter(
            models.Usuario.empresa_id == empresa_id,
            models.Usuario.perfil.ilike('%vendedor%')
        ).scalar() or 0
        
        # Orçamentos pendentes (RASCUNHO, ENVIADO, APROVADO)
        orcamentos_pendentes = db.query(func.count(models.Orcamento.id)).join(
            models.Usuario
        ).filter(
            models.Usuario.empresa_id == empresa_id,
            models.Orcamento.status.in_([
                OrcamentoStatus.RASCUNHO.value,
                OrcamentoStatus.ENVIADO.value,
                OrcamentoStatus.APROVADO.value
            ])
        ).scalar() or 0
        
        # Orçamentos do mês
        orcamentos_mes = db.query(func.count(models.Orcamento.id)).join(
            models.Usuario
        ).filter(
            models.Usuario.empresa_id == empresa_id,
            func.date(models.Orcamento.data_criacao) >= inicio_mes
        ).scalar() or 0
        
        # Vendedores ativos (que criaram orçamentos no mês)
        vendedores_ativos = db.query(func.count(func.distinct(models.Orcamento.usuario_id))).join(
            models.Usuario
        ).filter(
            models.Usuario.empresa_id == empresa_id,
            func.date(models.Orcamento.data_criacao) >= inicio_mes
        ).scalar() or 0

        # ============= VENDAS =============
        # Vendas do mês (movimentações de SAIDA com origem VENDA)
        vendas_mes = db.query(
            func.sum(models.MovimentacaoEstoque.quantidade * models.Produto.preco_venda)
        ).join(
            models.Produto
        ).filter(
            models.MovimentacaoEstoque.tipo_movimentacao == TipoMovimentacao.SAIDA.value,
            models.MovimentacaoEstoque.origem == OrigemMovimentacao.VENDA.value,
            models.Produto.empresa_id == empresa_id,
            func.date(models.MovimentacaoEstoque.data_movimentacao) >= inicio_mes
        ).scalar() or 0
        
        # Vendas da semana
        vendas_semana = db.query(
            func.sum(models.MovimentacaoEstoque.quantidade * models.Produto.preco_venda)
        ).join(
            models.Produto
        ).filter(
            models.MovimentacaoEstoque.tipo_movimentacao == TipoMovimentacao.SAIDA.value,
            models.MovimentacaoEstoque.origem == OrigemMovimentacao.VENDA.value,
            models.Produto.empresa_id == empresa_id,
            func.date(models.MovimentacaoEstoque.data_movimentacao) >= inicio_semana
        ).scalar() or 0
        
        # Orçamentos confirmados (FINALIZADO) do mês
        orcamentos_confirmados_mes = db.query(func.count(models.Orcamento.id)).join(
            models.Usuario
        ).filter(
            models.Usuario.empresa_id == empresa_id,
            models.Orcamento.status == OrcamentoStatus.FINALIZADO.value,
            func.date(models.Orcamento.data_criacao) >= inicio_mes
        ).scalar() or 0
        
        # Valor total dos orçamentos confirmados do mês
        valor_orcamentos_confirmados = db.query(
            func.sum(models.OrcamentoItem.quantidade * models.OrcamentoItem.preco_unitario_congelado)
        ).join(
            models.Orcamento
        ).join(
            models.Usuario
        ).filter(
            models.Usuario.empresa_id == empresa_id,
            models.Orcamento.status == OrcamentoStatus.FINALIZADO.value,
            func.date(models.Orcamento.data_criacao) >= inicio_mes
        ).scalar() or 0
        
        # Ticket médio (vendas do mês / número de vendas)
        numero_vendas_mes = db.query(func.count(func.distinct(models.MovimentacaoEstoque.id))).join(
            models.Produto
        ).filter(
            models.MovimentacaoEstoque.tipo_movimentacao == TipoMovimentacao.SAIDA.value,
            models.MovimentacaoEstoque.origem == OrigemMovimentacao.VENDA.value,
            models.Produto.empresa_id == empresa_id,
            func.date(models.MovimentacaoEstoque.data_movimentacao) >= inicio_mes
        ).scalar() or 0
        
        ticket_medio = round(vendas_mes / numero_vendas_mes, 2) if numero_vendas_mes > 0 else 0

        return {
            "estoque": {
                "total_produtos": total_produtos,
                "produtos_baixo_estoque": produtos_baixo_estoque,
                "produtos_sem_estoque": produtos_sem_estoque,
                "valor_total_estoque": round(valor_total_estoque, 2),
                "valor_total_estoque_venda": round(valor_total_estoque_venda, 2)
            },
            "vendedores": {
                "total_vendedores": total_vendedores,
                "vendedores_ativos_mes": vendedores_ativos,
                "orcamentos_pendentes": orcamentos_pendentes,
                "orcamentos_mes": orcamentos_mes
            },
            "vendas": {
                "vendas_mes": round(vendas_mes, 2),
                "vendas_semana": round(vendas_semana, 2),
                "orcamentos_confirmados_mes": orcamentos_confirmados_mes,
                "valor_orcamentos_confirmados": round(valor_orcamentos_confirmados, 2),
                "ticket_medio": ticket_medio,
                "numero_vendas_mes": numero_vendas_mes
            }
        }
    except Exception as e:
        logger.error(f"Erro ao buscar KPIs do dashboard: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar KPIs do dashboard: {str(e)}"
        )