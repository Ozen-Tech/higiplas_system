# /backend/app/routers/produtos.py

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse
import traceback

from ..crud import produto as crud_produto
from ..db.connection import get_db
from ..schemas import produto as schemas_produto
from ..schemas import usuario as schemas_usuario
from app.dependencies import get_current_user

# Definimos o prefixo aqui para manter as rotas organizadas
router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"],
    responses={404: {"description": "Produto não encontrado"}},
)

# --- ROTAS DA API ---

@router.post("/", response_model=schemas_produto.Produto, status_code=status.HTTP_201_CREATED, summary="Criar um novo produto")
def create_produto(produto: schemas_produto.ProdutoCreate, db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    """Cria um novo produto associado à empresa do usuário logado."""
    return crud_produto.create_produto(db=db, produto=produto, empresa_id=current_user.empresa_id)

@router.get("/", response_model=List[schemas_produto.Produto], summary="Listar todos os produtos")
def read_all_produtos(db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    """Retorna uma lista de todos os produtos da empresa do usuário logado."""
    return crud_produto.get_produtos(db=db, empresa_id=current_user.empresa_id)

@router.get("/{produto_id}", response_model=schemas_produto.Produto, summary="Buscar um produto por ID")
def read_one_produto(produto_id: int, db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    """
    Retorna os dados de um produto específico.
    Utilizado pela página de histórico para buscar o nome do produto.
    """
    db_produto = crud_produto.get_produto_by_id(db=db, produto_id=produto_id, empresa_id=current_user.empresa_id)
    if db_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado ou não pertence à sua empresa.")
    return db_produto

@router.put("/{produto_id}", response_model=schemas_produto.Produto, summary="Atualizar um produto")
def update_produto_endpoint(produto_id: int, produto: schemas_produto.ProdutoUpdate, db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    """Atualiza os dados de um produto existente."""
    updated_produto = crud_produto.update_produto(db=db, produto_id=produto_id, produto_data=produto, empresa_id=current_user.empresa_id)
    if updated_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return updated_produto

@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deletar um produto")
def delete_produto_endpoint(produto_id: int, db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    """Deleta um produto do banco de dados."""
    deleted_produto = crud_produto.delete_produto(db=db, produto_id=produto_id, empresa_id=current_user.empresa_id)
    if deleted_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/download/excel", response_description="Retorna um arquivo Excel com todos os produtos", summary="Exportar produtos para Excel")
def download_produtos_excel(db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    """
    Busca todos os produtos da empresa do usuário logado e os retorna
    como um arquivo Excel (.xlsx) para download.
    """
    try:
        produtos = crud_produto.get_produtos(db=db, empresa_id=current_user.empresa_id)
        if not produtos:
            raise HTTPException(status_code=404, detail="Nenhum produto encontrado para exportar.")

        produtos_dict_list = [
            {
                "nome": p.nome,
                "codigo": p.codigo,
                "categoria": p.categoria,
                "estoque": p.quantidade_em_estoque,
                "estoque_minimo": p.estoque_minimo,
                "unidade_medida": p.unidade_medida,
                "preco_venda": p.preco_venda,
                "preco_custo": p.preco_custo,
                "data_validade": p.data_validade,
                "descricao": p.descricao,
            }
            for p in produtos
        ]
        
        df = pd.DataFrame(produtos_dict_list)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Produtos')
        
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="higiplas_produtos.xlsx"'
        }
        
        return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    except Exception as e:
        print(f"\n--- ERRO INTERNO AO GERAR EXCEL ---\n{e}\n{traceback.format_exc()}\n---------------------------------\n")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro no servidor ao gerar o arquivo Excel: {str(e)}"
        )