from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.empresa import Empresa, EmpresaCreate
from app.crud import empresa as crud_empresa
from app.db.connection import get_db_cursor


router = APIRouter(
    prefix="/empresas",
    tags=["Empresas"]
)

@router.post("/", response_model=Empresa, status_code=201)
def create_new_empresa(empresa: EmpresaCreate):
    # Aqui você pode adicionar validações, como verificar se o CNPJ já existe
    new_empresa_data = crud_empresa.create_empresa(empresa)
    return Empresa.model_validate(dict(zip([desc[0] for desc in new_empresa_data.cursor.description], new_empresa_data)))


@router.get("/", response_model=List[Empresa])
def read_empresas():
    empresas_data = crud_empresa.get_empresas()
    # Converte a lista de tuplas do DB para uma lista de dicionários e depois para o modelo Pydantic
    column_names = [desc[0] for desc in empresas_data[0].cursor.description]
    return [Empresa.model_validate(dict(zip(column_names, row))) for row in empresas_data]