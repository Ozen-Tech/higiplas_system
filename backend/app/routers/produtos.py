from fastapi import APIRouter, HTTPException, Depends # Adicione Depends
from typing import List
from app.schemas.produto import Produto, ProdutoCreate
from app.schemas.usuario import Usuario # Importe o schema do usuário
from app.crud import produto as crud_produto
from app.db.connection import get_db_cursor
from app.routers.auth import get_current_user # Importe a dependência

router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)

# Adicione a dependência 'current_user'
@router.post("/", response_model=Produto, status_code=201)
def create_new_produto(produto: ProdutoCreate, current_user: Usuario = Depends(get_current_user)):
    # Agora você tem acesso ao usuário logado via 'current_user'
    # Ex: print(f"Usuário {current_user.email} está criando um produto.")
    new_produto_data = crud_produto.create_produto(produto)
    return Produto.model_validate(dict(zip([desc[0] for desc in new_produto_data.cursor.description], new_produto_data)))

# Adicione a dependência 'current_user'
@router.get("/", response_model=List[Produto])
def read_produtos(current_user: Usuario = Depends(get_current_user)):
    produtos_data = crud_produto.get_produtos()
    if not produtos_data:
        return []
    column_names = [desc[0] for desc in produtos_data[0].cursor.description]
    return [Produto.model_validate(dict(zip(column_names, row))) for row in produtos_data]