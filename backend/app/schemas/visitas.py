"""
Schemas Pydantic para o sistema de visitas de vendedores.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class VisitaVendedorBase(BaseModel):
    """Schema base para visita de vendedor."""
    vendedor_id: int
    cliente_id: Optional[int] = None
    latitude: float = Field(..., description="Latitude GPS da visita")
    longitude: float = Field(..., description="Longitude GPS da visita")
    endereco_completo: Optional[str] = None
    motivo_visita: Optional[str] = None
    observacoes: Optional[str] = None
    foto_comprovante: Optional[str] = None
    empresa_id: int


class VisitaVendedorCreate(VisitaVendedorBase):
    """Schema para criação de visita."""
    confirmada: bool = False


class VisitaVendedorUpdate(BaseModel):
    """Schema para atualização de visita (apenas se não confirmada)."""
    cliente_id: Optional[int] = None
    motivo_visita: Optional[str] = None
    observacoes: Optional[str] = None
    foto_comprovante: Optional[str] = None


class VisitaVendedorConfirm(BaseModel):
    """Schema para confirmação de visita."""
    confirmar: bool = True


class VisitaVendedorResponse(VisitaVendedorBase):
    """Schema de resposta com dados completos da visita."""
    id: int
    data_visita: datetime
    confirmada: bool
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    # Dados relacionados
    vendedor_nome: Optional[str] = None
    cliente_nome: Optional[str] = None
    empresa_nome: Optional[str] = None
    
    class Config:
        from_attributes = True


class VisitaVendedorListResponse(BaseModel):
    """Schema para lista de visitas."""
    visitas: List[VisitaVendedorResponse]
    total: int
    pagina: int = 1
    por_pagina: int = 20


class VisitaVendedorStatsResponse(BaseModel):
    """Schema para estatísticas de visitas."""
    total_visitas: int
    visitas_hoje: int
    visitas_semana: int
    visitas_mes: int
    visitas_confirmadas: int
    visitas_pendentes: int
