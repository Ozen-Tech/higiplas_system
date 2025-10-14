# /backend/app/schemas/cliente_v2.py
"""
Schema simplificado para clientes - v2
Focado em eficiência e praticidade para vendedores de rua
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class TipoPessoa(str, Enum):
    FISICA = "FISICA"
    JURIDICA = "JURIDICA"

class StatusCliente(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    PROSPECTO = "PROSPECTO"  # Cliente em potencial

class ClienteBase(BaseModel):
    """Base para cliente - campos essenciais apenas"""
    nome: str = Field(..., min_length=3, max_length=200, description="Nome ou razão social")
    telefone: str = Field(..., min_length=10, max_length=20, description="WhatsApp ou telefone principal")
    tipo_pessoa: TipoPessoa = TipoPessoa.FISICA
    cpf_cnpj: Optional[str] = Field(None, description="CPF ou CNPJ (opcional)")

    # Localização simplificada
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)

    # Email
    email: Optional[str] = Field(None, max_length=200, description="Email do cliente")

    # Informações do vendedor
    observacoes: Optional[str] = Field(None, max_length=500, description="Notas do vendedor")
    referencia_localizacao: Optional[str] = Field(None, max_length=200, description="Ponto de referência")

    @validator('telefone')
    def clean_telefone(cls, v):
        """Remove caracteres não numéricos do telefone"""
        if v:
            return ''.join(filter(str.isdigit, v))
        return v

    @validator('cpf_cnpj')
    def clean_cpf_cnpj(cls, v):
        """Remove caracteres não numéricos do CPF/CNPJ"""
        if v:
            return ''.join(filter(str.isdigit, v))
        return v

class ClienteCreate(ClienteBase):
    """Schema para criar cliente - super simples"""
    pass

class ClienteUpdate(BaseModel):
    """Schema para atualizar cliente - todos os campos opcionais"""
    nome: Optional[str] = None
    telefone: Optional[str] = None
    tipo_pessoa: Optional[TipoPessoa] = None
    cpf_cnpj: Optional[str] = None
    email: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    observacoes: Optional[str] = None
    referencia_localizacao: Optional[str] = None
    status: Optional[StatusCliente] = None

class ClienteQuickCreate(BaseModel):
    """Criação ultra-rápida - apenas nome e telefone"""
    nome: str = Field(..., min_length=3)
    telefone: str = Field(..., min_length=10)

class ClienteResponse(ClienteBase):
    """Schema de resposta - inclui campos do sistema"""
    id: int
    status: StatusCliente = StatusCliente.ATIVO
    vendedor_id: int
    vendedor_nome: Optional[str] = None
    empresa_id: int

    # Estatísticas
    total_vendas: Optional[float] = 0
    ultima_venda: Optional[datetime] = None

    # Timestamps
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

class ClienteList(BaseModel):
    """Resposta para listagem - informações mínimas"""
    id: int
    nome: str
    telefone: str
    bairro: Optional[str]
    cidade: Optional[str]
    status: StatusCliente
    ultima_venda: Optional[datetime]

    class Config:
        from_attributes = True

class ClienteSearch(BaseModel):
    """Parâmetros de busca"""
    termo: Optional[str] = Field(None, description="Nome, telefone ou CPF/CNPJ")
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    status: Optional[StatusCliente] = None
    vendedor_id: Optional[int] = None

class ClienteBulkCreate(BaseModel):
    """Criação em lote de clientes"""
    clientes: list[ClienteCreate]

class ClienteStats(BaseModel):
    """Estatísticas do cliente"""
    total_orcamentos: int = 0
    total_vendido: float = 0
    ticket_medio: float = 0
    produtos_mais_comprados: list[dict] = []
    historico_vendas: list[dict] = []
