"""
Exceções customizadas para o sistema Higiplas.

Fornece uma hierarquia de exceções específicas para diferentes tipos de erros,
facilitando tratamento, logging e respostas consistentes da API.
"""

from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """Classe base para todas as exceções customizadas da aplicação."""
    
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.detail = detail
        self.status_code = status_code


class ValidationException(BaseAppException):
    """Exceção para erros de validação de negócio."""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST
        )
        self.field = field


class NotFoundError(BaseAppException):
    """Exceção para recursos não encontrados."""
    
    def __init__(self, resource: str, resource_id: Optional[int] = None):
        if resource_id:
            detail = f"{resource} com ID {resource_id} não encontrado(a)."
        else:
            detail = f"{resource} não encontrado(a)."
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND
        )
        self.resource = resource
        self.resource_id = resource_id


class BusinessRuleException(BaseAppException):
    """Exceção para violação de regras de negócio."""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class StockInsufficientError(BusinessRuleException):
    """Exceção para estoque insuficiente."""
    
    def __init__(
        self,
        produto_nome: str,
        quantidade_disponivel: float,
        quantidade_solicitada: float
    ):
        detail = (
            f"Estoque insuficiente para '{produto_nome}'. "
            f"Disponível: {quantidade_disponivel}, Solicitado: {quantidade_solicitada}"
        )
        super().__init__(detail=detail)
        self.produto_nome = produto_nome
        self.quantidade_disponivel = quantidade_disponivel
        self.quantidade_solicitada = quantidade_solicitada


class PermissionDeniedError(BaseAppException):
    """Exceção para acesso negado por falta de permissão."""
    
    def __init__(self, detail: str = "Acesso negado. Você não tem permissão para realizar esta operação."):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN
        )


class OrcamentoStatusError(BusinessRuleException):
    """Exceção para operações inválidas com status de orçamento."""
    
    def __init__(
        self,
        orcamento_id: int,
        status_atual: str,
        operacao: str,
        status_validos: List[str]
    ):
        status_validos_str = ", ".join(status_validos)
        detail = (
            f"Orçamento #{orcamento_id} com status '{status_atual}' não pode ser {operacao}. "
            f"Status válidos: {status_validos_str}"
        )
        super().__init__(detail=detail)
        self.orcamento_id = orcamento_id
        self.status_atual = status_atual
        self.operacao = operacao
        self.status_validos = status_validos

