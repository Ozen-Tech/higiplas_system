# /backend/app/schemas/cliente.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime
from enum import Enum

class EmpresaVinculada(str, Enum):
    HIGIPLAS = "HIGIPLAS"
    HIGITEC = "HIGITEC"

class StatusPagamento(str, Enum):
    BOM_PAGADOR = "BOM_PAGADOR"
    MAU_PAGADOR = "MAU_PAGADOR"

# Cliente Base
class ClienteBase(BaseModel):
    razao_social: str
    cnpj: Optional[str] = None
    endereco: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    empresa_vinculada: EmpresaVinculada
    status_pagamento: StatusPagamento = StatusPagamento.BOM_PAGADOR

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    razao_social: Optional[str] = None
    cnpj: Optional[str] = None
    endereco: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    empresa_vinculada: Optional[EmpresaVinculada] = None
    status_pagamento: Optional[StatusPagamento] = None

class Cliente(ClienteBase):
    id: int
    data_criacao: datetime
    empresa_id: int
    
    model_config = ConfigDict(from_attributes=True)

# Histórico de Pagamentos
class StatusPagamentoHistorico(str, Enum):
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    ATRASADO = "ATRASADO"

class HistoricoPagamentoBase(BaseModel):
    valor: float
    data_vencimento: date
    data_pagamento: Optional[date] = None
    status: StatusPagamentoHistorico = StatusPagamentoHistorico.PENDENTE
    numero_nf: Optional[str] = None
    observacoes: Optional[str] = None

class HistoricoPagamentoCreate(HistoricoPagamentoBase):
    cliente_id: int
    orcamento_id: Optional[int] = None

class HistoricoPagamentoUpdate(BaseModel):
    valor: Optional[float] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    status: Optional[StatusPagamentoHistorico] = None
    numero_nf: Optional[str] = None
    observacoes: Optional[str] = None

class HistoricoPagamento(HistoricoPagamentoBase):
    id: int
    data_criacao: datetime
    cliente_id: int
    orcamento_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

# Cliente com histórico completo
class ClienteCompleto(Cliente):
    historico_pagamentos: List[HistoricoPagamento] = []
    
    model_config = ConfigDict(from_attributes=True)