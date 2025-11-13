from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..db.connection import get_db
from ..dependencies import get_current_user
from ..db import models
from ..services.purchase_suggestion_service import PurchaseSuggestionService
from ..services.compras_kpi_service import ComprasKPIService
from ..schemas import compras as schemas_compras

router = APIRouter(prefix="/compras", tags=["Compras"])


@router.get("/sugestoes", response_model=schemas_compras.PurchaseSuggestionResponse)
def get_purchase_suggestions(
    days_analysis: int = Query(90, description="Período de análise em dias (padrão: 90 dias)"),
    lead_time_days: int = Query(7, description="Lead time em dias (padrão: 7 dias)"),
    coverage_days: int = Query(14, description="Dias de cobertura para compra (padrão: 14 dias)"),
    min_sales_threshold: int = Query(2, description="Número mínimo de vendas para considerar histórico suficiente (padrão: 2)"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna sugestões de compra baseadas em análise de demanda histórica.
    
    Apenas produtos com histórico suficiente (mínimo de vendas) são incluídos.
    Produtos sem histórico suficiente não são sugeridos para compra.
    """
    try:
        service = PurchaseSuggestionService(db)
        
        suggestions = service.get_purchase_suggestions(
            empresa_id=current_user.empresa_id,
            days_analysis=days_analysis,
            lead_time_days=lead_time_days,
            coverage_days=coverage_days,
            min_sales_threshold=min_sales_threshold
        )
        
        # Conta sugestões por status
        sugestoes_criticas = len([s for s in suggestions if s['status'] == 'CRÍTICO'])
        sugestoes_baixas = len([s for s in suggestions if s['status'] == 'BAIXO'])
        
        return {
            'total_sugestoes': len(suggestions),
            'sugestoes_criticas': sugestoes_criticas,
            'sugestoes_baixas': sugestoes_baixas,
            'sugestoes': suggestions,
            'data_analise': datetime.now()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar sugestões de compra: {str(e)}"
        )


@router.get("/sugestoes/produto/{produto_id}", response_model=schemas_compras.ProductAnalysisResponse)
def get_product_analysis(
    produto_id: int,
    days_analysis: int = Query(90, description="Período de análise em dias (padrão: 90 dias)"),
    lead_time_days: int = Query(7, description="Lead time em dias (padrão: 7 dias)"),
    coverage_days: int = Query(14, description="Dias de cobertura para compra (padrão: 14 dias)"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna análise completa de um produto específico para compras.
    
    Inclui demanda histórica, estoque mínimo calculado e quantidade sugerida de compra.
    """
    try:
        service = PurchaseSuggestionService(db)
        
        analysis = service.get_product_analysis(
            produto_id=produto_id,
            empresa_id=current_user.empresa_id,
            days_analysis=days_analysis,
            lead_time_days=lead_time_days,
            coverage_days=coverage_days
        )
        
        if 'erro' in analysis:
            raise HTTPException(status_code=404, detail=analysis['erro'])
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao analisar produto: {str(e)}"
        )


# ============= KPIs DE COMPRAS =============

@router.get("/kpis", summary="Obter todos os KPIs de compras")
def obter_kpis_compras(
    periodo_meses: int = Query(12, description="Período de análise em meses (padrão: 12 meses)"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna todos os KPIs de compras calculados em tempo real.
    Inclui: curva ABC, eficiência de compras, estoque parado, etc.
    """
    try:
        kpi_service = ComprasKPIService(db)
        empresa_id = current_user.empresa_id or 1  # Fallback se não tiver empresa_id
        
        kpis = kpi_service.calcular_todos_kpis(empresa_id, periodo_meses)
        return kpis
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular KPIs de compras: {str(e)}"
        )


@router.get("/kpis/produto/{produto_id}", summary="KPIs específicos de um produto")
def obter_kpi_produto(
    produto_id: int,
    periodo_meses: int = Query(12, description="Período de análise em meses"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna KPIs específicos de um produto: giro de estoque, dias de cobertura, previsão de compras.
    """
    try:
        kpi_service = ComprasKPIService(db)
        empresa_id = current_user.empresa_id or 1
        
        giro = kpi_service.calcular_giro_estoque(produto_id, empresa_id, periodo_meses)
        cobertura = kpi_service.calcular_dias_cobertura(produto_id, empresa_id, 90)
        previsao = kpi_service.calcular_previsao_compras(produto_id, empresa_id)
        
        return {
            'produto_id': produto_id,
            'giro_estoque': giro,
            'dias_cobertura': cobertura,
            'previsao_compras': previsao
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular KPIs do produto: {str(e)}"
        )


@router.get("/kpis/fornecedor/{fornecedor_id}", summary="KPIs por fornecedor")
def obter_kpi_fornecedor(
    fornecedor_id: int,
    periodo_meses: int = Query(12, description="Período de análise em meses"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna KPIs de rotatividade e eficiência de um fornecedor.
    """
    try:
        kpi_service = ComprasKPIService(db)
        empresa_id = current_user.empresa_id or 1
        
        turnover = kpi_service.calcular_turnover_fornecedor(fornecedor_id, empresa_id, periodo_meses)
        
        if not turnover:
            raise HTTPException(status_code=404, detail="Fornecedor não encontrado ou sem histórico")
        
        return turnover
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular KPIs do fornecedor: {str(e)}"
        )

