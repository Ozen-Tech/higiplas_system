from pydantic import BaseModel, EmailStr, Field, constr
from typing import Optional
from datetime import datetime
from enum import Enum

class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=3)
    email: EmailStr
    empresa_id: int
    perfil: str # 'admin', 'vendedor', 'estoquista'

class PerfisUsuario(str, Enum): 
    admin = "admin"
    vendedor = "vendedor"
    gerente = "gerente"

class UsuarioCreate(UsuarioBase):
    email: EmailStr
    password: str
    nome: str
    empresa_id: int
    perfil: str

class Usuario(UsuarioBase):
    id: int
    is_active: bool
    data_criacao: datetime
    perfil: str

    class Config:
        from_attributes = True

# Schemas para o fluxo de Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None