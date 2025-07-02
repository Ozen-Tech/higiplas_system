# backend/app/crud/produto.py

from sqlalchemy.orm import Session
from ..schemas import produto as schemas_produto
from ..db import models

def get_produtos(db: Session, empresa_id: int):
    """Busca todos os produtos de uma empresa."""
    return db.query(models.Produto).filter(models.Produto.empresa_id == empresa_id).all()

def create_produto(db: Session, produto: schemas_produto.ProdutoCreate, empresa_id: int):
    """Cria um novo produto."""
    db_produto = models.Produto(
        **produto.model_dump(), 
        empresa_id=empresa_id
    )
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

# --- NOVA FUNÇÃO DE UPDATE ---
def update_produto(db: Session, produto_id: int, produto_data: schemas_produto.ProdutoUpdate, empresa_id: int):
    """Atualiza um produto existente."""
    # Busca o produto pelo ID e pelo ID da empresa (por segurança)
    db_produto = db.query(models.Produto).filter(models.Produto.id == produto_id, models.Produto.empresa_id == empresa_id).first()

    if not db_produto:
        return None

    # Pega os dados enviados pelo usuário (excluindo os que não foram enviados)
    update_data = produto_data.model_dump(exclude_unset=True)

    # Atualiza os campos do objeto SQLAlchemy
    for key, value in update_data.items():
        setattr(db_produto, key, value)

    db.commit()
    db.refresh(db_produto)
    return db_produto

# --- NOVA FUNÇÃO DE DELETE ---
def delete_produto(db: Session, produto_id: int, empresa_id: int):
    """Deleta um produto existente."""
    db_produto = db.query(models.Produto).filter(models.Produto.id == produto_id, models.Produto.empresa_id == empresa_id).first()

    if not db_produto:
        return None

    db.delete(db_produto)
    db.commit()
    return db_produto