# backend/app/crud/proposta_detalhada.py

import secrets
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from ..schemas import proposta_detalhada as schemas
from ..db import models
from ..core.logger import app_logger

logger = app_logger


def _resolver_itens_entrada(
    proposta_in: schemas.PropostaDetalhadaBase,
) -> List[schemas.PropostaDetalhadaItemCreate]:
    """Garante que exista ao menos um item, convertendo dados legados quando necessário."""
    itens = getattr(proposta_in, "itens", None)
    if itens:
        return list(itens)

    if (
        getattr(proposta_in, "produto_id", None) is None
        or getattr(proposta_in, "quantidade_produto", None) is None
    ):
        raise ValueError("É necessário informar ao menos um produto para a proposta detalhada.")

    logger.warning("Usando modo legado de criação de proposta detalhada (um único item).")
    item_legado = schemas.PropostaDetalhadaItemCreate(
        produto_id=proposta_in.produto_id,  # type: ignore[arg-type]
        quantidade_produto=proposta_in.quantidade_produto,  # type: ignore[arg-type]
        dilucao_aplicada=proposta_in.dilucao_aplicada,
        dilucao_numerador=proposta_in.dilucao_numerador,
        dilucao_denominador=proposta_in.dilucao_denominador,
    )
    return [item_legado]


def _montar_itens_calculados(
    db: Session,
    itens_input: List[schemas.PropostaDetalhadaItemCreate],
) -> dict:
    """Calcula rendimentos/custos dos itens e retorna contexto para persistência."""
    if not itens_input:
        raise ValueError("Envie ao menos um item para montar a proposta detalhada.")

    produto_ids = {item.produto_id for item in itens_input}
    produtos = db.query(models.Produto).filter(models.Produto.id.in_(produto_ids)).all()
    produtos_map = {produto.id: produto for produto in produtos}

    if len(produtos_map) != len(produto_ids):
        ids_encontrados = set(produtos_map.keys())
        ids_faltantes = produto_ids - ids_encontrados
        raise ValueError(f"Produtos não encontrados: {', '.join(map(str, ids_faltantes))}")

    itens_payload = []
    primeiro_item_resumo = None
    primeiro_produto = None
    ficha_tecnica_id = None

    for ordem, item in enumerate(itens_input, start=1):
        produto = produtos_map[item.produto_id]

        ficha_tecnica = (
            db.query(models.FichaTecnica)
            .filter(models.FichaTecnica.produto_id == item.produto_id)
            .first()
        )

        if ordem == 1:
            primeiro_produto = produto
            if ficha_tecnica:
                ficha_tecnica_id = ficha_tecnica.id

        dilucao_num = item.dilucao_numerador or (ficha_tecnica.dilucao_numerador if ficha_tecnica else None)
        dilucao_den = item.dilucao_denominador or (ficha_tecnica.dilucao_denominador if ficha_tecnica else None)
        dilucao_aplicada = item.dilucao_aplicada
        if not dilucao_aplicada and dilucao_num and dilucao_den:
            dilucao_aplicada = f"{dilucao_num:g}:{dilucao_den:g}"

        rendimento = calcular_rendimento(
            item.quantidade_produto,
            dilucao_num,
            dilucao_den,
        )
        custo = calcular_custo_por_litro(
            produto.preco_venda if produto.preco_venda is not None else 0,
            item.quantidade_produto,
            rendimento,
        )

        item_payload = {
            "produto_id": item.produto_id,
            "quantidade_produto": item.quantidade_produto,
            "dilucao_aplicada": dilucao_aplicada,
            "dilucao_numerador": dilucao_num,
            "dilucao_denominador": dilucao_den,
            "rendimento_total_litros": rendimento,
            "preco_produto": produto.preco_venda,
            "custo_por_litro_final": custo,
            "observacoes": item.observacoes,
            "ordem": item.ordem or ordem,
            "concorrente_nome_manual": item.concorrente_nome_manual,
            "concorrente_rendimento_manual": item.concorrente_rendimento_manual,
            "concorrente_custo_por_litro_manual": item.concorrente_custo_por_litro_manual,
        }

        if primeiro_item_resumo is None:
            primeiro_item_resumo = item_payload

        itens_payload.append(item_payload)

    return {
        "itens": itens_payload,
        "primeiro_item": primeiro_item_resumo,
        "primeiro_produto": primeiro_produto,
        "ficha_tecnica_id": ficha_tecnica_id,
        "produtos_map": produtos_map,
    }


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
    itens_input = _resolver_itens_entrada(proposta_in)
    contexto_itens = _montar_itens_calculados(db, itens_input)
    primeiro_item = contexto_itens["primeiro_item"]
    produto_principal: models.Produto = contexto_itens["primeiro_produto"]

    rendimento_total = primeiro_item.get("rendimento_total_litros")
    custo_por_litro = primeiro_item.get("custo_por_litro_final")

    comparacoes = []
    if rendimento_total and custo_por_litro:
        comparacoes = comparar_com_concorrentes(
            db,
            primeiro_item["produto_id"],
            rendimento_total,
            custo_por_litro,
            produto_principal.categoria if produto_principal else None,
        )

    melhor_comparacao = comparacoes[0] if comparacoes else None

    proposta_data = {
        "orcamento_id": proposta_in.orcamento_id,
        "cliente_id": proposta_in.cliente_id,
        "vendedor_id": vendedor_id,
        "observacoes": proposta_in.observacoes,
        "compartilhavel": proposta_in.compartilhavel,
        "token_compartilhamento": secrets.token_urlsafe(32)
        if proposta_in.compartilhavel
        else None,
        "produto_id": primeiro_item["produto_id"],
        "quantidade_produto": primeiro_item["quantidade_produto"],
        "dilucao_aplicada": primeiro_item["dilucao_aplicada"],
        "dilucao_numerador": primeiro_item["dilucao_numerador"],
        "dilucao_denominador": primeiro_item["dilucao_denominador"],
        "rendimento_total_litros": rendimento_total,
        "preco_produto": primeiro_item.get("preco_produto"),
        "custo_por_litro_final": custo_por_litro,
        "ficha_tecnica_id": contexto_itens["ficha_tecnica_id"],
    }

    if melhor_comparacao:
        proposta_data["concorrente_id"] = melhor_comparacao.concorrente_id
        proposta_data["economia_percentual"] = melhor_comparacao.economia_percentual
        proposta_data["economia_valor"] = melhor_comparacao.economia_valor
        proposta_data["economia_vs_concorrente"] = melhor_comparacao.economia_percentual

    db_proposta = models.PropostaDetalhada(
        **{k: v for k, v in proposta_data.items() if v is not None}
    )
    db.add(db_proposta)
    db.flush()  # Garante ID para relacionamentos

    # Persistir itens
    for item_payload in contexto_itens["itens"]:
        db.add(
            models.PropostaDetalhadaItem(
                proposta_id=db_proposta.id,
                **item_payload,
            )
        )

    # Comparações manuais
    if proposta_in.comparacoes_personalizadas:
        for ordem, comp in enumerate(proposta_in.comparacoes_personalizadas, start=1):
            db.add(
                models.PropostaConcorrenteManual(
                    proposta_id=db_proposta.id,
                    nome=comp.nome,
                    rendimento_litro=comp.rendimento_litro,
                    custo_por_litro=comp.custo_por_litro,
                    observacoes=comp.observacoes,
                    ordem=comp.ordem or ordem,
                )
            )

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
            joinedload(models.PropostaDetalhada.concorrente),
            joinedload(models.PropostaDetalhada.itens).joinedload(models.PropostaDetalhadaItem.produto),
            joinedload(models.PropostaDetalhada.concorrentes_personalizados),
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
    
    itens_atualizados = getattr(proposta_update, "itens", None)
    if itens_atualizados is not None:
        contexto_itens = _montar_itens_calculados(db, itens_atualizados)
        primeiro_item = contexto_itens["primeiro_item"]
        produto_principal: models.Produto = contexto_itens["primeiro_produto"]

        # Limpa itens atuais e adiciona novos
        db_proposta.itens.clear()
        for item_payload in contexto_itens["itens"]:
            db_proposta.itens.append(models.PropostaDetalhadaItem(**item_payload))

        db_proposta.produto_id = primeiro_item["produto_id"]
        db_proposta.quantidade_produto = primeiro_item["quantidade_produto"]
        db_proposta.dilucao_aplicada = primeiro_item["dilucao_aplicada"]
        db_proposta.dilucao_numerador = primeiro_item["dilucao_numerador"]
        db_proposta.dilucao_denominador = primeiro_item["dilucao_denominador"]
        db_proposta.rendimento_total_litros = primeiro_item.get("rendimento_total_litros")
        db_proposta.preco_produto = primeiro_item.get("preco_produto")
        db_proposta.custo_por_litro_final = primeiro_item.get("custo_por_litro_final")
        db_proposta.ficha_tecnica_id = contexto_itens["ficha_tecnica_id"]

        rendimento_total = primeiro_item.get("rendimento_total_litros")
        custo_por_litro = primeiro_item.get("custo_por_litro_final")
        if rendimento_total and custo_por_litro:
            comparacoes = comparar_com_concorrentes(
                db,
                primeiro_item["produto_id"],
                rendimento_total,
                custo_por_litro,
                produto_principal.categoria if produto_principal else None,
            )
            melhor_comparacao = comparacoes[0] if comparacoes else None
        else:
            melhor_comparacao = None

        if melhor_comparacao:
            db_proposta.concorrente_id = melhor_comparacao.concorrente_id
            db_proposta.economia_percentual = melhor_comparacao.economia_percentual
            db_proposta.economia_valor = melhor_comparacao.economia_valor
            db_proposta.economia_vs_concorrente = melhor_comparacao.economia_percentual
        else:
            db_proposta.concorrente_id = None
            db_proposta.economia_percentual = None
            db_proposta.economia_valor = None
            db_proposta.economia_vs_concorrente = None

    # Atualizar comparações manuais
    if proposta_update.comparacoes_personalizadas is not None:
        db.query(models.PropostaConcorrenteManual).filter(
            models.PropostaConcorrenteManual.proposta_id == db_proposta.id
        ).delete(synchronize_session=False)
        for ordem, comp in enumerate(proposta_update.comparacoes_personalizadas, start=1):
            db.add(
                models.PropostaConcorrenteManual(
                    proposta_id=db_proposta.id,
                    nome=comp.nome,
                    rendimento_litro=comp.rendimento_litro,
                    custo_por_litro=comp.custo_por_litro,
                    observacoes=comp.observacoes,
                    ordem=comp.ordem or ordem,
                )
            )

    campos_simples = proposta_update.model_dump(
        exclude_unset=True,
        exclude={"itens", "comparacoes_personalizadas"},
    )
    for key, value in campos_simples.items():
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

