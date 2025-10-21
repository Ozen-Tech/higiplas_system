# backend/app/crud/proposta.py

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.db import models
from app.schemas import proposta as schemas_proposta

def create_proposta(db: Session, proposta_in: schemas_proposta.PropostaCreate, vendedor_id: int) -> models.Proposta:
    """Cria uma nova proposta com seus itens."""
    
    db_proposta = models.Proposta(
        cliente_id=proposta_in.cliente_id,
        usuario_id=vendedor_id,
        status=proposta_in.status,
        observacoes=proposta_in.observacoes
    )
    db.add(db_proposta)
    db.flush()

    for item_in in proposta_in.itens:
        db_item = models.PropostaItem(
            proposta_id=db_proposta.id,
            produto_nome=item_in.produto_nome,
            descricao=item_in.descricao,
            valor=item_in.valor,
            rendimento_litros=item_in.rendimento_litros,
            custo_por_litro=item_in.custo_por_litro
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_proposta)
    return db_proposta

def get_propostas_by_vendedor(db: Session, vendedor_id: int) -> List[models.Proposta]:
    """
    Lista todas as propostas criadas por um vendedor específico,
    carregando os dados relacionados e garantindo integridade dos dados.
    """
    return db.query(models.Proposta).options(
        joinedload(models.Proposta.cliente),
        joinedload(models.Proposta.usuario),
        joinedload(models.Proposta.itens)
    ).join(
        models.Cliente
    ).filter(
        models.Proposta.usuario_id == vendedor_id,
        models.Proposta.cliente_id.isnot(None)
    ).order_by(
        models.Proposta.data_criacao.desc()
    ).all()

def get_proposta_by_id(db: Session, proposta_id: int, vendedor_id: int) -> Optional[models.Proposta]:
    """
    Busca uma proposta específica por ID, garantindo que pertence ao vendedor.
    """
    return db.query(models.Proposta).options(
        joinedload(models.Proposta.cliente),
        joinedload(models.Proposta.usuario),
        joinedload(models.Proposta.itens)
    ).filter(
        models.Proposta.id == proposta_id,
        models.Proposta.usuario_id == vendedor_id
    ).first()

def update_proposta(db: Session, proposta_id: int, proposta_update: schemas_proposta.PropostaUpdate, vendedor_id: int) -> Optional[models.Proposta]:
    """
    Atualiza uma proposta existente.
    """
    db_proposta = get_proposta_by_id(db, proposta_id, vendedor_id)
    if not db_proposta:
        return None
    
    update_data = proposta_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_proposta, key, value)
    
    db.commit()
    db.refresh(db_proposta)
    return db_proposta

def delete_proposta(db: Session, proposta_id: int, vendedor_id: int) -> bool:
    """
    Deleta uma proposta.
    """
    db_proposta = get_proposta_by_id(db, proposta_id, vendedor_id)
    if not db_proposta:
        return False
    
    db.delete(db_proposta)
    db.commit()
    return True
