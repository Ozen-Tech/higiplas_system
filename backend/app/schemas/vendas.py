# /backend/app/schemas/vendas.py
"""
Schemas Pydantic para o módulo de vendas mobile
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

# ============= DASHBOARD =============

class VendedorDashboard(BaseModel):
    """Dashboard do vendedor com métricas do dia"""
    total_vendido_hoje: float = Field(..., description="Total em R$ vendido hoje")
    quantidade_pedidos_hoje: int = Field(..., description="Número de pedidos finalizados")
    clientes_visitados_hoje: int = Field(..., description="Clientes únicos atendidos")
    meta_dia: float = Field(..., description="Meta de vendas do dia")
    progresso_meta: float = Field(..., description="Progresso em % da meta")

# ============= CLIENTES =============

class ClienteRapido(BaseModel):
    """Informações simplificadas de cliente para busca rápida"""
    id: int
    nome: str
    telefone: str
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    ultima_compra: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============= PRODUTOS =============

class EstatisticasPreco(BaseModel):
    """Estatísticas de preços históricos de um produto"""
    preco_maior: Optional[float] = None
    preco_medio: Optional[float] = None
    preco_menor: Optional[float] = None
    total_vendas: int = 0

class ProdutoVenda(BaseModel):
    """Produto disponível para venda"""
    id: int
    nome: str
    codigo: str
    preco: float
    estoque_disponivel: int
    categoria: str
    unidade_medida: str
    estatisticas_preco: Optional[EstatisticasPreco] = None
    
    class Config:
        from_attributes = True

# ============= VENDA =============

class ItemVendaCreate(BaseModel):
    """Item individual de uma venda"""
    produto_id: int = Field(..., description="ID do produto")
    quantidade: float = Field(..., gt=0, description="Quantidade vendida")

class VendaCreate(BaseModel):
    """Dados para criar uma venda"""
    cliente_id: int = Field(..., description="ID do cliente")
    itens: List[ItemVendaCreate] = Field(..., min_items=1, description="Produtos vendidos")
    observacao: Optional[str] = Field(None, max_length=500, description="Observações da venda")
    forma_pagamento: Optional[str] = Field(None, description="Forma de pagamento")

class ItemVendaResponse(BaseModel):
    """Detalhes de um item processado"""
    produto_nome: str
    quantidade: float
    valor_unitario: float
    valor_total: float

class VendaResponse(BaseModel):
    """Resposta após criar uma venda"""
    sucesso: bool
    mensagem: str
    venda_id: str
    cliente_nome: str
    total_venda: float
    itens_processados: int
    detalhes: List[dict]

# ============= HISTÓRICO =============

class VendaHistorico(BaseModel):
    """Registro de venda no histórico"""
    data: datetime
    cliente_nome: str
    total: float
    quantidade_itens: int
    observacao: Optional[str] = None

# ============= ESTATÍSTICAS =============

class ProdutoMaisVendido(BaseModel):
    """Produto no ranking de mais vendidos"""
    produto: str
    quantidade: float
    valor_total: float

class EstatisticasVendas(BaseModel):
    """Estatísticas de vendas do período"""
    total_vendido: float
    quantidade_vendas: int
    ticket_medio: float
    produtos_mais_vendidos: List[dict]