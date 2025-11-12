"""
Constantes e Enums centralizados para o sistema Higiplas.

Centraliza valores hardcoded, status, tipos e configurações de negócio
para facilitar manutenção e evitar erros de digitação.
"""

from enum import Enum
from typing import List


class OrcamentoStatus(str, Enum):
    """Status possíveis para um orçamento."""
    RASCUNHO = "RASCUNHO"
    ENVIADO = "ENVIADO"
    APROVADO = "APROVADO"
    REJEITADO = "REJEITADO"
    FINALIZADO = "FINALIZADO"


class TipoMovimentacao(str, Enum):
    """Tipos de movimentação de estoque."""
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"


class OrigemMovimentacao(str, Enum):
    """Origens possíveis para uma movimentação de estoque."""
    VENDA = "VENDA"
    DEVOLUCAO = "DEVOLUCAO"
    CORRECAO_MANUAL = "CORRECAO_MANUAL"
    COMPRA = "COMPRA"
    AJUSTE = "AJUSTE"
    OUTRO = "OUTRO"


# Status válidos para confirmação de orçamento
STATUS_CONFIRMAVEL: List[str] = [
    OrcamentoStatus.ENVIADO.value,
    OrcamentoStatus.APROVADO.value
]

# Origens automáticas válidas para análise de vendas (exclui manuais)
ORIGENS_AUTOMATICAS: List[str] = [
    OrigemMovimentacao.VENDA.value,
    OrigemMovimentacao.DEVOLUCAO.value,
    OrigemMovimentacao.COMPRA.value,
    OrigemMovimentacao.OUTRO.value
]

# Origens manuais (não devem ser consideradas em análises de vendas)
ORIGENS_MANUAIS: List[str] = [
    OrigemMovimentacao.CORRECAO_MANUAL.value,
    OrigemMovimentacao.AJUSTE.value
]

# Mensagens de erro padronizadas
MENSAGENS_ERRO = {
    "RECURSO_NAO_ENCONTRADO": "{recurso} não encontrado(a).",
    "ESTOQUE_INSUFICIENTE": "Estoque insuficiente para '{produto}'. Disponível: {disponivel}, Solicitado: {solicitado}",
    "PERMISSAO_NEGADA": "Acesso negado. Você não tem permissão para realizar esta operação.",
    "STATUS_INVALIDO": "Status '{status_atual}' inválido para esta operação. Status válidos: {status_validos}",
    "VALIDACAO_FALHOU": "Validação falhou: {detalhes}",
}

# Configurações de negócio
CONFIGURACOES = {
    "META_VENDAS_DIA": 2000.00,  # Meta diária de vendas para vendedores
    "ESTOQUE_MINIMO_PADRAO": 0,
    "DIAS_ANALISE_ESTOQUE_MINIMO": 90,
    "MARGEM_SEGURANCA_ESTOQUE": 1.5,
}

# Limites e paginação
LIMITES = {
    "PRODUTOS_MAIS_VENDIDOS": 50,
    "HISTORICO_MOVIMENTACOES": 100,
    "BUSCA_PRODUTOS": 100,
    "BUSCA_CLIENTES": 50,
}

