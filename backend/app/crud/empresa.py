# backend/app/crud/empresa.py

from sqlalchemy.orm import Session
from ..db import models
from ..schemas import empresa as schemas_empresa

def get_empresa(db: Session, empresa_id: int):
    """Busca uma única empresa pelo seu ID."""
    return db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()

def get_empresas(db: Session, skip: int = 0, limit: int = 100):
    """Busca uma lista de empresas com paginação."""
    return db.query(models.Empresa).offset(skip).limit(limit).all()

def create_empresa(db: Session, empresa: schemas_empresa.EmpresaCreate):
    """Cria uma nova empresa no banco de dados."""
    # O ORM cuida da conversão do schema para o modelo.
    # Usamos .model_dump() que é o sucessor de .dict() no Pydantic V2
    db_empresa = models.Empresa(**empresa.model_dump())
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    return db_empresa