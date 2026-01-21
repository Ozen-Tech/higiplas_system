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
        
        # Buscar estatísticas por cliente
        query = """
            SELECT 
                c.id as cliente_id,
                c.razao_social as cliente_nome,
                c.cnpj,
                COUNT(DISTINCT hp.nota_fiscal) as total_notas,
                COUNT(DISTINCT hp.produto_id) as produtos_unicos,
                MAX(hp.data_venda) as ultima_compra,
                SUM(hp.valor_total) as valor_total_compras
            FROM clientes c
            LEFT JOIN historico_preco_produto hp ON c.id = hp.cliente_id 
                AND hp.empresa_id = :empresa_id
                AND hp.data_venda >= :data_limite
                AND hp.nota_fiscal IS NOT NULL
            WHERE c.empresa_id = :empresa_id
            GROUP BY c.id, c.razao_social, c.cnpj
            HAVING COUNT(hp.id) > 0
            ORDER BY valor_total_compras DESC NULLS LAST
        """
        
        result = db.execute(
            text(query),
            {
                'empresa_id': current_user.empresa_id,
                'data_limite': data_limite
            }
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
