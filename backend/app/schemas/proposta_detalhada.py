# backend/app/schemas/proposta_detalhada.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ============= FICHA TÉCNICA =============

class FichaTecnicaBase(BaseModel):
    nome_produto: str
    dilucao_recomendada: Optional[str] = None
    dilucao_numerador: Optional[float] = None
    dilucao_denominador: Optional[float] = None
    rendimento_litro: Optional[float] = None
    modo_uso: Optional[str] = None
    arquivo_pdf_path: Optional[str] = None
    observacoes: Optional[str] = None


class FichaTecnicaCreate(FichaTecnicaBase):
    produto_id: Optional[int] = None


class FichaTecnicaUpdate(BaseModel):
    produto_id: Optional[int] = None
    nome_produto: Optional[str] = None
    dilucao_recomendada: Optional[str] = None
    dilucao_numerador: Optional[float] = None
    dilucao_denominador: Optional[float] = None
    rendimento_litro: Optional[float] = None
    modo_uso: Optional[str] = None
    arquivo_pdf_path: Optional[str] = None
    observacoes: Optional[str] = None


class FichaTecnica(FichaTecnicaBase):
    id: int
    produto_id: Optional[int] = None
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============= PRODUTO CONCORRENTE =============

class ProdutoConcorrenteBase(BaseModel):
    nome: str
    marca: Optional[str] = None
    preco_medio: Optional[float] = None
    rendimento_litro: Optional[float] = None
    dilucao: Optional[str] = None
    dilucao_numerador: Optional[float] = None
    dilucao_denominador: Optional[float] = None
    categoria: Optional[str] = None
    observacoes: Optional[str] = None


class ProdutoConcorrenteCreate(ProdutoConcorrenteBase):
    ativo: bool = True


class ProdutoConcorrenteUpdate(BaseModel):
    nome: Optional[str] = None
    marca: Optional[str] = None
    preco_medio: Optional[float] = None
    rendimento_litro: Optional[float] = None
    dilucao: Optional[str] = None
    dilucao_numerador: Optional[float] = None
    dilucao_denominador: Optional[float] = None
    categoria: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None


class ProdutoConcorrente(ProdutoConcorrenteBase):
    id: int
    ativo: bool
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============= PROPOSTA DETALHADA =============

class PropostaDetalhadaBase(BaseModel):
    orcamento_id: Optional[int] = None
    cliente_id: int
    produto_id: int
    quantidade_produto: float
    dilucao_aplicada: Optional[str] = None
    dilucao_numerador: Optional[float] = None
    dilucao_denominador: Optional[float] = None
    concorrente_id: Optional[int] = None
    observacoes: Optional[str] = None
    compartilhavel: bool = False


class PropostaDetalhadaCreate(PropostaDetalhadaBase):
    pass


class PropostaDetalhadaUpdate(BaseModel):
    orcamento_id: Optional[int] = None
    quantidade_produto: Optional[float] = None
    dilucao_aplicada: Optional[str] = None
    dilucao_numerador: Optional[float] = None
    dilucao_denominador: Optional[float] = None
    concorrente_id: Optional[int] = None
    observacoes: Optional[str] = None
    compartilhavel: Optional[bool] = None


class ComparacaoConcorrente(BaseModel):
    """Informações de comparação com um concorrente"""
    concorrente_id: int
    concorrente_nome: str
    concorrente_marca: Optional[str] = None
    preco_concorrente: Optional[float] = None
    rendimento_concorrente: Optional[float] = None
    custo_por_litro_concorrente: Optional[float] = None
    economia_percentual: Optional[float] = None
    economia_valor: Optional[float] = None


class PropostaDetalhadaResponse(PropostaDetalhadaBase):
    id: int
    vendedor_id: int
    ficha_tecnica_id: Optional[int] = None
    rendimento_total_litros: Optional[float] = None
    preco_produto: Optional[float] = None
    custo_por_litro_final: Optional[float] = None
    economia_vs_concorrente: Optional[float] = None
    economia_percentual: Optional[float] = None
    economia_valor: Optional[float] = None
    token_compartilhamento: Optional[str] = None
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None
    
    # Informações relacionadas
    produto_nome: Optional[str] = None
    cliente_nome: Optional[str] = None
    vendedor_nome: Optional[str] = None
    ficha_tecnica: Optional[FichaTecnica] = None
    concorrente: Optional[ProdutoConcorrente] = None
    comparacoes: Optional[List[ComparacaoConcorrente]] = None

    model_config = ConfigDict(from_attributes=True)


class PropostaDetalhadaCompleta(PropostaDetalhadaResponse):
    """Resposta completa com todos os dados calculados"""
    pass

