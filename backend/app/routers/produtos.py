# backend/app/routers/produtos.py

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
import pandas as pd 
from io import BytesIO 
# --- IMPORTAÇÕES ADICIONADAS ---
from fastapi.responses import StreamingResponse
import traceback

from ..crud import produto as crud_produto
from ..db.connection import get_db
from ..schemas import produto as schemas_produto
from ..schemas import usuario as schemas_usuario
from app.dependencies import get_current_user

router = APIRouter(
    #prefix="/produtos", # É uma boa prática definir o prefixo aqui ou no main.py, mas não em ambos.
    tags=["Produtos"],
    responses={404: {"description": "Produto não encontrado"}},
)

# --- SUAS ROTAS EXISTENTES (sem alterações) ---

@router.post("/", response_model=schemas_produto.Produto, status_code=status.HTTP_201_CREATED)
def create_produto(produto: schemas_produto.ProdutoCreate, db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    return crud_produto.create_produto(db=db, produto=produto, empresa_id=current_user.empresa_id)

@router.get("/", response_model=List[schemas_produto.Produto])
def read_produtos(db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    return crud_produto.get_produtos(db=db, empresa_id=current_user.empresa_id)

@router.put("/{produto_id}", response_model=schemas_produto.Produto)
def update_produto_endpoint(produto_id: int, produto: schemas_produto.ProdutoUpdate, db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    updated_produto = crud_produto.update_produto(db=db, produto_id=produto_id, produto_data=produto, empresa_id=current_user.empresa_id)
    if updated_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return updated_produto

@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_produto_endpoint(produto_id: int, db: Session = Depends(get_db), current_user: schemas_usuario.Usuario = Depends(get_current_user)):
    deleted_produto = crud_produto.delete_produto(db=db, produto_id=produto_id, empresa_id=current_user.empresa_id)
    if deleted_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- ROTA DE DOWNLOAD COM TRATAMENTO DE ERRO ---

@router.get("/download/excel", response_description="Retorna um arquivo Excel com todos os produtos")
def download_produtos_excel(
    db: Session = Depends(get_db),
    current_user: schemas_usuario.Usuario = Depends(get_current_user)
):
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
        # Bloco de captura para encontrar o erro interno (500)
        print("\n--- ERRO INTERNO NO BACKEND AO GERAR EXCEL ---")
        print(f"Tipo de Erro: {type(e).__name__}")
        print(f"Mensagem de Erro: {e}")
        print("Traceback completo:")
        traceback.print_exc()
        print("------------------------------------------------\n")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro no servidor ao gerar o arquivo Excel: {str(e)}"
        )