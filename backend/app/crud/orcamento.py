# /backend/app/crud/orcamento.py - VERSÃO PROFISSIONAL COM SOLID

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Type
from sqlalchemy.exc import SQLAlchemyError

from app.db import models
from app.schemas import orcamento as schemas_orcamento
from app.core.validators import OrcamentoValidator, StockValidator
from app.core.exceptions import BusinessRuleException
from app.core.constants import OrcamentoStatus, OrigemMovimentacao, TipoMovimentacao
from app.core.logger import orcamento_logger

def create_orcamento(db: Session, orcamento_in: schemas_orcamento.OrcamentoCreate, vendedor_id: int) -> models.Orcamento:
    """Cria um novo orçamento com seus itens."""
    
    db_orcamento = models.Orcamento(
        cliente_id=orcamento_in.cliente_id,
        usuario_id=vendedor_id,
        status=orcamento_in.status,
        condicao_pagamento=orcamento_in.condicao_pagamento
    )
    db.add(db_orcamento)
    db.flush()

    for item_in in orcamento_in.itens:
        db_item = models.OrcamentoItem(
            orcamento_id=db_orcamento.id,
            produto_id=item_in.produto_id,
            quantidade=item_in.quantidade,
            preco_unitario_congelado=item_in.preco_unitario
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_orcamento)
    return db_orcamento

def get_orcamentos_by_vendedor(db: Session, vendedor_id: int) -> List[models.Orcamento]:
    """
    Lista todos os orçamentos criados por um vendedor específico,
    carregando os dados relacionados e IGNORANDO registros órfãos.
    """
    return db.query(models.Orcamento).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.usuario),
        joinedload(models.Orcamento.itens).joinedload(models.OrcamentoItem.produto)
    ).filter(
        models.Orcamento.usuario_id == vendedor_id,
        # ===== CORREÇÃO FINAL =====
        # Adiciona um filtro para garantir que o orçamento tenha um cliente.
        # Isso previne o erro 500 se houver dados inválidos no banco.
        models.Orcamento.cliente_id.isnot(None)
    ).order_by(
        models.Orcamento.data_criacao.desc()
    ).all()

def get_all_orcamentos(db: Session, empresa_id: Optional[int] = None) -> List[models.Orcamento]:
    """
    Lista todos os orçamentos do sistema (apenas para admin).
    Se empresa_id for fornecido, filtra por empresa.
    """
    query = db.query(models.Orcamento).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.usuario),
        joinedload(models.Orcamento.itens).joinedload(models.OrcamentoItem.produto)
    ).filter(
        models.Orcamento.cliente_id.isnot(None)
    )
    
    if empresa_id:
        query = query.join(models.Usuario).filter(
            models.Usuario.empresa_id == empresa_id
        )
    
    return query.order_by(
        models.Orcamento.data_criacao.desc()
    ).all()

def get_orcamento_by_id(db: Session, orcamento_id: int) -> Optional[models.Orcamento]:
    """
    Busca um orçamento específico por ID com todos os dados relacionados.
    """
    return db.query(models.Orcamento).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.usuario),
        joinedload(models.Orcamento.itens).joinedload(models.OrcamentoItem.produto)
    ).filter(
        models.Orcamento.id == orcamento_id
    ).first()

def _update_orcamento_fields(
    db: Session,
    orcamento: models.Orcamento,
    orcamento_update: schemas_orcamento.OrcamentoUpdate
) -> None:
    """
    Atualiza os campos básicos de um orçamento.
    
    Args:
        db: Sessão do banco de dados
        orcamento: Orçamento a ser atualizado
        orcamento_update: Dados de atualização
    """
    if orcamento_update.cliente_id is not None:
        orcamento.cliente_id = orcamento_update.cliente_id
    if orcamento_update.condicao_pagamento is not None:
        orcamento.condicao_pagamento = orcamento_update.condicao_pagamento
    if orcamento_update.status is not None:
        # Validar transição de status se necessário
        if orcamento.status != orcamento_update.status:
            OrcamentoValidator.validar_status_transicao(
                status_atual=orcamento.status,
                novo_status=orcamento_update.status
            )
        orcamento.status = orcamento_update.status


def _update_orcamento_items(
    db: Session,
    orcamento: models.Orcamento,
    itens_update: List[schemas_orcamento.OrcamentoItemUpdate]
) -> None:
    """
    Atualiza os itens de um orçamento.
    
    Remove itens antigos e adiciona os novos.
    
    Args:
        db: Sessão do banco de dados
        orcamento: Orçamento a ser atualizado
        itens_update: Lista de novos itens
    """
    # Remover itens antigos
    for item in orcamento.itens:
        db.delete(item)
    
    # Adicionar novos itens
    for item_update in itens_update:
        db_item = models.OrcamentoItem(
            orcamento_id=orcamento.id,
            produto_id=item_update.produto_id,
            quantidade=item_update.quantidade,
            preco_unitario_congelado=item_update.preco_unitario
        )
        db.add(db_item)


def update_orcamento(
    db: Session,
    orcamento_id: int,
    orcamento_update: schemas_orcamento.OrcamentoUpdate
) -> models.Orcamento:
    """
    Atualiza um orçamento existente (apenas admin).
    
    Permite atualizar cliente, condição de pagamento, status e itens.
    Segue o princípio de responsabilidade única, delegando atualizações
    para funções específicas.
    
    Args:
        db: Sessão do banco de dados
        orcamento_id: ID do orçamento a ser atualizado
        orcamento_update: Dados de atualização
        
    Returns:
        Orçamento atualizado com dados completos
        
    Raises:
        NotFoundError: Se orçamento não existir
        OrcamentoStatusError: Se transição de status for inválida
        BusinessRuleException: Se houver erro ao atualizar
    """
    orcamento_logger.info(
        f"Iniciando atualização do orçamento #{orcamento_id}",
        extra={"orcamento_id": orcamento_id}
    )
    
    try:
        # Validar que orçamento existe
        orcamento = OrcamentoValidator.validar_orcamento_existe(db, orcamento_id)
        
        # Atualizar campos básicos
        _update_orcamento_fields(db, orcamento, orcamento_update)
        
        # Atualizar itens se fornecidos
        if orcamento_update.itens is not None:
            _update_orcamento_items(db, orcamento, orcamento_update.itens)
        
        # Commit das alterações
        db.commit()
        db.refresh(orcamento)
        
        # Retornar com dados completos
        orcamento_atualizado = get_orcamento_by_id(db, orcamento_id)
        
        orcamento_logger.info(
            f"Orçamento #{orcamento_id} atualizado com sucesso",
            extra={"orcamento_id": orcamento_id}
        )
        
        return orcamento_atualizado
        
    except (NotFoundError, OrcamentoStatusError):
        # Re-raise exceções de negócio
        raise
    except SQLAlchemyError as e:
        db.rollback()
        orcamento_logger.error(
            f"Erro de banco de dados ao atualizar orçamento #{orcamento_id}: {str(e)}",
            extra={"orcamento_id": orcamento_id},
            exc_info=True
        )
        raise BusinessRuleException(f"Erro ao atualizar orçamento: {str(e)}")
    except Exception as e:
        db.rollback()
        orcamento_logger.error(
            f"Erro inesperado ao atualizar orçamento #{orcamento_id}: {str(e)}",
            extra={"orcamento_id": orcamento_id},
            exc_info=True
        )
        raise BusinessRuleException(f"Erro inesperado ao atualizar orçamento: {str(e)}")

def update_orcamento_status(
    db: Session,
    orcamento_id: int,
    novo_status: str
) -> models.Orcamento:
    """
    Atualiza apenas o status de um orçamento.
    
    Args:
        db: Sessão do banco de dados
        orcamento_id: ID do orçamento
        novo_status: Novo status a ser definido
        
    Returns:
        Orçamento atualizado
        
    Raises:
        NotFoundError: Se orçamento não existir
        OrcamentoStatusError: Se transição de status for inválida
        BusinessRuleException: Se houver erro ao atualizar
    """
    orcamento_logger.info(
        f"Atualizando status do orçamento #{orcamento_id} para '{novo_status}'",
        extra={"orcamento_id": orcamento_id, "novo_status": novo_status}
    )
    
    try:
        # Validar que orçamento existe
        orcamento = OrcamentoValidator.validar_orcamento_existe(db, orcamento_id)
        
        # Validar transição de status
        if orcamento.status != novo_status:
            OrcamentoValidator.validar_status_transicao(
                status_atual=orcamento.status,
                novo_status=novo_status
            )
        
        # Atualizar status
        orcamento.status = novo_status
        db.commit()
        db.refresh(orcamento)
        
        # Retornar com dados completos
        orcamento_atualizado = get_orcamento_by_id(db, orcamento_id)
        
        orcamento_logger.info(
            f"Status do orçamento #{orcamento_id} atualizado com sucesso",
            extra={"orcamento_id": orcamento_id}
        )
        
        return orcamento_atualizado
        
    except (NotFoundError, OrcamentoStatusError):
        # Re-raise exceções de negócio
        raise
    except SQLAlchemyError as e:
        db.rollback()
        orcamento_logger.error(
            f"Erro de banco de dados ao atualizar status do orçamento #{orcamento_id}: {str(e)}",
            extra={"orcamento_id": orcamento_id},
            exc_info=True
        )
        raise BusinessRuleException(f"Erro ao atualizar status do orçamento: {str(e)}")
    except Exception as e:
        db.rollback()
        orcamento_logger.error(
            f"Erro inesperado ao atualizar status do orçamento #{orcamento_id}: {str(e)}",
            extra={"orcamento_id": orcamento_id},
            exc_info=True
        )
        raise BusinessRuleException(f"Erro inesperado ao atualizar status: {str(e)}")

def _validar_orcamento_para_confirmacao(
    db: Session,
    orcamento_id: int
) -> models.Orcamento:
    """
    Valida se o orçamento existe e está em status válido para confirmação.
    
    Args:
        db: Sessão do banco de dados
        orcamento_id: ID do orçamento
        
    Returns:
        Orçamento validado
        
    Raises:
        NotFoundError: Se orçamento não existir
        OrcamentoStatusError: Se status não permitir confirmação
    """
    db_orcamento = OrcamentoValidator.validar_orcamento_existe(db, orcamento_id)
    OrcamentoValidator.validar_status_confirmacao(db_orcamento)
    return db_orcamento


def _validar_estoque_orcamento(
    db: Session,
    orcamento: models.Orcamento
) -> None:
    """
    Valida se há estoque suficiente para todos os itens do orçamento.
    
    Args:
        db: Sessão do banco de dados
        orcamento: Orçamento a ser validado
        
    Raises:
        BusinessRuleException: Se houver produtos com estoque insuficiente
    """
    StockValidator.validar_estoque_orcamento(db, orcamento)


def _processar_baixa_estoque(
    db: Session,
    orcamento: models.Orcamento,
    usuario_id: int,
    empresa_id: int,
    stock_service: Optional[Type] = None
) -> None:
    """
    Processa a baixa de estoque para todos os itens do orçamento.
    
    Args:
        db: Sessão do banco de dados
        orcamento: Orçamento a ser processado
        usuario_id: ID do usuário que está confirmando
        empresa_id: ID da empresa
        stock_service: Serviço de estoque (injetado para facilitar testes)
        
    Raises:
        Exception: Se houver erro ao processar baixa
    """
    # Injetar dependência ou usar padrão
    if stock_service is None:
        from app.services.stock_service import StockService
        stock_service = StockService
    
    for item in orcamento.itens:
        stock_service.update_stock_transactionally(
            db=db,
            produto_id=item.produto_id,
            quantidade=item.quantidade,
            tipo_movimentacao=TipoMovimentacao.SAIDA.value,
            usuario_id=usuario_id,
            empresa_id=empresa_id,
            origem=OrigemMovimentacao.VENDA.value,
            observacao=f"Orçamento #{orcamento.id} confirmado"
        )


def _atualizar_status_finalizado(
    db: Session,
    orcamento: models.Orcamento
) -> None:
    """
    Atualiza o status do orçamento para FINALIZADO.
    
    Args:
        db: Sessão do banco de dados
        orcamento: Orçamento a ser atualizado
    """
    orcamento.status = OrcamentoStatus.FINALIZADO.value
    db.commit()
    db.refresh(orcamento)


def confirmar_orcamento(
    db: Session,
    orcamento_id: int,
    usuario_id: int,
    empresa_id: int,
    stock_service: Optional[Type] = None
) -> models.Orcamento:
    """
    Confirma um orçamento e dá baixa no estoque dos produtos.
    
    Orquestra as operações de validação, processamento de estoque e atualização de status.
    Segue o princípio de responsabilidade única, delegando cada etapa para funções específicas.
    
    Args:
        db: Sessão do banco de dados
        orcamento_id: ID do orçamento a ser confirmado
        usuario_id: ID do usuário que está confirmando
        empresa_id: ID da empresa
        stock_service: Serviço de estoque (injetado para facilitar testes)
        
    Returns:
        Orçamento confirmado com status FINALIZADO
        
    Raises:
        NotFoundError: Se orçamento não existir
        OrcamentoStatusError: Se status não permitir confirmação
        BusinessRuleException: Se houver estoque insuficiente
        Exception: Se houver erro ao processar
    """
    orcamento_logger.info(
        f"Iniciando confirmação do orçamento #{orcamento_id}",
        extra={"orcamento_id": orcamento_id, "usuario_id": usuario_id}
    )
    
    try:
        # 1. Validar orçamento e status
        orcamento = _validar_orcamento_para_confirmacao(db, orcamento_id)
        
        # 2. Validar estoque disponível
        _validar_estoque_orcamento(db, orcamento)
        
        # 3. Processar baixa de estoque
        _processar_baixa_estoque(db, orcamento, usuario_id, empresa_id, stock_service)
        
        # 4. Atualizar status para FINALIZADO
        _atualizar_status_finalizado(db, orcamento)
        
        # 5. Retornar orçamento atualizado
        orcamento_atualizado = get_orcamento_by_id(db, orcamento_id)
        
        orcamento_logger.info(
            f"Orçamento #{orcamento_id} confirmado com sucesso",
            extra={"orcamento_id": orcamento_id}
        )
        
        return orcamento_atualizado
        
    except (NotFoundError, OrcamentoStatusError, BusinessRuleException):
        # Re-raise exceções de negócio
        raise
    except SQLAlchemyError as e:
        db.rollback()
        orcamento_logger.error(
            f"Erro de banco de dados ao confirmar orçamento #{orcamento_id}: {str(e)}",
            extra={"orcamento_id": orcamento_id},
            exc_info=True
        )
        raise BusinessRuleException(f"Erro ao confirmar orçamento: {str(e)}")
    except Exception as e:
        db.rollback()
        orcamento_logger.error(
            f"Erro inesperado ao confirmar orçamento #{orcamento_id}: {str(e)}",
            extra={"orcamento_id": orcamento_id},
            exc_info=True
        )
        raise BusinessRuleException(f"Erro inesperado ao confirmar orçamento: {str(e)}")