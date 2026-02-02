"""
Serviço para obter regras de sugestão de compra por empresa.
Usado por PurchaseSuggestionService e ClientePurchaseSuggestionService.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from ..db import models

DEFAULTS = {
    "lead_time_dias": 7,
    "cobertura_dias": 14,
    "dias_analise": 90,
    "min_vendas_historico": 2,
    "margem_seguranca": 1.2,
    "margem_adicional_cobertura": 1.15,
    "dias_antecedencia_cliente": 7,
}


def get_regras_empresa(db: Session, empresa_id: int) -> Dict[str, Any]:
    """
    Retorna as regras de sugestão de compra da empresa.
    Se não houver registro, retorna os valores padrão.
    """
    regras = db.query(models.RegrasSugestaoCompra).filter(
        models.RegrasSugestaoCompra.empresa_id == empresa_id
    ).first()
    if not regras:
        return DEFAULTS.copy()
    return {
        "lead_time_dias": regras.lead_time_dias,
        "cobertura_dias": regras.cobertura_dias,
        "dias_analise": regras.dias_analise,
        "min_vendas_historico": regras.min_vendas_historico,
        "margem_seguranca": regras.margem_seguranca,
        "margem_adicional_cobertura": regras.margem_adicional_cobertura,
        "dias_antecedencia_cliente": regras.dias_antecedencia_cliente,
    }
