from pydantic import BaseModel, ConfigDict
from typing import Optional


class FornecedorBase(BaseModel):
    nome: str
    cnpj: Optional[str] = None
    contato_email: Optional[str] = None
    contato_telefone: Optional[str] = None

class FornecedorCreate(FornecedorBase):
    pass

class Fornecedor(FornecedorBase):
    id: int
    empresa_id: int

model_config = ConfigDict(from_attributes=True)
