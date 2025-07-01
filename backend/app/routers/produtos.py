# app/routers/produtos.py

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extensions import connection
from typing import List

# Importe os schemas necessários
from app.schemas.produto import Produto, ProdutoCreate
from app.schemas.usuario import Usuario

# Importe o módulo CRUD
from app.crud import produto as crud_produto

# Importe as dependências
from app.db.connection import get_db
from app.security import get_current_user

router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)

@router.post("/", response_model=Produto, status_code=status.HTTP_201_CREATED)
def create_new_produto(
    produto: ProdutoCreate, 
    db: connection = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cria um novo produto. Requer autenticação.
    - A função agora recebe 'db' via injeção de dependência.
    - A chamada ao CRUD passa a conexão 'db'.
    - O retorno é direto, o FastAPI cuida da validação.
    """
    # Opcional: você pode usar o current_user para lógicas de permissão aqui
    # print(f"Usuário {current_user.email} está criando um produto.")
    
    return crud_produto.create_produto(conn=db, produto=produto)


@router.get("/", response_model=List[Produto])
def read_produtos(
    skip: int = 0, 
    limit: int = 100, 
    db: connection = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna uma lista de produtos. Requer autenticação.
    - A função agora recebe 'db', 'skip' e 'limit'.
    - A chamada ao CRUD passa todos os parâmetros necessários.
    - O retorno é a lista de dicionários que o CRUD fornece.
    """
    produtos = crud_produto.get_produtos(conn=db, skip=skip, limit=limit)
    return produtos