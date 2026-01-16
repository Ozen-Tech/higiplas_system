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


@router.get("/sugestoes/relatorio-completo", summary="Relatório completo de sugestões de compra")
def get_relatorio_completo_sugestoes(
    days_analysis: int = Query(90, description="Período de análise em dias (padrão: 90 dias)"),
    lead_time_days: int = Query(7, description="Lead time em dias (padrão: 7 dias)"),
    coverage_days: int = Query(14, description="Dias de cobertura para compra (padrão: 14 dias)"),
    min_sales_threshold: int = Query(2, description="Número mínimo de vendas para considerar histórico suficiente (padrão: 2)"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente específico (opcional)"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria (opcional)"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Gera relatório completo de sugestões de compra com justificativas detalhadas por cliente.
    Inclui análise por cliente, produtos mais comprados, projeções e investimento necessário.
    """
    try:
        from ..services.purchase_suggestion_service import PurchaseSuggestionService
        from ..services.cliente_analytics_service import ClienteAnalyticsService
        
        service = PurchaseSuggestionService(db)
        analytics_service = ClienteAnalyticsService(db)
        
        # Obter sugestões base
        suggestions = service.get_purchase_suggestions(
            empresa_id=current_user.empresa_id,
            days_analysis=days_analysis,
            lead_time_days=lead_time_days,
            coverage_days=coverage_days,
            min_sales_threshold=min_sales_threshold
        )
        
        # Filtrar por cliente se fornecido
        if cliente_id:
            # Buscar produtos comprados pelo cliente e filtrar sugestões
            analise_cliente = analytics_service.analisar_padroes_cliente(
                cliente_id=cliente_id,
                empresa_id=current_user.empresa_id,
                dias_analise=days_analysis
            )
            
            produtos_cliente_ids = {
                p['produto_id'] for p in analise_cliente.get('produtos_mais_comprados', [])
            }
            
            suggestions = [
                s for s in suggestions 
                if s['produto_id'] in produtos_cliente_ids
            ]
        
        # Filtrar por categoria se fornecido
        if categoria:
            suggestions = [
                s for s in suggestions 
                if s.get('categoria') and categoria.lower() in s['categoria'].lower()
            ]
        
        # Estatísticas do relatório
        total_sugestoes = len(suggestions)
        sugestoes_criticas = len([s for s in suggestions if s['status'] == 'CRÍTICO'])
        sugestoes_baixas = len([s for s in suggestions if s['status'] == 'BAIXO'])
        
        valor_total_estimado = sum(s.get('valor_estimado_compra', 0) for s in suggestions)
        
        # Agrupar por categoria
        por_categoria = {}
        for s in suggestions:
            cat = s.get('categoria') or 'Sem categoria'
            if cat not in por_categoria:
                por_categoria[cat] = {
                    'total_produtos': 0,
                    'valor_total': 0,
                    'produtos_criticos': 0
                }
            por_categoria[cat]['total_produtos'] += 1
            por_categoria[cat]['valor_total'] += s.get('valor_estimado_compra', 0)
            if s['status'] == 'CRÍTICO':
                por_categoria[cat]['produtos_criticos'] += 1
        
        # Top clientes que compram os produtos sugeridos
        top_clientes_por_produto = {}
        for s in suggestions[:10]:  # Top 10 produtos
            analise_produto = analytics_service.analisar_padroes_produto_por_cliente(
                produto_id=s['produto_id'],
                empresa_id=current_user.empresa_id,
                dias_analise=days_analysis
            )
            
            top_clientes = sorted(
                analise_produto.get('clientes', []),
                key=lambda x: x.get('total_valor', 0),
                reverse=True
            )[:3]  # Top 3 clientes por produto
            
            top_clientes_por_produto[s['produto_id']] = {
                'produto_nome': s['produto_nome'],
                'clientes': top_clientes
            }
        
        # Projeção de vendas (próximos 14-30 dias)
        projecao_vendas = {}
        for s in suggestions:
            demanda_media_diaria = s.get('demanda_media_diaria', 0)
            projecao_14_dias = demanda_media_diaria * 14
            projecao_30_dias = demanda_media_diaria * 30
            
            projecao_vendas[s['produto_id']] = {
                'produto_nome': s['produto_nome'],
                'projecao_14_dias': round(projecao_14_dias, 1),
                'projecao_30_dias': round(projecao_30_dias, 1),
                'demanda_media_diaria': demanda_media_diaria
            }
        
        return {
            'resumo': {
                'total_sugestoes': total_sugestoes,
                'sugestoes_criticas': sugestoes_criticas,
                'sugestoes_baixas': sugestoes_baixas,
                'valor_total_estimado': round(valor_total_estimado, 2),
                'periodo_analise_dias': days_analysis,
                'data_geracao': datetime.now().isoformat()
            },
            'sugestoes': suggestions,
            'por_categoria': por_categoria,
            'top_clientes_por_produto': top_clientes_por_produto,
            'projecao_vendas': projecao_vendas,
            'parametros': {
                'days_analysis': days_analysis,
                'lead_time_days': lead_time_days,
                'coverage_days': coverage_days,
                'min_sales_threshold': min_sales_threshold,
                'cliente_id': cliente_id,
                'categoria': categoria
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório completo: {str(e)}"
        )

