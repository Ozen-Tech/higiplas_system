# app/routers/movimentacoes.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extensions import connection

# Importe as dependências e schemas
from app.db.connection import get_db
from app.schemas.movimentacao_estoque import MovimentacaoEstoque, MovimentacaoEstoqueCreate
from app.schemas.usuario import Usuario
from app.crud import movimentacao_estoque as crud_movimentacao
from app.security import get_current_user

router = APIRouter(
    prefix="/movimentacoes",
    tags=["Movimentações de Estoque"],
    dependencies=[Depends(get_current_user)] # Ótima prática! Protege todas as rotas.
)

@router.post("/", response_model=MovimentacaoEstoque, status_code=status.HTTP_201_CREATED)
def registrar_nova_movimentacao(
    movimentacao: MovimentacaoEstoqueCreate,
    db: connection = Depends(get_db), # Renomeei 'conn' para 'db' para manter o padrão
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registra uma nova movimentação de estoque (ENTRADA ou SAIDA).
    Esta operação é transacional e requer autenticação.
    """
    # A chamada para o CRUD está perfeita, passando o ID do usuário logado.
    db_movimentacao = crud_movimentacao.create_movimentacao_estoque(
        conn=db, 
        movimentacao=movimentacao, 
        usuario_id=current_user.id
    )
    
    # CORREÇÃO: O retorno agora é direto. 
    # O FastAPI usa o 'response_model' para validar o dicionário que o CRUD retorna.
    return db_movimentacao

@router.get("/produto/{produto_id}", response_model=List[MovimentacaoEstoque])
def listar_movimentacoes_por_produto(
    produto_id: int,
    db: connection = Depends(get_db) # Renomeei 'conn' para 'db' para manter o padrão
):
    """
    Lista todo o histórico de movimentações de estoque para um produto específico.
    """
    movimentacoes = crud_movimentacao.get_movimentacoes_by_produto_id(conn=db, produto_id=produto_id)
    return movimentacoes