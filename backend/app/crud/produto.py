# backend/app/crud/produto.py

from sqlalchemy.orm import Session
from datetime import datetime
import time
import uuid
from ..schemas import produto as schemas_produto
from ..db import models

def get_produtos(db: Session, empresa_id: int):
    """Busca todos os produtos de uma empresa."""
    return db.query(models.Produto).filter(models.Produto.empresa_id == empresa_id).all()

def get_produto_by_id(db: Session, produto_id: int, empresa_id: int):
    """Busca um único produto pelo ID, garantindo que pertence à empresa correta."""
    return db.query(models.Produto).filter(
        models.Produto.id == produto_id,
        models.Produto.empresa_id == empresa_id
    ).first()

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
    """
    Deleta um produto existente.
    
    Verifica se o produto está sendo usado em orçamentos antes de deletar.
    Se estiver sendo usado, retorna None para indicar que não pode ser deletado.
    """
    db_produto = db.query(models.Produto).filter(
        models.Produto.id == produto_id, 
        models.Produto.empresa_id == empresa_id
    ).first()

    if not db_produto:
        return None

    # Verificar se o produto está sendo usado em itens de orçamento
    itens_orcamento = db.query(models.OrcamentoItem).filter(
        models.OrcamentoItem.produto_id == produto_id
    ).first()
    
    if itens_orcamento:
        # Produto está sendo usado em orçamentos, não pode ser deletado
        raise ValueError("Produto não pode ser deletado pois está sendo usado em orçamentos. Delete os orçamentos relacionados primeiro.")

    db.delete(db_produto)
    db.commit()
    return db_produto


def update_produto_by_nome(db: Session, nome: str, estoque: int, data_validade, preco_venda: float, estoque_minimo: int):
    produto = db.query(models.Produto).filter(models.Produto.nome == nome).first() # Corrigido para models.Produto
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

def criar_produto_personalizado(
    db: Session,
    nome: str,
    preco_unitario: float,
    empresa_id: int
) -> models.Produto:
    """
    Cria um produto personalizado automaticamente quando um item personalizado
    é adicionado ao orçamento.
    
    Usa timestamp em milissegundos + UUID para garantir unicidade mesmo em
    requisições simultâneas.
    
    Args:
        db: Sessão do banco de dados
        nome: Nome do produto personalizado
        preco_unitario: Preço unitário do produto
        empresa_id: ID da empresa
        
    Returns:
        Produto criado
    """
    # Gera código único usando timestamp em milissegundos + parte do UUID
    # Isso garante unicidade mesmo em requisições simultâneas
    timestamp = int(time.time() * 1000)  # milissegundos para maior precisão
    uuid_part = str(uuid.uuid4())[:8]  # Primeiros 8 caracteres do UUID
    codigo = f"PERS-{timestamp}-{uuid_part}"
    
    # Verificar se o código já existe (muito improvável, mas por segurança)
    tentativas = 0
    while db.query(models.Produto).filter(models.Produto.codigo == codigo).first() and tentativas < 5:
        timestamp = int(time.time() * 1000)
        uuid_part = str(uuid.uuid4())[:8]
        codigo = f"PERS-{timestamp}-{uuid_part}"
        tentativas += 1
    
    # Cria produto com estoque inicial 0
    db_produto = models.Produto(
        nome=nome,
        codigo=codigo,
        categoria="Personalizado",
        descricao=f"Produto personalizado criado automaticamente",
        preco_custo=None,  # Não tem custo definido
        preco_venda=preco_unitario,
        unidade_medida="UN",  # Unidade padrão
        estoque_minimo=0,
        quantidade_em_estoque=0,  # Estoque inicial 0
        data_validade=None,
        empresa_id=empresa_id
    )
    
    db.add(db_produto)
    db.flush()  # Usa flush em vez de commit para manter transação
    db.refresh(db_produto)
    return db_produto