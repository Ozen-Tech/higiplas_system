# backend/app/routers/produtos_mais_vendidos.py
"""
Router para produtos mais vendidos baseado no histórico real de movimentações
Utiliza dados de MovimentacaoEstoque para cálculos em tempo real
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_, extract, or_
from typing import List, Optional
from datetime import datetime, date, timedelta, timezone
from collections import defaultdict

from ..db.connection import get_db
from ..dependencies import get_current_user
from ..db import models
from ..schemas import produtos_mais_vendidos as schemas

router = APIRouter(
    prefix="/produtos-mais-vendidos",
    tags=["Produtos Mais Vendidos"]
)

# Origens automáticas válidas para análise de vendas (exclui CORRECAO_MANUAL e AJUSTE que são manuais)
# Inclui: VENDA (vendas e orçamentos confirmados), DEVOLUCAO, COMPRA, OUTRO
ORIGENS_AUTOMATICAS = ['VENDA', 'DEVOLUCAO', 'COMPRA', 'OUTRO']

# Observações padrão que caracterizam vendas realizadas pelo aplicativo de vendedores
OBSERVACOES_VENDA_PADRAO = [
    "Venda Operador",
    "Venda realizada pelo vendedor",
    "Venda para"
]

# Observações padrão utilizadas para baixas automáticas a partir de notas fiscais importadas
OBSERVACOES_NF_PADRAO = [
    "Importação automática - NF",
    "Processamento automático - NF"
]


def _status_confirmado_expression():
    """Garante que apenas movimentações confirmadas (ou legadas sem status) sejam consideradas."""
    return or_(
        models.MovimentacaoEstoque.status == 'CONFIRMADO',
        models.MovimentacaoEstoque.status.is_(None)
    )


def _observacao_permitida_expression():
    """Filtra apenas movimentações que tenham observações padronizadas (vendedores / NF)."""
    observacao_col = func.coalesce(models.MovimentacaoEstoque.observacao, "")
    condicoes = [
        observacao_col.ilike(f"{pattern}%")
        for pattern in (OBSERVACOES_VENDA_PADRAO + OBSERVACOES_NF_PADRAO)
    ]
    return or_(*condicoes)

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
    Considera apenas movimentações automáticas (VENDA, DEVOLUCAO, COMPRA, OUTRO), 
    excluindo correções manuais (CORRECAO_MANUAL, AJUSTE).
    Inclui automaticamente movimentações de orçamentos confirmados (origem='VENDA').
    Calcula métricas avançadas como quantidade total, valor total, frequência de vendas, etc.
    """

    # Definir período de análise
    if data_inicio and data_fim:
        inicio = datetime.combine(data_inicio, datetime.min.time())
        fim = datetime.combine(data_fim, datetime.max.time())
    else:
        fim = datetime.now()
        inicio = fim - timedelta(days=periodo_dias)

    allowed_observacoes = _observacao_permitida_expression()
    status_confirmado = _status_confirmado_expression()

    # Query base para movimentações de SAÍDA automáticas
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
            models.Produto.empresa_id == current_user.empresa_id,
            # Filtrar apenas movimentações automáticas
            or_(
                models.MovimentacaoEstoque.origem.in_(ORIGENS_AUTOMATICAS),
                models.MovimentacaoEstoque.origem.is_(None)  # Incluir movimentações antigas sem origem definida
            ),
            status_confirmado,
            allowed_observacoes
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
    # Nota: Para ordenação por valor, calculamos após o group_by usando a expressão correta
    if ordenar_por == "quantidade":
        query = query.order_by(desc('total_quantidade'))
    elif ordenar_por == "valor":
        # Ordena pela soma das quantidades multiplicada pelo preço (usando alias após group_by)
        # Usamos func.sum() dentro do order_by porque já está agrupado
        query = query.order_by(desc(func.sum(models.MovimentacaoEstoque.quantidade) * func.max(models.Produto.preco_venda)))
    elif ordenar_por == "frequencia":
        query = query.order_by(desc('numero_vendas'))

    # Aplicar limite
    resultados = query.limit(limite).all()

    # Processar resultados e calcular métricas adicionais
    produtos_processados = []
    total_geral_quantidade = 0
    total_geral_valor = 0

    # Get current time with timezone awareness
    now = datetime.now(timezone.utc)

    for resultado in resultados:
        valor_total = float(resultado.total_quantidade * resultado.preco_atual)
        total_geral_quantidade += resultado.total_quantidade
        total_geral_valor += valor_total

        # Preparar datas de primeira/ultima venda de forma segura (evita problemas de timezone)
        primeira_venda = resultado.primeira_venda
        ultima_venda_raw = resultado.ultima_venda

        if primeira_venda is not None and ultima_venda_raw is not None:
            # Use apenas a parte date para evitar mismatches entre aware/naive
            dias_periodo = (ultima_venda_raw.date() - primeira_venda.date()).days + 1
        else:
            dias_periodo = 1

        frequencia_diaria = resultado.numero_vendas / max(dias_periodo, 1)

        # Tornar ultima_venda timezone-aware se estiver sem tzinfo
        ultima_venda = ultima_venda_raw
        if ultima_venda is not None and ultima_venda.tzinfo is None:
            ultima_venda = ultima_venda.replace(tzinfo=timezone.utc)

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
            primeira_venda=primeira_venda,
            ultima_venda=ultima_venda,
            dias_desde_ultima_venda=(now - ultima_venda).days if ultima_venda is not None else None
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
    Retorna tendências de vendas por mês para análise de sazonalidade.
    Considera apenas movimentações automáticas (exclui correções manuais).
    """

    fim = datetime.now()
    inicio = fim - timedelta(days=periodo_meses * 30)

    # Query para dados mensais (apenas movimentações automáticas)
    # Nota: Calculamos quantidade_mensal primeiro, depois multiplicamos pelo preço atual
    # Isso evita distorções se o preço mudou ao longo do tempo
    allowed_observacoes = _observacao_permitida_expression()
    status_confirmado = _status_confirmado_expression()

    query = db.query(
        extract('year', models.MovimentacaoEstoque.data_movimentacao).label('ano'),
        extract('month', models.MovimentacaoEstoque.data_movimentacao).label('mes'),
        models.Produto.nome.label('produto_nome'),
        models.Produto.preco_venda.label('preco_atual'),
        func.sum(models.MovimentacaoEstoque.quantidade).label('quantidade_mensal')
    ).join(
        models.Produto, models.MovimentacaoEstoque.produto_id == models.Produto.id
    ).filter(
        and_(
            models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
            models.MovimentacaoEstoque.data_movimentacao >= inicio,
            models.MovimentacaoEstoque.data_movimentacao <= fim,
            models.Produto.empresa_id == current_user.empresa_id,
            # Filtrar apenas movimentações automáticas
            or_(
                models.MovimentacaoEstoque.origem.in_(ORIGENS_AUTOMATICAS),
                models.MovimentacaoEstoque.origem.is_(None)  # Incluir movimentações antigas sem origem definida
            ),
            status_confirmado,
            allowed_observacoes
        )
    )

    if produto_id:
        query = query.filter(models.MovimentacaoEstoque.produto_id == produto_id)

    query = query.group_by('ano', 'mes', models.Produto.nome, models.Produto.preco_venda).order_by('ano', 'mes')

    resultados = query.all()

    # Processar dados mensais
    tendencias_mensais = []
    for resultado in resultados:
        mes_ano = f"{int(resultado.ano)}-{int(resultado.mes):02d}"
        # Calcular valor usando quantidade total * preço atual
        valor_mensal = float(resultado.quantidade_mensal * resultado.preco_atual)
        tendencia = schemas.TendenciaMensal(
            mes_ano=mes_ano,
            produto_nome=resultado.produto_nome,
            quantidade_vendida=resultado.quantidade_mensal,
            valor_vendido=valor_mensal
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
    Compara performance de vendedores nos produtos mais vendidos.
    Considera apenas movimentações automáticas (exclui correções manuais).
    """

    fim = datetime.now()
    inicio = fim - timedelta(days=periodo_dias)

    allowed_observacoes = _observacao_permitida_expression()
    status_confirmado = _status_confirmado_expression()

    # Query para comparativo de vendedores
    # Nota: Agrupamos por produto primeiro para calcular valor corretamente
    query = db.query(
        models.Usuario.nome.label('vendedor_nome'),
        models.Usuario.id.label('vendedor_id'),
        models.MovimentacaoEstoque.produto_id,
        models.Produto.preco_venda.label('preco_produto'),
        func.sum(models.MovimentacaoEstoque.quantidade).label('quantidade_produto'),
        func.count(models.MovimentacaoEstoque.id).label('num_movimentacoes')
    ).join(
        models.Usuario, models.MovimentacaoEstoque.usuario_id == models.Usuario.id
    ).join(
        models.Produto, models.MovimentacaoEstoque.produto_id == models.Produto.id
    ).filter(
        and_(
            models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
            models.MovimentacaoEstoque.data_movimentacao >= inicio,
            models.MovimentacaoEstoque.data_movimentacao <= fim,
            models.Produto.empresa_id == current_user.empresa_id,
            # Filtrar apenas movimentações automáticas
            or_(
                models.MovimentacaoEstoque.origem.in_(ORIGENS_AUTOMATICAS),
                models.MovimentacaoEstoque.origem.is_(None)  # Incluir movimentações antigas sem origem definida
            ),
            status_confirmado,
            allowed_observacoes
        )
    ).group_by(
        models.Usuario.nome, 
        models.Usuario.id,
        models.MovimentacaoEstoque.produto_id,
        models.Produto.preco_venda
    )

    resultados = query.all()

    # Agrupar resultados por vendedor e calcular totais
    vendedores_dict = {}
    for resultado in resultados:
        vendedor_id = resultado.vendedor_id
        if vendedor_id not in vendedores_dict:
            vendedores_dict[vendedor_id] = {
                'vendedor_id': vendedor_id,
                'vendedor_nome': resultado.vendedor_nome,
                'total_quantidade': 0,
                'total_valor': 0.0,
                'produtos_diferentes': set(),
                'numero_vendas': 0
            }
        
        # Calcular valor: quantidade do produto * preço atual
        valor_produto = float(resultado.quantidade_produto * resultado.preco_produto)
        vendedores_dict[vendedor_id]['total_quantidade'] += resultado.quantidade_produto
        vendedores_dict[vendedor_id]['total_valor'] += valor_produto
        vendedores_dict[vendedor_id]['produtos_diferentes'].add(resultado.produto_id)
        vendedores_dict[vendedor_id]['numero_vendas'] += resultado.num_movimentacoes

    # Converter para lista de schemas
    comparativo = []
    for vendedor_data in vendedores_dict.values():
        numero_vendas = vendedor_data['numero_vendas']
        vendedor = schemas.ComparativoVendedor(
            vendedor_id=vendedor_data['vendedor_id'],
            vendedor_nome=vendedor_data['vendedor_nome'],
            total_quantidade_vendida=vendedor_data['total_quantidade'],
            total_valor_vendido=round(vendedor_data['total_valor'], 2),
            produtos_diferentes_vendidos=len(vendedor_data['produtos_diferentes']),
            numero_vendas=numero_vendas,
            ticket_medio=round(vendedor_data['total_valor'] / max(numero_vendas, 1), 2)
        )
        comparativo.append(vendedor)

    # Ordenar por valor total
    comparativo.sort(key=lambda x: x.total_valor_vendido, reverse=True)

    return comparativo

def _calcular_categoria_mais_vendida(produtos: List[schemas.ProdutoMaisVendidoDetalhado]) -> Optional[str]:
    """Calcula qual categoria teve mais vendas em quantidade"""
    if not produtos:
        return None

    categorias = defaultdict(float)
    for produto in produtos:
        categorias[produto.categoria] += produto.total_quantidade_vendida

    return max(categorias.items(), key=lambda x: x[1])[0] if categorias else None
