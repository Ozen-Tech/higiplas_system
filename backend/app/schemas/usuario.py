from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=3)
    email: EmailStr
    empresa_id: int
    perfil: str # 'admin', 'vendedor', 'estoquista'

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6)

class Usuario(UsuarioBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Schemas para o fluxo de Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None