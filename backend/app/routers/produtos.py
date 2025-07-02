# backend/app/routers/produtos.py

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from ..crud import produto as crud_produto
from ..db.connection import get_db
from ..schemas import produto as schemas_produto
from ..schemas import usuario as schemas_usuario
from ..security import get_current_user

router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"],
    responses={404: {"description": "Produto não encontrado"}},
)

@router.post("/", response_model=schemas_produto.Produto, status_code=status.HTTP_201_CREATED)
def create_produto(produto: schemas_produto.ProdutoCreate, db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    return crud_produto.create_produto(db=db, produto=produto, empresa_id=current_user.empresa_id)

@router.get("/", response_model=List[schemas_produto.Produto])
def read_produtos(db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    return crud_produto.get_produtos(db=db, empresa_id=current_user.empresa_id)

# --- NOVO ENDPOINT DE UPDATE (PUT) ---
@router.put("/{produto_id}", response_model=schemas_produto.Produto)
def update_produto_endpoint(produto_id: int, produto: schemas_produto.ProdutoUpdate, db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    updated_produto = crud_produto.update_produto(db=db, produto_id=produto_id, produto_data=produto, empresa_id=current_user.empresa_id)
    if updated_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return updated_produto

# --- NOVO ENDPOINT DE DELETE ---
@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_produto_endpoint(produto_id: int, db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    deleted_produto = crud_produto.delete_produto(db=db, produto_id=produto_id, empresa_id=current_user.empresa_id)
    if deleted_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    # Retorna uma resposta vazia com status 204, como é a boa prática para DELETE
    return Response(status_code=status.HTTP_204_NO_CONTENT)