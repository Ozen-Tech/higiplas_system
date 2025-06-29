from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extensions import connection
from app.db.connection import get_db_cursor
from app.schemas.movimentacao_estoque import MovimentacaoEstoque, MovimentacaoEstoqueCreate
from app.schemas.usuario import Usuario
from app.crud import movimentacao_estoque as crud_movimentacao
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/movimentacoes", # Todas as rotas aqui começarão com /movimentacoes
    tags=["Movimentações de Estoque"],
    dependencies=[Depends(get_current_user)] # Protege TODAS as rotas neste arquivo
)

@router.post("/", response_model=MovimentacaoEstoque, status_code=status.HTTP_201_CREATED)
def registrar_nova_movimentacao(
    movimentacao: MovimentacaoEstoqueCreate,
    conn: connection = Depends(get_db_cursor),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registra uma nova movimentação de estoque (ENTRADA ou SAIDA).

    Esta operação é transacional:
    - **Atualiza** o `estoque_atual` na tabela `produtos`.
    - **Cria** um registro na tabela `movimentacoes_estoque`.

    Apenas usuários autenticados podem realizar esta operação.
    """
    
    # Passamos o ID do usuário logado para a função do CRUD
    # para que a movimentação seja associada a ele.
    db_movimentacao = crud_movimentacao.create_movimentacao_estoque(
        conn=conn, 
        movimentacao=movimentacao, 
        usuario_id=current_user.id
    )
    
    if not db_movimentacao:
        # Esta é uma proteção extra, embora o CRUD já levante exceções.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível criar a movimentação de estoque."
        )
        
    return MovimentacaoEstoque.model_validate(db_movimentacao)