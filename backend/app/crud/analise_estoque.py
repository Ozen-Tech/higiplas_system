# /backend/app/crud/analise_estoque.py

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..db import models
from ..schemas import produto as schemas_produto


def calcular_estoque_minimo_por_demanda(
    db: Session, 
    produto_id: int, 
    empresa_id: int,
    dias_analise: int = 90,
    dias_lead_time: int = 7,
    margem_seguranca: float = 1.2
) -> Dict[str, Any]:
    """
    Calcula o estoque mínimo baseado na demanda histórica dos últimos X dias.
    
    Args:
        produto_id: ID do produto
        empresa_id: ID da empresa
        dias_analise: Período de análise da demanda (padrão 90 dias)
        dias_lead_time: Tempo de reposição em dias (padrão 7 dias)
        margem_seguranca: Margem de segurança (padrão 20%)
    
    Returns:
        Dict com análise completa do estoque mínimo
    """
    
    # Verifica se o produto existe e pertence à empresa
    produto = db.query(models.Produto).filter(
        models.Produto.id == produto_id,
        models.Produto.empresa_id == empresa_id
    ).first()
    
    if not produto:
        return {"erro": "Produto não encontrado"}
    
    # Data limite para análise
    data_limite = datetime.now() - timedelta(days=dias_analise)
    
    # Busca todas as saídas (vendas) do produto no período
    saidas = db.query(models.MovimentacaoEstoque).filter(
        models.MovimentacaoEstoque.produto_id == produto_id,
        models.MovimentacaoEstoque.tipo_movimentacao == "SAIDA",
        models.MovimentacaoEstoque.data_movimentacao >= data_limite
    ).all()
    
    if not saidas:
        return {
            "produto_nome": produto.nome,
            "estoque_atual": produto.quantidade_em_estoque,
            "estoque_minimo_atual": produto.estoque_minimo,
            "estoque_minimo_sugerido": produto.estoque_minimo or 5,
            "demanda_media_diaria": 0,
            "total_vendido_periodo": 0,
            "dias_com_vendas": 0,
            "observacao": "Sem histórico de vendas no período analisado"
        }
    
    # Calcula estatísticas de demanda
    total_vendido = sum(saida.quantidade for saida in saidas)
    demanda_media_diaria = total_vendido / dias_analise
    
    # Agrupa vendas por dia para calcular variabilidade
    vendas_por_dia = {}
    for saida in saidas:
        data_str = saida.data_movimentacao.date().isoformat()
        if data_str not in vendas_por_dia:
            vendas_por_dia[data_str] = 0
        vendas_por_dia[data_str] += saida.quantidade
    
    dias_com_vendas = len(vendas_por_dia)
    
    # Calcula demanda máxima diária
    demanda_maxima_diaria = max(vendas_por_dia.values()) if vendas_por_dia else 0
    
    # Fórmula do estoque mínimo: (Demanda média diária * Lead time) * Margem de segurança
    estoque_minimo_calculado = (demanda_media_diaria * dias_lead_time) * margem_seguranca
    estoque_minimo_sugerido = max(int(estoque_minimo_calculado), 1)  # Mínimo de 1 unidade
    
    # Análise de risco
    dias_cobertura_atual = produto.quantidade_em_estoque / demanda_media_diaria if demanda_media_diaria > 0 else float('inf')
    
    status_estoque = "CRÍTICO" if dias_cobertura_atual < dias_lead_time else "BAIXO" if dias_cobertura_atual < (dias_lead_time * 2) else "ADEQUADO"
    
    return {
        "produto_nome": produto.nome,
        "produto_codigo": produto.codigo,
        "estoque_atual": produto.quantidade_em_estoque,
        "estoque_minimo_atual": produto.estoque_minimo,
        "estoque_minimo_sugerido": estoque_minimo_sugerido,
        "demanda_media_diaria": round(demanda_media_diaria, 2),
        "demanda_maxima_diaria": demanda_maxima_diaria,
        "total_vendido_periodo": total_vendido,
        "dias_com_vendas": dias_com_vendas,
        "dias_cobertura_atual": round(dias_cobertura_atual, 1) if dias_cobertura_atual != float('inf') else "Infinito",
        "status_estoque": status_estoque,
        "lead_time_usado": dias_lead_time,
        "margem_seguranca_usado": margem_seguranca,
        "periodo_analise_dias": dias_analise
    }


def analisar_todos_produtos_estoque_minimo(
    db: Session, 
    empresa_id: int,
    dias_analise: int = 90
) -> List[Dict[str, Any]]:
    """
    Analisa o estoque mínimo de todos os produtos da empresa.
    """
    
    produtos = db.query(models.Produto).filter(
        models.Produto.empresa_id == empresa_id
    ).all()
    
    resultados = []
    
    for produto in produtos:
        analise = calcular_estoque_minimo_por_demanda(
            db=db,
            produto_id=produto.id,
            empresa_id=empresa_id,
            dias_analise=dias_analise
        )
        resultados.append(analise)
    
    # Ordena por status crítico primeiro
    resultados.sort(key=lambda x: (
        0 if x.get('status_estoque') == 'CRÍTICO' else
        1 if x.get('status_estoque') == 'BAIXO' else 2
    ))
    
    return resultados


def obter_produtos_alta_rotatividade(
    db: Session, 
    empresa_id: int,
    dias: int = 30,
    limite: int = 10
) -> List[Dict[str, Any]]:
    """
    Identifica produtos com alta rotatividade (mais vendidos) no período.
    """
    
    data_limite = datetime.now() - timedelta(days=dias)
    
    # Query para somar as saídas por produto
    resultado = db.query(
        models.Produto.id,
        models.Produto.nome,
        models.Produto.codigo,
        models.Produto.quantidade_em_estoque,
        models.Produto.estoque_minimo,
        func.sum(models.MovimentacaoEstoque.quantidade).label('total_vendido')
    ).join(
        models.MovimentacaoEstoque,
        models.Produto.id == models.MovimentacaoEstoque.produto_id
    ).filter(
        models.Produto.empresa_id == empresa_id,
        models.MovimentacaoEstoque.tipo_movimentacao == "SAIDA",
        models.MovimentacaoEstoque.data_movimentacao >= data_limite
    ).group_by(
        models.Produto.id,
        models.Produto.nome,
        models.Produto.codigo,
        models.Produto.quantidade_em_estoque,
        models.Produto.estoque_minimo
    ).order_by(
        desc('total_vendido')
    ).limit(limite).all()
    
    produtos_alta_rotatividade = []
    
    for item in resultado:
        rotatividade_diaria = item.total_vendido / dias
        dias_cobertura = item.quantidade_em_estoque / rotatividade_diaria if rotatividade_diaria > 0 else float('inf')
        
        produtos_alta_rotatividade.append({
            "produto_id": item.id,
            "nome": item.nome,
            "codigo": item.codigo,
            "estoque_atual": item.quantidade_em_estoque,
            "estoque_minimo": item.estoque_minimo,
            "total_vendido_periodo": item.total_vendido,
            "rotatividade_diaria": round(rotatividade_diaria, 2),
            "dias_cobertura": round(dias_cobertura, 1) if dias_cobertura != float('inf') else "Infinito",
            "periodo_dias": dias
        })
    
    return produtos_alta_rotatividade


def obter_produtos_sem_movimento(
    db: Session, 
    empresa_id: int,
    dias: int = 60
) -> List[Dict[str, Any]]:
    """
    Identifica produtos sem movimento (vendas) no período especificado.
    """
    
    data_limite = datetime.now() - timedelta(days=dias)
    
    # Subquery para produtos com movimento no período
    produtos_com_movimento = db.query(
        models.MovimentacaoEstoque.produto_id
    ).filter(
        models.MovimentacaoEstoque.tipo_movimentacao == "SAIDA",
        models.MovimentacaoEstoque.data_movimentacao >= data_limite
    ).subquery()
    
    # Produtos sem movimento
    produtos_sem_movimento = db.query(models.Produto).filter(
        models.Produto.empresa_id == empresa_id,
        ~models.Produto.id.in_(produtos_com_movimento)
    ).all()
    
    resultado = []
    
    for produto in produtos_sem_movimento:
        # Busca a última movimentação de saída
        ultima_saida = db.query(models.MovimentacaoEstoque).filter(
            models.MovimentacaoEstoque.produto_id == produto.id,
            models.MovimentacaoEstoque.tipo_movimentacao == "SAIDA"
        ).order_by(
            desc(models.MovimentacaoEstoque.data_movimentacao)
        ).first()
        
        dias_sem_movimento = None
        if ultima_saida:
            dias_sem_movimento = (datetime.now() - ultima_saida.data_movimentacao).days
        
        resultado.append({
            "produto_id": produto.id,
            "nome": produto.nome,
            "codigo": produto.codigo,
            "estoque_atual": produto.quantidade_em_estoque,
            "valor_estoque": produto.quantidade_em_estoque * (produto.preco_custo or 0),
            "dias_sem_movimento": dias_sem_movimento,
            "ultima_venda": ultima_saida.data_movimentacao.isoformat() if ultima_saida else None
        })
    
    # Ordena por valor de estoque (maior primeiro)
    resultado.sort(key=lambda x: x['valor_estoque'], reverse=True)
    
    return resultado


def gerar_relatorio_completo_estoque(
    db: Session, 
    empresa_id: int
) -> Dict[str, Any]:
    """
    Gera um relatório completo de análise de estoque.
    """
    
    # Análises individuais
    analise_estoque_minimo = analisar_todos_produtos_estoque_minimo(db, empresa_id)
    produtos_alta_rotatividade = obter_produtos_alta_rotatividade(db, empresa_id)
    produtos_sem_movimento = obter_produtos_sem_movimento(db, empresa_id)
    
    # Estatísticas gerais
    total_produtos = db.query(models.Produto).filter(
        models.Produto.empresa_id == empresa_id
    ).count()
    
    produtos_criticos = len([p for p in analise_estoque_minimo if p.get('status_estoque') == 'CRÍTICO'])
    produtos_baixo_estoque = len([p for p in analise_estoque_minimo if p.get('status_estoque') == 'BAIXO'])
    
    valor_total_estoque = db.query(
        func.sum(models.Produto.quantidade_em_estoque * models.Produto.preco_custo)
    ).filter(
        models.Produto.empresa_id == empresa_id,
        models.Produto.preco_custo.isnot(None)
    ).scalar() or 0
    
    return {
        "resumo": {
            "total_produtos": total_produtos,
            "produtos_criticos": produtos_criticos,
            "produtos_baixo_estoque": produtos_baixo_estoque,
            "produtos_sem_movimento_60_dias": len(produtos_sem_movimento),
            "valor_total_estoque": round(valor_total_estoque, 2)
        },
        "analise_estoque_minimo": analise_estoque_minimo[:20],  # Top 20
        "produtos_alta_rotatividade": produtos_alta_rotatividade,
        "produtos_sem_movimento": produtos_sem_movimento[:10],  # Top 10 por valor
        "data_analise": datetime.now().isoformat()
    }