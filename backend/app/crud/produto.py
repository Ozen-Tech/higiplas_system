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


def update_produto_by_nome(db: Session, nome: str, estoque: int, data_validade, preco_venda: float, estoque_minimo: int):
    produto = db.query(Produto).filter(Produto.nome == nome).first()
    if not produto:
        raise Exception("Produto não encontrado")

    produto.quantidade_em_estoque = estoque
    produto.data_validade = data_validade
    produto.preco_venda = preco_venda
    produto.estoque_minimo = estoque_minimo

    db.commit()
    db.refresh(produto)
    return produto

def create_or_update_produto(db: Session, produto_data: schemas_produto.ProdutoCreate, empresa_id: int):
    """
    Verifica se um produto com o mesmo código já existe para a empresa.
    Se existir, atualiza seus dados (incluindo o estoque). 
    Se não existir, cria um novo com os dados fornecidos.
    """
    db_produto = db.query(models.Produto).filter(
        models.Produto.codigo == produto_data.codigo,
        models.Produto.empresa_id == empresa_id
    ).first()

    # Separa o valor do estoque dos outros dados para um tratamento claro.
    estoque_para_definir = produto_data.quantidade_em_estoque or 0
    # Gera um dicionário com os outros dados do produto.
    update_dict = produto_data.model_dump(exclude={"quantidade_em_estoque"}, exclude_unset=True)
    
    # Se o produto já existe, atualize-o
    if db_produto:
        for key, value in update_dict.items():
            setattr(db_produto, key, value)
        # Define o estoque com o valor do arquivo (sobrescreve o anterior)
        db_produto.quantidade_em_estoque = estoque_para_definir
        
    # Se não existe, crie um novo
    else:
        db_produto = models.Produto(
            **update_dict, # Usa o dicionário com os dados principais
            empresa_id=empresa_id,
            # Define o estoque com o valor do arquivo (em vez de 0)
            quantidade_em_estoque=estoque_para_definir 
        )
        db.add(db_produto)

    db.commit()
    db.refresh(db_produto)
    return db_produto