from pydantic import BaseModel, Field, validator, ConfigDict
from datetime import datetime
from typing import Optional, Literal
from enum import Enum
from .usuario import Usuario
from .produto import Produto

OrigemMovimentacao = Literal['VENDA', 'DEVOLUCAO', 'CORRECAO_MANUAL', 'COMPRA', 'AJUSTE', 'OUTRO']

class MotivoMovimentacao(str, Enum):
    CARREGAMENTO = "CARREGAMENTO"
    DEVOLUCAO = "DEVOLUCAO"
    AJUSTE_FISICO = "AJUSTE_FISICO"
    PERDA_AVARIA = "PERDA_AVARIA"
    TRANSFERENCIA_INTERNA = "TRANSFERENCIA_INTERNA"

class StatusMovimentacao(str, Enum):
    PENDENTE = "PENDENTE"
    CONFIRMADO = "CONFIRMADO"
    REJEITADO = "REJEITADO"

class MovimentacaoEstoqueBase(BaseModel):
    produto_id: int
    quantidade: float = Field(..., gt=0, description="A quantidade deve ser maior que zero.")
    observacao: Optional[str] = None
    origem: Optional[OrigemMovimentacao] = None

class MovimentacaoEstoqueCreate(MovimentacaoEstoqueBase):
    tipo_movimentacao: str
    motivo_movimentacao: Optional[MotivoMovimentacao] = None
    observacao_motivo: Optional[str] = None

    @validator('tipo_movimentacao')
    def tipo_deve_ser_valido(cls, v):
        tipo_normalizado = v.upper()
        if tipo_normalizado not in ['ENTRADA', 'SAIDA']:
            raise ValueError("O tipo de movimentação deve ser 'ENTRADA' ou 'SAIDA'")
        return tipo_normalizado

class MovimentacaoEstoquePendenteCreate(MovimentacaoEstoqueBase):
    tipo_movimentacao: str
    motivo_movimentacao: MotivoMovimentacao = Field(..., description="Motivo obrigatório para movimentação pendente")
    observacao_motivo: Optional[str] = Field(None, description="Observações adicionais sobre o motivo")

    @validator('tipo_movimentacao')
    def tipo_deve_ser_valido(cls, v):
        tipo_normalizado = v.upper()
        if tipo_normalizado not in ['ENTRADA', 'SAIDA']:
            raise ValueError("O tipo de movimentação deve ser 'ENTRADA' ou 'SAIDA'")
        return tipo_normalizado

class MovimentacaoEstoqueAprovacao(BaseModel):
    motivo_rejeicao: Optional[str] = None

class MovimentacaoEstoqueEdicao(BaseModel):
    produto_id: Optional[int] = None
    quantidade: Optional[float] = Field(None, gt=0)
    tipo_movimentacao: Optional[str] = None
    motivo_movimentacao: Optional[MotivoMovimentacao] = None
    observacao: Optional[str] = None
    observacao_motivo: Optional[str] = None

    @validator('tipo_movimentacao')
    def tipo_deve_ser_valido(cls, v):
        if v is None:
            return v
        tipo_normalizado = v.upper()
        if tipo_normalizado not in ['ENTRADA', 'SAIDA']:
            raise ValueError("O tipo de movimentação deve ser 'ENTRADA' ou 'SAIDA'")
        return tipo_normalizado

class MovimentacaoEstoque(MovimentacaoEstoqueBase):
    id: int
    tipo_movimentacao: str
    usuario_id: int
    data_movimentacao: datetime
    quantidade_antes: Optional[float] = None
    quantidade_depois: Optional[float] = None
    status: StatusMovimentacao
    aprovado_por_id: Optional[int] = None
    data_aprovacao: Optional[datetime] = None
    motivo_rejeicao: Optional[str] = None
    motivo_movimentacao: Optional[MotivoMovimentacao] = None
    
    model_config = ConfigDict(from_attributes=True)

class MovimentacaoEstoqueResponse(MovimentacaoEstoqueBase):
    id: int
    tipo_movimentacao: str
    data_movimentacao: datetime
    usuario: Optional[Usuario] = None
    produto: Optional[Produto] = None
    quantidade_antes: Optional[float] = None
    quantidade_depois: Optional[float] = None
    status: StatusMovimentacao
    aprovado_por: Optional[Usuario] = None
    data_aprovacao: Optional[datetime] = None
    motivo_rejeicao: Optional[str] = None
    motivo_movimentacao: Optional[MotivoMovimentacao] = None
    observacao_motivo: Optional[str] = None

    class Config:
        from_attributes = True
