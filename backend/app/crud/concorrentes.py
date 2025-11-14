# backend/app/crud/concorrentes.py

from sqlalchemy.orm import Session
from typing import Optional, List
from ..schemas import proposta_detalhada as schemas
from ..db import models


def create_concorrente(db: Session, concorrente_in: schemas.ProdutoConcorrenteCreate) -> models.ProdutoConcorrente:
    """Cria um novo produto concorrente"""
    db_concorrente = models.ProdutoConcorrente(**concorrente_in.model_dump())
    db.add(db_concorrente)
    db.commit()
    db.refresh(db_concorrente)
    return db_concorrente


def get_concorrente_by_id(db: Session, concorrente_id: int) -> Optional[models.ProdutoConcorrente]:
    """Busca um concorrente por ID"""
    return db.query(models.ProdutoConcorrente).filter(
        models.ProdutoConcorrente.id == concorrente_id
    ).first()


def get_concorrentes(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    categoria: Optional[str] = None,
    ativo: Optional[bool] = True
) -> List[models.ProdutoConcorrente]:
    """Lista concorrentes com filtros opcionais"""
    query = db.query(models.ProdutoConcorrente)
    
    if ativo is not None:
        query = query.filter(models.ProdutoConcorrente.ativo == ativo)
    
    if categoria:
        query = query.filter(models.ProdutoConcorrente.categoria == categoria)
    
    return query.offset(skip).limit(limit).all()


def get_concorrentes_por_categoria(db: Session, categoria: str) -> List[models.ProdutoConcorrente]:
    """Busca concorrentes de uma categoria específica"""
    return db.query(models.ProdutoConcorrente).filter(
        models.ProdutoConcorrente.categoria == categoria,
        models.ProdutoConcorrente.ativo == True
    ).all()


def update_concorrente(
    db: Session,
    concorrente_id: int,
    concorrente_update: schemas.ProdutoConcorrenteUpdate
) -> Optional[models.ProdutoConcorrente]:
    """Atualiza um concorrente"""
    db_concorrente = db.query(models.ProdutoConcorrente).filter(
        models.ProdutoConcorrente.id == concorrente_id
    ).first()
    
    if not db_concorrente:
        return None
    
    update_data = concorrente_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_concorrente, key, value)
    
    db.commit()
    db.refresh(db_concorrente)
    return db_concorrente


def delete_concorrente(db: Session, concorrente_id: int) -> bool:
    """Deleta um concorrente (ou desativa se preferir)"""
    db_concorrente = db.query(models.ProdutoConcorrente).filter(
        models.ProdutoConcorrente.id == concorrente_id
    ).first()
    
    if not db_concorrente:
        return False
    
    # Ao invés de deletar, podemos apenas desativar
    # db.delete(db_concorrente)
    db_concorrente.ativo = False
    db.commit()
    return True

