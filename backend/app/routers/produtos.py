# /backend/app/routers/produtos.py

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse
import traceback
from ..db import models
# Importações dos seus módulos de aplicação
from ..crud import produto as crud_produto
from ..db.connection import get_db
from ..schemas import produto as schemas_produto
from ..schemas import usuario as schemas_usuario
from app.dependencies import get_current_user
from sqlalchemy import func, case, or_
from ..services.purchase_suggestion_service import PurchaseSuggestionService

# Define o prefixo e as tags para todas as rotas neste arquivo
router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"],
    responses={404: {"description": "Produto não encontrado"}},
)

# --- ROTAS DA API (na ordem correta de especificidade) ---

@router.get("/", response_model=List[schemas_produto.Produto], summary="Listar todos os produtos")
def read_all_produtos(
    db: Session = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    """Retorna uma lista de todos os produtos da empresa do usuário logado."""
    return crud_produto.get_produtos(db=db, empresa_id=current_user.empresa_id)

@router.get("/baixo-estoque", response_model=List[schemas_produto.Produto], summary="Listar produtos com estoque baixo")
@router.get("/baixo-estoque/", response_model=List[schemas_produto.Produto], summary="Listar produtos com estoque baixo")
def read_low_stock_produtos(
    db: Session = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna uma lista de produtos onde a quantidade em estoque é menor ou igual ao estoque mínimo.
    Usa cálculo baseado em demanda real quando há histórico suficiente.
    Trata casos onde o estoque mínimo é nulo.
    """
    # Busca produtos com estoque baixo usando estoque mínimo atual
    produtos_baixo_estoque = db.query(models.Produto).filter(
        models.Produto.empresa_id == current_user.empresa_id,
        models.Produto.quantidade_em_estoque <= models.Produto.estoque_minimo
    ).all()
    
    # Para produtos com histórico suficiente, verifica também estoque mínimo calculado
    service = PurchaseSuggestionService(db)
    suggestions = service.get_purchase_suggestions(
        empresa_id=current_user.empresa_id,
        days_analysis=90,
        min_sales_threshold=2
    )
    
    # Cria set de IDs de produtos que precisam de compra
    produtos_que_precisam_compra = {s['produto_id'] for s in suggestions}
    
    # Adiciona produtos que estão abaixo do estoque mínimo calculado mas não do atual
    produtos_ids_baixo_estoque = {p.id for p in produtos_baixo_estoque}
    
    # Busca produtos adicionais que estão abaixo do mínimo calculado
    for suggestion in suggestions:
        produto_id = suggestion['produto_id']
        if produto_id not in produtos_ids_baixo_estoque:
            produto = db.query(models.Produto).filter(
                models.Produto.id == produto_id,
                models.Produto.empresa_id == current_user.empresa_id
            ).first()
            if produto:
                produtos_baixo_estoque.append(produto)
    
    return produtos_baixo_estoque

@router.get("/buscar", response_model=List[schemas_produto.Produto], summary="Buscar produtos por termo")
def buscar_produtos(
    q: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Busca produtos por nome ou código.
    Retorna produtos que contenham o termo de busca no nome ou código.
    IMPORTANTE: Esta rota deve estar ANTES da rota /{produto_id} para evitar conflito.
    """
    if not q or len(q.strip()) < 2:
        return []
    
    termo = q.strip().upper()
    
    produtos = db.query(models.Produto).filter(
        models.Produto.empresa_id == current_user.empresa_id,
        or_(
            func.upper(models.Produto.nome).contains(termo),
            func.upper(models.Produto.codigo).contains(termo)
        )
    ).limit(50).all()
    
    return produtos

@router.get("/download/excel", response_description="Retorna um arquivo Excel com todos os produtos", summary="Exportar produtos para Excel")
def download_produtos_excel(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
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
        
        return StreamingResponse(
            output, 
            headers=headers, 
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print("\n--- ERRO INTERNO AO GERAR EXCEL ---")
        print(f"Tipo de Erro: {type(e).__name__}")
        print(f"Mensagem de Erro: {e}")
        traceback.print_exc()
        print("---------------------------------\n")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro no servidor ao gerar o arquivo Excel: {str(e)}"
        )

@router.get("/{produto_id}", response_model=schemas_produto.Produto, summary="Buscar um produto por ID")
def read_one_produto(
    produto_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna os dados de um produto específico.
    Importante para a página de histórico funcionar.
    """
    # A função get_produto_by_id precisa existir em seu crud/produto.py
    db_produto = crud_produto.get_produto_by_id(db=db, produto_id=produto_id, empresa_id=current_user.empresa_id)
    if db_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado ou não pertence à sua empresa.")
    return db_produto

@router.post("/", response_model=schemas_produto.Produto, status_code=status.HTTP_201_CREATED, summary="Criar um novo produto")
def create_produto(
    produto: schemas_produto.ProdutoCreate, 
    db: Session = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo produto associado à empresa do usuário logado."""
    return crud_produto.create_produto(db=db, produto=produto, empresa_id=current_user.empresa_id)

@router.put("/{produto_id}", response_model=schemas_produto.Produto, summary="Atualizar um produto")
def update_produto_endpoint(
    produto_id: int, 
    produto: schemas_produto.ProdutoUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza os dados de um produto existente."""
    updated_produto = crud_produto.update_produto(db=db, produto_id=produto_id, produto_data=produto, empresa_id=current_user.empresa_id)
    if updated_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return updated_produto

@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deletar um produto")
def delete_produto_endpoint(
    produto_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    """Deleta um produto do banco de dados."""
    deleted_produto = crud_produto.delete_produto(db=db, produto_id=produto_id, empresa_id=current_user.empresa_id)
    if deleted_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

