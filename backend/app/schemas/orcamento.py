# /backend/app/schemas/orcamento.py - VERSÃO FINAL CORRIGIDA

from pydantic import BaseModel, ConfigDict, model_validator
from typing import List, Optional
from datetime import datetime

# Importa os outros schemas que serão usados aqui
from .produto import Produto
from .usuario import Usuario
# NÃO vamos mais importar ClienteResponse de cliente_v2

# ================== CORREÇÃO IMPORTANTE ==================
# Criamos um schema mais simples para o Cliente, que representa
# exatamente o que o banco de dados retorna. Isso resolve o erro de validação.
class ClienteParaOrcamento(BaseModel):
    id: int
    razao_social: str # Usamos o nome exato da coluna do banco: 'razao_social'
    telefone: Optional[str] = None # O telefone pode ser nulo

    model_config = ConfigDict(from_attributes=True)


# --- Itens do Orçamento ---

class OrcamentoItemBase(BaseModel):
    quantidade: int
    
class OrcamentoItemCreate(OrcamentoItemBase):
    produto_id: Optional[int] = None  # Opcional: se None, deve ter nome_produto_personalizado
    nome_produto_personalizado: Optional[str] = None  # Opcional: se None, deve ter produto_id
    preco_unitario: float
    
    @model_validator(mode='after')
    def validate_produto_or_nome(self):
        """Valida que ou produto_id ou nome_produto_personalizado está presente"""
        if not self.produto_id and not self.nome_produto_personalizado:
            raise ValueError("Deve fornecer produto_id ou nome_produto_personalizado")
        if self.produto_id and self.nome_produto_personalizado:
            raise ValueError("Forneça apenas produto_id OU nome_produto_personalizado, não ambos")
        return self

class OrcamentoItem(OrcamentoItemBase):
    id: int
    produto_id: int
    preco_unitario_congelado: float
    produto: Produto

    model_config = ConfigDict(from_attributes=True)


# --- Orçamento Principal ---

class OrcamentoBase(BaseModel):
    cliente_id: int
    condicao_pagamento: str
    status: str = "RASCUNHO"

class OrcamentoCreate(OrcamentoBase):
    itens: List[OrcamentoItemCreate]

class Orcamento(OrcamentoBase):
    id: int
    data_criacao: datetime
    token_compartilhamento: Optional[str] = None
    
    # Relações com outros objetos
    usuario: Usuario
    # ================== CORREÇÃO IMPORTANTE ==================
    # Trocamos o schema complexo 'ClienteResponse' pelo nosso schema simples.
    cliente: ClienteParaOrcamento
    itens: List[OrcamentoItem]

    model_config = ConfigDict(from_attributes=True)

# Schemas para atualização (admin)
class OrcamentoItemUpdate(BaseModel):
    id: Optional[int] = None  # Se None, é um novo item
    produto_id: Optional[int] = None  # Opcional: se None, deve ter nome_produto_personalizado
    nome_produto_personalizado: Optional[str] = None  # Opcional: nome do produto personalizado
    quantidade: int
    preco_unitario: float
    
    @model_validator(mode='after')
    def validate_produto_or_nome(self):
        """Valida que ou produto_id ou nome_produto_personalizado está presente"""
        if not self.produto_id and not self.nome_produto_personalizado:
            raise ValueError("Deve fornecer produto_id ou nome_produto_personalizado")
        if self.produto_id and self.nome_produto_personalizado:
            raise ValueError("Forneça apenas produto_id OU nome_produto_personalizado, não ambos")
        return self

class OrcamentoUpdate(BaseModel):
    cliente_id: Optional[int] = None
    condicao_pagamento: Optional[str] = None
    status: Optional[str] = None
    itens: Optional[List[OrcamentoItemUpdate]] = None

class OrcamentoStatusUpdate(BaseModel):
    status: str

# Schema para range de preços por cliente-produto
class RangePrecosClienteProduto(BaseModel):
    """Schema para retornar range de preços de um produto para um cliente específico"""
    cliente_id: int
    produto_id: int
    preco_padrao: float  # Preço do sistema do produto
    preco_minimo: Optional[float] = None  # Menor preço já vendido para este cliente
    preco_maximo: Optional[float] = None  # Maior preço já vendido para este cliente
    
    model_config = ConfigDict(from_attributes=True)


# Schemas para sugestões inteligentes de preços
class PrecoCliente(BaseModel):
    """Range de preços do histórico com o cliente"""
    ultimo: Optional[float] = None      # Último preço vendido
    minimo: Optional[float] = None      # Menor preço já vendido
    maximo: Optional[float] = None      # Maior preço já vendido
    medio: Optional[float] = None       # Média de preços


class SugestaoProdutoExpandida(BaseModel):
    """Sugestão expandida com range de preços e preço do sistema"""
    produto_id: int
    produto_nome: Optional[str] = None
    preco_sistema: float                # Preço de venda cadastrado no produto
    preco_cliente: Optional[PrecoCliente] = None  # Range de preços do cliente
    quantidade_sugerida: Optional[int] = None
    total_vendas: int = 0               # Quantas vezes vendeu para este cliente
    historico_disponivel: bool = False


class SugestoesClienteResponse(BaseModel):
    """Resposta do endpoint de sugestões com dados expandidos"""
    cliente_id: int
    sugestoes: List[SugestaoProdutoExpandida]
    total_produtos: int