"""
Router para análise de compras dos clientes baseado em histórico de NF-e.
Endpoints para histórico de compras, produtos mais comprados e sugestões.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List
from ..db.connection import get_db
from ..dependencies import get_current_user
from ..db import models
from ..services.cliente_purchase_suggestion_service import ClientePurchaseSuggestionService

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes - Análise de Compras"],
    responses={404: {"description": "Não encontrado"}}
)


@router.get("/{cliente_id}/historico-compras", summary="Histórico completo de compras do cliente")
def get_historico_compras_cliente(
    cliente_id: int,
    dias: int = Query(90, description="Período de análise em dias"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna histórico completo de todas as compras do cliente via NF-e processadas.
    Agrupa compras por nota fiscal, incluindo produtos, quantidades, valores e datas.
    Apenas dados verificados de NF-e eletrônicas (com nota_fiscal).
    """
    try:
        # Verificar se cliente pertence à empresa do usuário
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == cliente_id,
            models.Cliente.empresa_id == current_user.empresa_id
        ).first()
        
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        service = ClientePurchaseSuggestionService(db)
        historico = service.get_client_purchase_history(
            cliente_id=cliente_id,
            empresa_id=current_user.empresa_id,
            dias=dias
        )
        
        return historico
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar histórico de compras: {str(e)}")


@router.get("/{cliente_id}/produtos-mais-comprados", summary="Produtos mais comprados pelo cliente")
def get_produtos_mais_comprados_cliente(
    cliente_id: int,
    limit: int = Query(10, description="Número de produtos a retornar"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna lista dos produtos mais comprados pelo cliente, baseado em histórico de NF-e.
    Ordenado por valor total comprado.
    """
    try:
        # Verificar se cliente pertence à empresa do usuário
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == cliente_id,
            models.Cliente.empresa_id == current_user.empresa_id
        ).first()
        
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        service = ClientePurchaseSuggestionService(db)
        produtos = service.get_top_products_by_cliente(
            cliente_id=cliente_id,
            empresa_id=current_user.empresa_id,
            limit=limit
        )
        
        return {
            'cliente_id': cliente_id,
            'cliente_nome': cliente.razao_social,
            'cnpj': cliente.cnpj,
            'produtos_mais_comprados': produtos
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar produtos mais comprados: {str(e)}")


@router.get("/{cliente_id}/sugestoes-compra", summary="Sugestões de compra para o cliente")
def get_sugestoes_compra_cliente(
    cliente_id: int,
    dias_analise: int = Query(90, description="Período de análise em dias"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna sugestões de compra baseadas no padrão de compras do cliente.
    Indica produtos que o cliente compra regularmente e quando comprar (até 1 semana após pedido).
    """
    try:
        # Verificar se cliente pertence à empresa do usuário
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == cliente_id,
            models.Cliente.empresa_id == current_user.empresa_id
        ).first()
        
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        service = ClientePurchaseSuggestionService(db)
        sugestoes = service.get_purchase_suggestions_for_cliente(
            cliente_id=cliente_id,
            empresa_id=current_user.empresa_id,
            dias_analise=dias_analise
        )
        
        return sugestoes
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar sugestões de compra: {str(e)}")


@router.get("/todos/compras-analise", summary="Análise agregada de todos os clientes")
def get_compras_analise_todos_clientes(
    dias: int = Query(90, description="Período de análise em dias"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna análise agregada de compras de todos os clientes da empresa.
    Mostra produtos mais comprados, clientes mais frequentes, etc.
    """
    try:
        service = ClientePurchaseSuggestionService(db)
        sugestoes = service.get_global_purchase_suggestions(
            empresa_id=current_user.empresa_id,
            dias_analise=dias
        )
        
        return sugestoes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar análise agregada: {str(e)}")


@router.get("/todos/visao-geral", summary="Visão geral de todos os clientes")
def get_visao_geral_clientes(
    dias: int = Query(90, description="Período de análise em dias"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna visão geral de todos os clientes: total de compras, produtos únicos, última compra.
    Útil para dashboard e lista de clientes.
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        data_limite = datetime.now() - timedelta(days=dias)
        empresa_id = current_user.empresa_id

        # Unificar HPP (NF-e) e HVC (orçamentos): incluir clientes com compras em qualquer fonte.
        # Evitar duplicar venda quando orçamento já tem NF (mesma venda em HPP e HVC).
        query = """
            WITH vendas_nf AS (
                SELECT hp.cliente_id, hp.produto_id, hp.valor_total, hp.data_venda, hp.nota_fiscal
                FROM historico_preco_produto hp
                WHERE hp.empresa_id = :empresa_id AND hp.data_venda >= :data_limite
                  AND hp.nota_fiscal IS NOT NULL AND hp.cliente_id IS NOT NULL
            ),
            vendas_orcamento AS (
                SELECT hvc.cliente_id, hvc.produto_id, hvc.valor_total, hvc.data_venda
                FROM historico_vendas_cliente hvc
                LEFT JOIN orcamentos o ON o.id = hvc.orcamento_id AND o.numero_nf IS NOT NULL AND o.numero_nf != ''
                WHERE hvc.empresa_id = :empresa_id AND hvc.data_venda >= :data_limite AND o.id IS NULL
            ),
            vendas_unificado AS (
                SELECT cliente_id, produto_id, valor_total, data_venda FROM vendas_nf
                UNION ALL
                SELECT cliente_id, produto_id, valor_total, data_venda FROM vendas_orcamento
            ),
            agregado AS (
                SELECT v.cliente_id,
                    COUNT(DISTINCT v.produto_id) AS produtos_unicos,
                    MAX(v.data_venda) AS ultima_compra,
                    COALESCE(SUM(v.valor_total), 0) AS valor_total_compras
                FROM vendas_unificado v
                GROUP BY v.cliente_id
            ),
            total_notas AS (
                SELECT hp.cliente_id, COUNT(DISTINCT hp.nota_fiscal) AS total_notas
                FROM historico_preco_produto hp
                WHERE hp.empresa_id = :empresa_id AND hp.data_venda >= :data_limite
                  AND hp.nota_fiscal IS NOT NULL AND hp.cliente_id IS NOT NULL
                GROUP BY hp.cliente_id
            )
            SELECT c.id AS cliente_id, c.razao_social AS cliente_nome, c.cnpj,
                COALESCE(tn.total_notas, 0) AS total_notas,
                a.produtos_unicos,
                a.ultima_compra,
                a.valor_total_compras
            FROM clientes c
            JOIN agregado a ON c.id = a.cliente_id
            LEFT JOIN total_notas tn ON c.id = tn.cliente_id
            WHERE c.empresa_id = :empresa_id
            ORDER BY a.valor_total_compras DESC NULLS LAST
        """
        result = db.execute(
            text(query),
            {'empresa_id': empresa_id, 'data_limite': data_limite}
        )
        clientes_data = []
        for row in result:
            clientes_data.append({
                'cliente_id': row.cliente_id,
                'cliente_nome': row.cliente_nome,
                'cnpj': row.cnpj,
                'total_notas': row.total_notas or 0,
                'produtos_unicos': row.produtos_unicos or 0,
                'ultima_compra': row.ultima_compra.isoformat() if row.ultima_compra else None,
                'valor_total_compras': float(row.valor_total_compras) if row.valor_total_compras else 0
            })
        
        return {
            'periodo_dias': dias,
            'total_clientes_com_compras': len(clientes_data),
            'clientes': clientes_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar visão geral: {str(e)}")


@router.get("/resultados-mensais", summary="Resultados mensais por cliente (vendas unificadas)")
def get_resultados_mensais_clientes(
    ano: int = Query(..., description="Ano (ex.: 2025)"),
    mes: int = Query(..., ge=1, le=12, description="Mês (1-12)"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna resultados mensais por cliente: valor total, quantidade de pedidos e produtos vendidos.
    Fonte unificada: HistoricoPrecoProduto (NF-e) e HistoricoVendaCliente (orçamentos sem NF linkada).
    """
    try:
        from datetime import datetime
        start = datetime(ano, mes, 1)
        if mes == 12:
            end = datetime(ano + 1, 1, 1)
        else:
            end = datetime(ano, mes + 1, 1)
        empresa_id = current_user.empresa_id

        # Agregar por cliente a partir de HPP (NF) e HVC (orçamentos sem NF)
        query = text("""
            WITH vendas_nf AS (
                SELECT hp.cliente_id, hp.produto_id, hp.valor_total, hp.quantidade, hp.data_venda
                FROM historico_preco_produto hp
                WHERE hp.empresa_id = :empresa_id AND hp.data_venda >= :start AND hp.data_venda < :end
                  AND hp.nota_fiscal IS NOT NULL AND hp.cliente_id IS NOT NULL
            ),
            vendas_orc AS (
                SELECT hvc.cliente_id, hvc.produto_id, hvc.valor_total, hvc.quantidade_vendida AS quantidade, hvc.data_venda
                FROM historico_vendas_cliente hvc
                LEFT JOIN orcamentos o ON o.id = hvc.orcamento_id AND o.numero_nf IS NOT NULL AND o.numero_nf != ''
                WHERE hvc.empresa_id = :empresa_id AND hvc.data_venda >= :start AND hvc.data_venda < :end AND o.id IS NULL
            ),
            unificado AS (
                SELECT cliente_id, produto_id, valor_total, quantidade, data_venda FROM vendas_nf
                UNION ALL
                SELECT cliente_id, produto_id, valor_total, quantidade, data_venda FROM vendas_orc
            )
            SELECT u.cliente_id,
                c.razao_social AS cliente_nome,
                c.cnpj,
                COUNT(DISTINCT u.data_venda::date) AS num_pedidos,
                COALESCE(SUM(u.valor_total), 0) AS valor_total,
                COUNT(DISTINCT u.produto_id) AS produtos_unicos
            FROM unificado u
            JOIN clientes c ON c.id = u.cliente_id AND c.empresa_id = :empresa_id
            GROUP BY u.cliente_id, c.razao_social, c.cnpj
            ORDER BY valor_total DESC
        """)
        result = db.execute(query, {"empresa_id": empresa_id, "start": start, "end": end})
        clientes = []
        for row in result:
            clientes.append({
                "cliente_id": row.cliente_id,
                "cliente_nome": row.cliente_nome,
                "cnpj": row.cnpj,
                "num_pedidos": row.num_pedidos or 0,
                "valor_total": float(row.valor_total or 0),
                "produtos_unicos": row.produtos_unicos or 0,
            })
        return {"ano": ano, "mes": mes, "clientes": clientes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar resultados mensais: {str(e)}")
