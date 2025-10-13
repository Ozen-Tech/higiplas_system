# backend/app/schemas/produtos_mais_vendidos.py
"""
Schemas atualizados para produtos mais vendidos baseados em MovimentacaoEstoque
Inclui métricas avançadas e estruturas profissionais
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

class ProdutoMaisVendidoDetalhado(BaseModel):
    """Schema detalhado para produto mais vendido com métricas avançadas"""
    produto_id: int
    nome: str
    codigo: str
    categoria: str
    preco_atual: float = Field(..., description="Preço atual do produto")
    estoque_atual: int = Field(..., description="Quantidade atual em estoque")

    # Métricas de vendas
    total_quantidade_vendida: float = Field(..., description="Quantidade total vendida no período")
    valor_total_vendido: float = Field(..., description="Valor total vendido no período")
    numero_vendas: int = Field(..., description="Número de transações de venda")
    quantidade_media_por_venda: float = Field(..., description="Quantidade média por transação")
    frequencia_vendas_por_dia: float = Field(..., description="Frequência de vendas por dia")

    # Datas importantes
    primeira_venda: datetime = Field(..., description="Data da primeira venda no período")
    ultima_venda: datetime = Field(..., description="Data da última venda no período")
    dias_desde_ultima_venda: int = Field(..., description="Dias desde a última venda")

    # Métricas calculadas
    @property
    def ticket_medio(self) -> float:
        """Valor médio por venda"""
        return round(self.valor_total_vendido / max(self.numero_vendas, 1), 2)

    @property
    def rotatividade_estoque(self) -> float:
        """Quantas vezes o estoque atual foi vendido no período"""
        return round(self.total_quantidade_vendida / max(self.estoque_atual, 1), 2)

    @property
    def status_estoque(self) -> str:
        """Status do estoque baseado na rotatividade"""
        if self.dias_desde_ultima_venda > 30:
            return "PARADO"
        elif self.rotatividade_estoque > 5:
            return "ALTA_ROTACAO"
        elif self.rotatividade_estoque > 2:
            return "MEDIA_ROTACAO"
        else:
            return "BAIXA_ROTACAO"

    model_config = ConfigDict(from_attributes=True)

class EstatisticasGerais(BaseModel):
    """Estatísticas gerais do período analisado"""
    total_produtos_analisados: int
    periodo_analise_dias: int
    data_inicio: date
    data_fim: date
    total_quantidade_vendida: float
    total_valor_vendido: float
    ticket_medio: float
    produto_mais_vendido: Optional[str] = None
    categoria_mais_vendida: Optional[str] = None

class ProdutosMaisVendidosResponse(BaseModel):
    """Response completa para produtos mais vendidos"""
    produtos: List[ProdutoMaisVendidoDetalhado]
    estatisticas: EstatisticasGerais
    filtros_aplicados: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

class TendenciaMensal(BaseModel):
    """Dados de tendência mensal para um produto"""
    mes_ano: str = Field(..., description="Mês no formato YYYY-MM")
    produto_nome: str
    quantidade_vendida: float
    valor_vendido: float

class TendenciasVendasResponse(BaseModel):
    """Response para análise de tendências"""
    tendencias: List[TendenciaMensal]
    periodo_meses: int
    produto_especifico: bool = Field(..., description="Se a análise é para um produto específico")

class ComparativoVendedor(BaseModel):
    """Comparativo de performance entre vendedores"""
    vendedor_id: int
    vendedor_nome: str
    total_quantidade_vendida: float
    total_valor_vendido: float
    produtos_diferentes_vendidos: int
    numero_vendas: int
    ticket_medio: float

# Schemas para filtros avançados
class FiltrosProdutosMaisVendidos(BaseModel):
    """Filtros disponíveis para consulta"""
    periodo_dias: Optional[int] = Field(365, description="Período em dias")
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    limite: int = Field(50, ge=1, le=500, description="Limite de produtos")
    ordenar_por: str = Field("quantidade", pattern="^(quantidade|valor|frequencia)$")
    vendedor_id: Optional[int] = None
    categoria: Optional[str] = None
    apenas_com_estoque: bool = Field(False, description="Apenas produtos com estoque > 0")

# Schemas para dashboard/cards
class CardMetrica(BaseModel):
    """Card de métrica para dashboard"""
    titulo: str
    valor: str
    variacao: Optional[float] = None  # Percentual de variação
    variacao_tipo: Optional[str] = None  # "positiva", "negativa", "neutra"
    icone: Optional[str] = None
    cor: Optional[str] = None

class DashboardProdutosMaisVendidos(BaseModel):
    """Dashboard completo com cards e métricas"""
    cards_metricas: List[CardMetrica]
    top_5_produtos: List[ProdutoMaisVendidoDetalhado]
    grafico_tendencias: List[TendenciaMensal]
    alerta_estoque_baixo: List[ProdutoMaisVendidoDetalhado]

    model_config = ConfigDict(from_attributes=True)

# Schemas para relatórios
class RelatorioVendasProduto(BaseModel):
    """Relatório detalhado de vendas de um produto"""
    produto: ProdutoMaisVendidoDetalhado
    vendas_por_mes: List[TendenciaMensal]
    vendedores_que_venderam: List[ComparativoVendedor]
    clientes_que_compraram: List[Dict[str, Any]]  # Será implementado depois

class ConfiguracaoRelatorio(BaseModel):
    """Configurações para geração de relatórios"""
    incluir_graficos: bool = True
    incluir_detalhes_vendedores: bool = True
    incluir_historico_precos: bool = False
    formato_saida: str = Field("json", pattern="^(json|pdf|excel)$")

# Schemas para cache e performance
class CacheInfo(BaseModel):
    """Informações sobre cache dos dados"""
    cache_ativo: bool
    ultima_atualizacao: datetime
    proxima_atualizacao: datetime
    tempo_cache_segundos: int

class ResponseComCache(BaseModel):
    """Response que inclui informações de cache"""
    dados: ProdutosMaisVendidosResponse
    cache_info: CacheInfo