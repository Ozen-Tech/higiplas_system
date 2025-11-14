from pydantic import BaseModel, EmailStr, Field, constr, field_serializer
from typing import Optional
from datetime import datetime
from enum import Enum

class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=3)
    email: EmailStr
    empresa_id: int
    perfil: str # 'admin', 'vendedor', 'estoquista'

class PerfilUsuario(str, Enum):
    ADMIN = "ADMIN"
    GESTOR = "GESTOR"
    OPERADOR = "OPERADOR"

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

    @field_serializer('data_criacao')
    def serialize_datetime(self, value: datetime, _info):
        """Serializa datetime para string ISO format"""
        if value is None:
            return None
        return value.isoformat()

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Schemas para o fluxo de Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None