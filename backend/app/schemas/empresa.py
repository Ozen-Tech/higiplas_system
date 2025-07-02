# backend/app/schemas/empresa.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# --- Schema Base ---
class EmpresaBase(BaseModel):
    nome: str
    # Tornando o CNPJ opcional em toda a base
    cnpj: Optional[str] = None

# --- Schema para Criação (herda da base) ---
class EmpresaCreate(EmpresaBase):
    pass # Não precisa de mais nada, já herda nome e cnpj opcional

# --- Schema para Leitura/Retorno (o que a API devolve) ---
class Empresa(EmpresaBase):
    id: int
    data_criacao: datetime

    # Configuração para permitir que o Pydantic leia dados de um modelo ORM
    model_config = ConfigDict(from_attributes=True)