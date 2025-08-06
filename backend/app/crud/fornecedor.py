from sqlalchemy.orm import Session
from ..db import models
from ..schemas import fornecedor as schemas_fornecedor

def get_fornecedores(db: Session, empresa_id: int):
    return db.query(models.Fornecedor).filter(models.Fornecedor.empresa_id == empresa_id).all()

def create_fornecedor(db: Session, fornecedor: schemas_fornecedor.FornecedorCreate, empresa_id: int):
    db_fornecedor = models.Fornecedor(**fornecedor.model_dump(), empresa_id=empresa_id)
    db.add(db_fornecedor)
    db.commit()
    db.refresh(db_fornecedor)
    return db_fornecedor