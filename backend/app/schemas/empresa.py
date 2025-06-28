from pydantic import BaseModel, Field
from datetime import datetime

class EmpresaBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100, example="Higiplas")
    cnpj: str = Field(..., min_length=14, max_length=18, example="22.599.389/0001-76")

class EmpresaCreate(EmpresaBase):
    pass

class Empresa(EmpresaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True # Permite que o Pydantic leia dados de objetos (como os do DB)