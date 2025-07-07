from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.empresa import Empresa, EmpresaCreate
from psycopg2.extensions import connection 
from app.crud import empresa as crud_empresa
from app.db.connection import get_db
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/empresas",
    tags=["Empresas"]
)

@router.post("/", response_model=Empresa, status_code=status.HTTP_201_CREATED)
def create_new_empresa(empresa: EmpresaCreate, db: connection = Depends(get_db)): # <--- A MÁGICA ACONTECE AQUI!
    """
    Cria uma nova empresa no sistema.

    - **empresa**: Dados da nova empresa (nome, cnpj) vindos do corpo do request.
    - **db**: Dependência que injeta a sessão/conexão com o banco de dados.
    """
    # Agora a variável 'db' existe e pode ser passada para a função do CRUD.
    return crud_empresa.create_empresa(conn=db, empresa=empresa)

 
@router.get("/", response_model=List[Empresa])
def read_empresas(skip: int = 0, limit: int = 100, db: connection = Depends(get_db)):
    """
    Retorna uma lista de empresas cadastradas, com paginação.
    """
    empresas = crud_empresa.get_empresas(conn=db, skip=skip, limit=limit)
    return empresas