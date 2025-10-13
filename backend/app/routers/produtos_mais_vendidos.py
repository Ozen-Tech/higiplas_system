# backend/app/routers/produtos_mais_vendidos.py
"""
Router para produtos mais vendidos baseado no histórico real de movimentações
Utiliza dados de MovimentacaoEstoque para cálculos em tempo real
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_, extract
from typing import List, Optional
from datetime import datetime, date, timedelta
from collections import defaultdict

from ..db.connection import get_db
from ..dependencies import get_current_user
from ..db import models
from ..schemas import produtos_mais_vendidos as schemas

router = APIRouter(
    prefix="/produtos-mais-vendidos",
    tags=["Produtos Mais Vendidos"]
)

@router.get("/", response_model=schemas.ProdutosMaisVendidosResponse)
def get_produtos_mais_vendidos(
    periodo_dias: Optional[int] = Query(365, description="Período em dias para análise (padrão: 365 dias)"),
    data_inicio: Optional[date] = Query(None, description="Data de início específica (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data de fim específica (YYYY-MM-DD)"),
    limite: int = Query(50, description="Número máximo de produtos a retornar"),
    ordenar_por: str = Query("quantidade", description="Ordenar por: 'quantidade', 'valor', 'frequencia'"),
    vendedor_id: Optional[int] = Query(None, description="Filtrar por vendedor específico"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna os produtos mais vendidos baseado no histórico real de movimentações de SAÍDA.
    Calcula métricas avançadas como quantidade total, valor total, frequência de vendas, etc.
    """
    
    # Definir período de análise
    if data_inicio and data_fim:
        inicio = datetime.combine(data_inicio, datetime.min.time())
        fim = datetime.combine(data_fim, datetime.max.time())
    else:
        fim = datetime.now()
        inicio = fim - timedelta(days=periodo_dias)
    
    # Query base para movimentações de SAÍDA
    query = db.query(
        models.MovimentacaoEstoque.produto_id,
        models.Produto.nome.label('produto_nome'),
        models.Produto.codigo.label('produto_codigo'),
        models.Produto.preco_venda.label('preco_atual'),
        models.Produto.categoria.label('categoria'),
        models.Produto.quantidade_em_estoque.label('estoque_atual'),
        func.sum(models.MovimentacaoEstoque.quantidade).label('total_quantidade'),
        func.count(models.MovimentacaoEstoque.id).label('numero_vendas'),
        func.min(models.MovimentacaoEstoque.data_movimentacao).label('primeira_venda'),
        func.max(models.MovimentacaoEstoque.data_movimentacao).label('ultima_venda'),
        func.avg(models.MovimentacaoEstoque.quantidade).label('quantidade_media_por_venda')
    ).join(
        models.Produto, models.MovimentacaoEstoque.produto_id == models.Produto.id
    ).filter(
        and_(
            models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
            models.MovimentacaoEstoque.data_movimentacao >= inicio,
            models.MovimentacaoEstoque.data_movimentacao <= fim,
            models.Produto.empresa_id == current_user.empresa_id
        )
    )
    
    # Filtro por vendedor se especificado
    if vendedor_id:
        query = query.filter(models.MovimentacaoEstoque.usuario_id == vendedor_id)
    
    # Agrupar por produto
    query = query.group_by(
        models.MovimentacaoEstoque.produto_id,
        models.Produto.nome,
        models.Produto.codigo,
        models.Produto.preco_venda,
        models.Produto.categoria,
        models.Produto.quantidade_em_estoque
    )
    
    # Ordenação
    if ordenar_por == "quantidade":
        query = query.order_by(desc('total_quantidade'))
    elif ordenar_por == "valor":
        query = query.order_by(desc(func.sum(models.MovimentacaoEstoque.quantidade * models.Produto.preco_venda)))
    elif ordenar_por == "frequencia":
        query = query.order_by(desc('numero_vendas'))
    
    # Aplicar limite
    resultados = query.limit(limite).all()
    
    # Processar resultados e calcular métricas adicionais
    produtos_processados = []
    total_geral_quantidade = 0
    total_geral_valor = 0
    
    for resultado in resultados:
        valor_total = float(resultado.total_quantidade * resultado.preco_atual)
        total_geral_quantidade += resultado.total_quantidade
        total_geral_valor += valor_total
        
        # Calcular frequência (vendas por dia)
        dias_periodo = (resultado.ultima_venda - resultado.primeira_venda).days + 1
        frequencia_diaria = resultado.numero_vendas / max(dias_periodo, 1)
        
        produto = schemas.ProdutoMaisVendidoDetalhado(
            produto_id=resultado.produto_id,
            nome=resultado.produto_nome,
            codigo=resultado.produto_codigo or f"PROD-{resultado.produto_id}",
            categoria=resultado.categoria or "Sem categoria",
            preco_atual=resultado.preco_atual,
            estoque_atual=resultado.estoque_atual,
            total_quantidade_vendida=resultado.total_quantidade,
            valor_total_vendido=valor_total,
            numero_vendas=resultado.numero_vendas,
            quantidade_media_por_venda=round(float(resultado.quantidade_media_por_venda), 2),
            frequencia_vendas_por_dia=round(frequencia_diaria, 2),
            primeira_venda=resultado.primeira_venda,
            ultima_venda=resultado.ultima_venda,
            dias_desde_ultima_venda=(datetime.now() - resultado.ultima_venda).days
        )
        produtos_processados.append(produto)
    
    # Calcular estatísticas gerais
    estatisticas = schemas.EstatisticasGerais(
        total_produtos_analisados=len(produtos_processados),
        periodo_analise_dias=(fim - inicio).days,
        data_inicio=inicio.date(),
        data_fim=fim.date(),
        total_quantidade_vendida=total_geral_quantidade,
        total_valor_vendido=total_geral_valor,
        ticket_medio=round(total_geral_valor / max(len(produtos_processados), 1), 2),
        produto_mais_vendido=produtos_processados[0].nome if produtos_processados else None,
        categoria_mais_vendida=_calcular_categoria_mais_vendida(produtos_processados)
    )
    
    return schemas.ProdutosMaisVendidosResponse(
        produtos=produtos_processados,
        estatisticas=estatisticas,
        filtros_aplicados={
            "periodo_dias": periodo_dias,
            "data_inicio": data_inicio.isoformat() if data_inicio else None,
            "data_fim": data_fim.isoformat() if data_fim else None,
            "limite": limite,
            "ordenar_por": ordenar_por,
            "vendedor_id": vendedor_id
        }
    )

@router.get("/tendencias", response_model=schemas.TendenciasVendasResponse)
def get_tendencias_vendas(
    produto_id: Optional[int] = Query(None, description="ID do produto específico"),
    periodo_meses: int = Query(6, description="Período em meses para análise de tendências"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna tendências de vendas por mês para análise de sazonalidade
    """
    
    fim = datetime.now()
    inicio = fim - timedelta(days=periodo_meses * 30)
    
    # Query para dados mensais
    query = db.query(
        extract('year', models.MovimentacaoEstoque.data_movimentacao).label('ano'),
        extract('month', models.MovimentacaoEstoque.data_movimentacao).label('mes'),
        models.Produto.nome.label('produto_nome'),
        func.sum(models.MovimentacaoEstoque.quantidade).label('quantidade_mensal'),
        func.sum(models.MovimentacaoEstoque.quantidade * models.Produto.preco_venda).label('valor_mensal')
    ).join(
        models.Produto, models.MovimentacaoEstoque.produto_id == models.Produto.id
    ).filter(
        and_(
            models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
            models.MovimentacaoEstoque.data_movimentacao >= inicio,
            models.MovimentacaoEstoque.data_movimentacao <= fim,
            models.Produto.empresa_id == current_user.empresa_id
        )
    )
    
    if produto_id:
        query = query.filter(models.MovimentacaoEstoque.produto_id == produto_id)
    
    query = query.group_by('ano', 'mes', models.Produto.nome).order_by('ano', 'mes')
    
    resultados = query.all()
    
    # Processar dados mensais
    tendencias_mensais = []
    for resultado in resultados:
        mes_ano = f"{int(resultado.ano)}-{int(resultado.mes):02d}"
        tendencia = schemas.TendenciaMensal(
            mes_ano=mes_ano,
            produto_nome=resultado.produto_nome,
            quantidade_vendida=resultado.quantidade_mensal,
            valor_vendido=float(resultado.valor_mensal)
        )
        tendencias_mensais.append(tendencia)
    
    return schemas.TendenciasVendasResponse(
        tendencias=tendencias_mensais,
        periodo_meses=periodo_meses,
        produto_especifico=produto_id is not None
    )

@router.get("/comparativo-vendedores", response_model=List[schemas.ComparativoVendedor])
def get_comparativo_vendedores(
    periodo_dias: int = Query(30, description="Período em dias para comparação"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Compara performance de vendedores nos produtos mais vendidos
    """
    
    fim = datetime.now()
    inicio = fim - timedelta(days=periodo_dias)
    
    query = db.query(
        models.Usuario.nome.label('vendedor_nome'),
        models.Usuario.id.label('vendedor_id'),
        func.sum(models.MovimentacaoEstoque.quantidade).label('total_quantidade'),
        func.sum(models.MovimentacaoEstoque.quantidade * models.Produto.preco_venda).label('total_valor'),
        func.count(func.distinct(models.MovimentacaoEstoque.produto_id)).label('produtos_diferentes'),
        func.count(models.MovimentacaoEstoque.id).label('numero_vendas')
    ).join(
        models.Usuario, models.MovimentacaoEstoque.usuario_id == models.Usuario.id
    ).join(
        models.Produto, models.MovimentacaoEstoque.produto_id == models.Produto.id
    ).filter(
        and_(
            models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
            models.MovimentacaoEstoque.data_movimentacao >= inicio,
            models.MovimentacaoEstoque.data_movimentacao <= fim,
            models.Produto.empresa_id == current_user.empresa_id
        )
    ).group_by(
        models.Usuario.nome, models.Usuario.id
    ).order_by(desc('total_valor'))
    
    resultados = query.all()
    
    comparativo = []
    for resultado in resultados:
        vendedor = schemas.ComparativoVendedor(
            vendedor_id=resultado.vendedor_id,
            vendedor_nome=resultado.vendedor_nome,
            total_quantidade_vendida=resultado.total_quantidade,
            total_valor_vendido=float(resultado.total_valor),
            produtos_diferentes_vendidos=resultado.produtos_diferentes,
            numero_vendas=resultado.numero_vendas,
            ticket_medio=round(float(resultado.total_valor) / max(resultado.numero_vendas, 1), 2)
        )
        comparativo.append(vendedor)
    
    return comparativo

def _calcular_categoria_mais_vendida(produtos: List[schemas.ProdutoMaisVendidoDetalhado]) -> Optional[str]:
    """Calcula qual categoria teve mais vendas em quantidade"""
    if not produtos:
        return None
    
    categorias = defaultdict(float)
    for produto in produtos:
        categorias[produto.categoria] += produto.total_quantidade_vendida
    
    return max(categorias.items(), key=lambda x: x[1])[0] if categorias else None
@router.get("/", response_model=schemas.ProdutosMaisVendidosResponse)
def get_produtos_mais_vendidos(
    periodo_dias: Optional[int] = Query(365, description="Período em dias para análise (padrão: 365 dias)"),
    data_inicio: Optional[date] = Query(None, description="Data de início específica (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data de fim específica (YYYY-MM-DD)"),
    limite: int = Query(50, description="Número máximo de produtos a retornar"),
    ordenar_por: str = Query("quantidade", description="Ordenar por: 'quantidade', 'valor', 'frequencia'"),
    vendedor_id: Optional[int] = Query(None, description="Filtrar por vendedor específico"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna os produtos mais vendidos baseado no histórico real de movimentações de SAÍDA.
    Calcula métricas avançadas como quantidade total, valor total, frequência de vendas, etc.
    """
    
    try:
        # Definir período de análise
        if data_inicio and data_fim:
            inicio = datetime.combine(data_inicio, datetime.min.time())
            fim = datetime.combine(data_fim, datetime.max.time())
        else:
            fim = datetime.now()
            inicio = fim - timedelta(days=periodo_dias)
        
        # Query base para movimentações de SAÍDA
        query = db.query(
            models.MovimentacaoEstoque.produto_id,
            models.Produto.nome.label('produto_nome'),
            models.Produto.codigo.label('produto_codigo'),
            models.Produto.preco_venda.label('preco_atual'),
            models.Produto.categoria.label('categoria'),
            models.Produto.quantidade_em_estoque.label('estoque_atual'),
            func.sum(models.MovimentacaoEstoque.quantidade).label('total_quantidade'),
            func.count(models.MovimentacaoEstoque.id).label('numero_vendas'),
            func.min(models.MovimentacaoEstoque.data_movimentacao).label('primeira_venda'),
            func.max(models.MovimentacaoEstoque.data_movimentacao).label('ultima_venda'),
            func.avg(models.MovimentacaoEstoque.quantidade).label('quantidade_media_por_venda')
        ).join(
            models.Produto, models.MovimentacaoEstoque.produto_id == models.Produto.id
        ).filter(
            and_(
                models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
                models.MovimentacaoEstoque.data_movimentacao >= inicio,
                models.MovimentacaoEstoque.data_movimentacao <= fim,
                models.Produto.empresa_id == current_user.empresa_id
            )
        )
        
        # Filtro por vendedor se especificado
        if vendedor_id:
            query = query.filter(models.MovimentacaoEstoque.usuario_id == vendedor_id)
        
        # Agrupar por produto
        query = query.group_by(
            models.MovimentacaoEstoque.produto_id,
            models.Produto.nome,
            models.Produto.codigo,
            models.Produto.preco_venda,
            models.Produto.categoria,
            models.Produto.quantidade_em_estoque
        )
        
        # Ordenação
        if ordenar_por == "quantidade":
            query = query.order_by(desc('total_quantidade'))
        elif ordenar_por == "valor":
            query = query.order_by(desc(func.sum(models.MovimentacaoEstoque.quantidade * models.Produto.preco_venda)))
        elif ordenar_por == "frequencia":
            query = query.order_by(desc('numero_vendas'))
        
        # Aplicar limite
        resultados = query.limit(limite).all()
        
        # Processar resultados e calcular métricas adicionais
        produtos_processados = []
        total_geral_quantidade = 0
        total_geral_valor = 0
        
        for resultado in resultados:
            valor_total = float(resultado.total_quantidade * resultado.preco_atual)
            total_geral_quantidade += resultado.total_quantidade
            total_geral_valor += valor_total
            
            # Calcular frequência (vendas por dia)
            dias_periodo = (resultado.ultima_venda - resultado.primeira_venda).days + 1
            frequencia_diaria = resultado.numero_vendas / max(dias_periodo, 1)
            
            produto = schemas.ProdutoMaisVendidoDetalhado(
                produto_id=resultado.produto_id,
                nome=resultado.produto_nome,
                codigo=resultado.produto_codigo or f"PROD-{resultado.produto_id}",
                categoria=resultado.categoria or "Sem categoria",
                preco_atual=resultado.preco_atual,
                estoque_atual=resultado.estoque_atual,
                total_quantidade_vendida=resultado.total_quantidade,
                valor_total_vendido=valor_total,
                numero_vendas=resultado.numero_vendas,
                quantidade_media_por_venda=round(float(resultado.quantidade_media_por_venda), 2),
                frequencia_vendas_por_dia=round(frequencia_diaria, 2),
                primeira_venda=resultado.primeira_venda,
                ultima_venda=resultado.ultima_venda,
                dias_desde_ultima_venda=(datetime.now() - resultado.ultima_venda).days
            )
            produtos_processados.append(produto)
        
        # Calcular estatísticas gerais
        estatisticas = schemas.EstatisticasGerais(
            total_produtos_analisados=len(produtos_processados),
            periodo_analise_dias=(fim - inicio).days,
            data_inicio=inicio.date(),
            data_fim=fim.date(),
            total_quantidade_vendida=total_geral_quantidade,
            total_valor_vendido=total_geral_valor,
            ticket_medio=round(total_geral_valor / max(len(produtos_processados), 1), 2),
            produto_mais_vendido=produtos_processados[0].nome if produtos_processados else None,
            categoria_mais_vendida=_calcular_categoria_mais_vendida(produtos_processados)
        )
        
        return schemas.ProdutosMaisVendidosResponse(
            produtos=produtos_processados,
            estatisticas=estatisticas,
            filtros_aplicados={
                "periodo_dias": periodo_dias,
                "data_inicio": data_inicio.isoformat() if data_inicio else None,
                "data_fim": data_fim.isoformat() if data_fim else None,
                "limite": limite,
                "ordenar_por": ordenar_por,
                "vendedor_id": vendedor_id
            }
        )
    
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao buscar produtos mais vendidos: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar requisição de produtos mais vendidos: {str(e)}"
        )
