from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

# Campos base que toda movimentação terá
class MovimentacaoEstoqueBase(BaseModel):
    produto_id: int
    tipo_movimentacao: str
    quantidade: int = Field(gt=0, description="A quantidade deve ser maior que zero")
    observacao: Optional[str] = None

    # Validador para garantir que o tipo de movimentação seja válido
    @validator('tipo_movimentacao')
    def tipo_movimentacao_must_be_valid(cls, v):
        if v.upper() not in ['ENTRADA', 'SAIDA']:
            raise ValueError("O tipo de movimentação deve ser 'ENTRADA' ou 'SAIDA'")
        return v.upper()

# Schema para criar uma nova movimentação (o que a API recebe)
class MovimentacaoEstoqueCreate(MovimentacaoEstoqueBase):
    pass

# Schema para ler uma movimentação (o que a API retorna)
# Inclui campos que são gerados pelo banco de dados
class MovimentacaoEstoque(MovimentacaoEstoqueBase):
    id: int
    data_movimentacao: datetime
    usuario_id: Optional[int] = None

    class Config:
        from_attributes = True # Antigo orm_mode = True