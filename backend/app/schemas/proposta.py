# backend/app/schemas/proposta.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime, date

# Schema simples para Cliente
class ClienteParaProposta(BaseModel):
    id: int
    razao_social: Optional[str] = "Cliente sem nome"  # Aceita None com valor padrão
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Schema simples para Usuario
class UsuarioParaProposta(BaseModel):
    id: int
    nome: str
    email: str

    model_config = ConfigDict(from_attributes=True)

# --- Itens da Proposta ---

class PropostaItemBase(BaseModel):
    produto_nome: str
    descricao: Optional[str] = None
    valor: float
    rendimento_litros: Optional[str] = None
    custo_por_litro: Optional[float] = None

class PropostaItemCreate(PropostaItemBase):
    pass

class PropostaItem(PropostaItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- Proposta Principal ---

class PropostaBase(BaseModel):
    cliente_id: int
    status: str = "RASCUNHO"
    observacoes: Optional[str] = None

class PropostaCreate(PropostaBase):
    itens: List[PropostaItemCreate]

class PropostaUpdate(BaseModel):
    status: Optional[str] = None
    observacoes: Optional[str] = None
    data_validade: Optional[date] = None

class Proposta(PropostaBase):
    id: int
    data_criacao: datetime
    data_validade: Optional[date] = None
    
    # Relações com outros objetos
    usuario: UsuarioParaProposta
    cliente: ClienteParaProposta
    itens: List[PropostaItem]

    model_config = ConfigDict(from_attributes=True)
