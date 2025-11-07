from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class PurchaseSuggestionBase(BaseModel):
    """Schema base para sugestão de compra."""
    produto_id: int
    produto_nome: str
    codigo: Optional[str] = None
    categoria: Optional[str] = None
    estoque_atual: int
    estoque_minimo_atual: int
    estoque_minimo_calculado: int
    demanda_media_diaria: float
    demanda_maxima_diaria: float
    total_vendido_periodo: float
    numero_vendas: int
    dias_com_vendas: int
    dias_cobertura_atual: float
    quantidade_sugerida: int
    status: str  # CRÍTICO, BAIXO, ADEQUADO
    tem_historico_suficiente: bool
    fornecedor_id: Optional[int] = None
    fornecedor_nome: Optional[str] = None
    preco_custo: Optional[float] = None
    preco_venda: Optional[float] = None
    valor_estimado_compra: float
    periodo_analise_dias: int
    lead_time_dias: int
    coverage_days: int


class PurchaseSuggestion(PurchaseSuggestionBase):
    """Schema completo para sugestão de compra."""
    model_config = ConfigDict(from_attributes=True)


class PurchaseSuggestionResponse(BaseModel):
    """Resposta com lista de sugestões de compra."""
    total_sugestoes: int
    sugestoes_criticas: int
    sugestoes_baixas: int
    sugestoes: List[PurchaseSuggestion]
    data_analise: datetime


class ProductAnalysisResponse(BaseModel):
    """Resposta com análise completa de um produto."""
    produto_id: int
    produto_nome: str
    codigo: Optional[str] = None
    categoria: Optional[str] = None
    estoque_atual: int
    estoque_minimo_atual: int
    estoque_minimo_calculado: int
    demanda_media_diaria: float
    demanda_maxima_diaria: float
    total_vendido_periodo: float
    numero_vendas: int
    dias_com_vendas: int
    dias_cobertura_atual: float
    quantidade_sugerida: int
    precisa_compra: bool
    status: str
    tem_historico_suficiente: bool
    fornecedor_id: Optional[int] = None
    fornecedor_nome: Optional[str] = None
    preco_custo: Optional[float] = None
    preco_venda: Optional[float] = None
    valor_estimado_compra: float
    periodo_analise_dias: int
    lead_time_dias: int
    coverage_days: int
    
    model_config = ConfigDict(from_attributes=True)

