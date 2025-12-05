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
    foto_perfil: Optional[str] = None

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

# Schemas para atualização de perfil
class UsuarioUpdate(BaseModel):
    """Schema para atualizar dados do perfil do usuário"""
    nome: Optional[str] = Field(None, min_length=3)
    email: Optional[EmailStr] = None
    foto_perfil: Optional[str] = None

class UsuarioUpdateSenha(BaseModel):
    """Schema para atualizar senha do usuário"""
    senha_atual: str
    nova_senha: str = Field(..., min_length=6)