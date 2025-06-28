# backend/app/routers/produtos.py

from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.produto import Produto, ProdutoCreate
from app.crud import produto as crud_produto

router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)

@router.post("/", response_model=Produto, status_code=201)
def create_new_produto(produto: ProdutoCreate):
    new_produto_data = crud_produto.create_produto(produto)
    return Produto.model_validate(dict(zip([desc[0] for desc in new_produto_data.cursor.description], new_produto_data)))


@router.get("/", response_model=List[Produto])
def read_produtos():
    produtos_data = crud_produto.get_produtos()
    if not produtos_data:
        return []
    column_names = [desc[0] for desc in produtos_data[0].cursor.description]
    return [Produto.model_validate(dict(zip(column_names, row))) for row in produtos_data]