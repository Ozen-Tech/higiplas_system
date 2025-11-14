# backend/app/crud/proposta_detalhada.py

import secrets
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from ..schemas import proposta_detalhada as schemas
from ..db import models
from ..core.logger import app_logger

logger = app_logger


def calcular_rendimento(
    quantidade_produto: float,
    dilucao_numerador: Optional[float],
    dilucao_denominador: Optional[float]
) -> Optional[float]:
    """
    Calcula o rendimento total em litros baseado na quantidade e diluição.
    Ex: 1 litro com diluição 1:10 = 10 litros finais
    """
    if not dilucao_numerador or not dilucao_denominador or dilucao_numerador == 0:
        return None
    
    # Rendimento = quantidade * (denominador / numerador)
    rendimento = quantidade_produto * (dilucao_denominador / dilucao_numerador)
    return rendimento


def calcular_custo_por_litro(
    preco_produto: float,
    quantidade_produto: float,
    rendimento_total: Optional[float]
) -> Optional[float]:
    """Calcula o custo por litro da solução final"""
    if not rendimento_total or rendimento_total == 0:
        return None
    
    custo_total = preco_produto * quantidade_produto
    return custo_total / rendimento_total


def comparar_com_concorrentes(
    db: Session,
    produto_id: int,
    rendimento_total: float,
    custo_por_litro: float,
    categoria: Optional[str] = None
) -> List[schemas.ComparacaoConcorrente]:
    """
    Compara o produto Girassol com concorrentes similares.
    Retorna lista de comparações com economia calculada.
    """
    # Buscar produto para obter categoria
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        return []
    
    # Buscar concorrentes da mesma categoria ou todos se categoria não especificada
    query = db.query(models.ProdutoConcorrente).filter(
        models.ProdutoConcorrente.ativo == True
    )
    
    if categoria or produto.categoria:
        cat = categoria or produto.categoria
        query = query.filter(models.ProdutoConcorrente.categoria == cat)
    
    concorrentes = query.all()
    
    comparacoes = []
    for concorrente in concorrentes:
        # Calcular custo por litro do concorrente
        if concorrente.preco_medio and concorrente.rendimento_litro:
            custo_concorrente = concorrente.preco_medio / concorrente.rendimento_litro
        elif concorrente.preco_medio and concorrente.dilucao_numerador and concorrente.dilucao_denominador:
            # Calcular rendimento do concorrente
            rend_concorrente = concorrente.dilucao_denominador / concorrente.dilucao_numerador
            custo_concorrente = concorrente.preco_medio / rend_concorrente if rend_concorrente > 0 else None
        else:
            custo_concorrente = None
        
        if custo_concorrente and custo_por_litro:
            # Calcular economia
            economia_valor = custo_concorrente - custo_por_litro
            economia_percentual = (economia_valor / custo_concorrente) * 100 if custo_concorrente > 0 else 0
            
            comparacao = schemas.ComparacaoConcorrente(
                concorrente_id=concorrente.id,
                concorrente_nome=concorrente.nome,
                concorrente_marca=concorrente.marca,
                preco_concorrente=concorrente.preco_medio,
                rendimento_concorrente=concorrente.rendimento_litro,
                custo_por_litro_concorrente=custo_concorrente,
                economia_percentual=round(economia_percentual, 2),
                economia_valor=round(economia_valor, 2)
            )
            comparacoes.append(comparacao)
    
    # Ordenar por maior economia
    comparacoes.sort(key=lambda x: x.economia_percentual or 0, reverse=True)
    return comparacoes


def create_proposta_detalhada(
    db: Session,
    proposta_in: schemas.PropostaDetalhadaCreate,
    vendedor_id: int
) -> models.PropostaDetalhada:
    """
    Cria uma proposta detalhada com cálculos automáticos.
    """
    # Buscar produto para obter preço
    produto = db.query(models.Produto).filter(models.Produto.id == proposta_in.produto_id).first()
    if not produto:
        raise ValueError(f"Produto {proposta_in.produto_id} não encontrado")
    
    # Buscar ficha técnica do produto
    ficha_tecnica = db.query(models.FichaTecnica).filter(
        models.FichaTecnica.produto_id == proposta_in.produto_id
    ).first()
    
    # Se não tem ficha técnica vinculada ao produto, usar dados da proposta
    dilucao_num = proposta_in.dilucao_numerador
    dilucao_den = proposta_in.dilucao_denominador
    
    if ficha_tecnica:
        if not dilucao_num:
            dilucao_num = ficha_tecnica.dilucao_numerador
        if not dilucao_den:
            dilucao_den = ficha_tecnica.dilucao_denominador
    
    # Calcular rendimento
    rendimento_total = calcular_rendimento(
        proposta_in.quantidade_produto,
        dilucao_num,
        dilucao_den
    )
    
    # Calcular custo por litro
    custo_por_litro = calcular_custo_por_litro(
        produto.preco_venda,
        proposta_in.quantidade_produto,
        rendimento_total
    )
    
    # Comparar com concorrentes
    comparacoes = []
    if rendimento_total and custo_por_litro:
        comparacoes = comparar_com_concorrentes(
            db,
            proposta_in.produto_id,
            rendimento_total,
            custo_por_litro,
            produto.categoria
        )
    
    # Pegar melhor comparação (maior economia)
    melhor_comparacao = comparacoes[0] if comparacoes else None
    
    # Criar proposta
    proposta_data = proposta_in.model_dump()
    proposta_data['vendedor_id'] = vendedor_id
    proposta_data['ficha_tecnica_id'] = ficha_tecnica.id if ficha_tecnica else None
    proposta_data['rendimento_total_litros'] = rendimento_total
    proposta_data['preco_produto'] = produto.preco_venda
    proposta_data['custo_por_litro_final'] = custo_por_litro
    proposta_data['dilucao_numerador'] = dilucao_num
    proposta_data['dilucao_denominador'] = dilucao_den
    
    if melhor_comparacao:
        proposta_data['concorrente_id'] = melhor_comparacao.concorrente_id
        proposta_data['economia_percentual'] = melhor_comparacao.economia_percentual
        proposta_data['economia_valor'] = melhor_comparacao.economia_valor
        proposta_data['economia_vs_concorrente'] = melhor_comparacao.economia_percentual
    
    # Gerar token de compartilhamento se solicitado
    if proposta_data.get('compartilhavel'):
        proposta_data['token_compartilhamento'] = secrets.token_urlsafe(32)
    
    db_proposta = models.PropostaDetalhada(**proposta_data)
    db.add(db_proposta)
    db.commit()
    db.refresh(db_proposta)
    
    return db_proposta


def get_proposta_by_id(
    db: Session,
    proposta_id: int,
    incluir_relacionamentos: bool = True
) -> Optional[models.PropostaDetalhada]:
    """Busca uma proposta por ID"""
    query = db.query(models.PropostaDetalhada)
    
    if incluir_relacionamentos:
        query = query.options(
            joinedload(models.PropostaDetalhada.produto),
            joinedload(models.PropostaDetalhada.cliente),
            joinedload(models.PropostaDetalhada.vendedor),
            joinedload(models.PropostaDetalhada.ficha_tecnica),
            joinedload(models.PropostaDetalhada.concorrente)
        )
    
    return query.filter(models.PropostaDetalhada.id == proposta_id).first()


def get_propostas_by_vendedor(
    db: Session,
    vendedor_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.PropostaDetalhada]:
    """Lista propostas de um vendedor"""
    return db.query(models.PropostaDetalhada).filter(
        models.PropostaDetalhada.vendedor_id == vendedor_id
    ).order_by(models.PropostaDetalhada.data_criacao.desc()).offset(skip).limit(limit).all()


def get_propostas_by_cliente(
    db: Session,
    cliente_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.PropostaDetalhada]:
    """Lista propostas de um cliente"""
    return db.query(models.PropostaDetalhada).filter(
        models.PropostaDetalhada.cliente_id == cliente_id
    ).order_by(models.PropostaDetalhada.data_criacao.desc()).offset(skip).limit(limit).all()


def get_all_propostas(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[models.PropostaDetalhada]:
    """Lista todas as propostas (admin)"""
    return db.query(models.PropostaDetalhada).order_by(
        models.PropostaDetalhada.data_criacao.desc()
    ).offset(skip).limit(limit).all()


def get_proposta_by_token(
    db: Session,
    token: str
) -> Optional[models.PropostaDetalhada]:
    """Busca proposta por token de compartilhamento"""
    return db.query(models.PropostaDetalhada).filter(
        models.PropostaDetalhada.token_compartilhamento == token,
        models.PropostaDetalhada.compartilhavel == True
    ).first()


def update_proposta_detalhada(
    db: Session,
    proposta_id: int,
    proposta_update: schemas.PropostaDetalhadaUpdate
) -> Optional[models.PropostaDetalhada]:
    """Atualiza uma proposta detalhada"""
    db_proposta = db.query(models.PropostaDetalhada).filter(
        models.PropostaDetalhada.id == proposta_id
    ).first()
    
    if not db_proposta:
        return None
    
    update_data = proposta_update.model_dump(exclude_unset=True)
    
    # Recalcular se quantidade ou diluição mudaram
    if 'quantidade_produto' in update_data or 'dilucao_numerador' in update_data or 'dilucao_denominador' in update_data:
        quantidade = update_data.get('quantidade_produto', db_proposta.quantidade_produto)
        dilucao_num = update_data.get('dilucao_numerador', db_proposta.dilucao_numerador)
        dilucao_den = update_data.get('dilucao_denominador', db_proposta.dilucao_denominador)
        
        rendimento = calcular_rendimento(quantidade, dilucao_num, dilucao_den)
        update_data['rendimento_total_litros'] = rendimento
        
        if db_proposta.preco_produto:
            custo = calcular_custo_por_litro(
                db_proposta.preco_produto,
                quantidade,
                rendimento
            )
            update_data['custo_por_litro_final'] = custo
    
    for key, value in update_data.items():
        setattr(db_proposta, key, value)
    
    db.commit()
    db.refresh(db_proposta)
    return db_proposta


def delete_proposta_detalhada(db: Session, proposta_id: int) -> bool:
    """Deleta uma proposta detalhada"""
    db_proposta = db.query(models.PropostaDetalhada).filter(
        models.PropostaDetalhada.id == proposta_id
    ).first()
    
    if not db_proposta:
        return False
    
    db.delete(db_proposta)
    db.commit()
    return True

