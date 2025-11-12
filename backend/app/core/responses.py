"""
Respostas padronizadas para a API.

Fornece estruturas consistentes para respostas de sucesso, erro e paginação,
facilitando o consumo da API pelo frontend.
"""

from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """
    Resposta padrão de sucesso.
    
    Args:
        success: Indica se a operação foi bem-sucedida (sempre True)
        data: Dados retornados pela operação
        message: Mensagem opcional de sucesso
        timestamp: Timestamp da resposta
    """
    success: bool = Field(default=True, description="Indica sucesso da operação")
    data: T = Field(description="Dados retornados")
    message: Optional[str] = Field(default=None, description="Mensagem de sucesso")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da resposta")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """
    Resposta padrão de erro.
    
    Args:
        success: Indica se a operação foi bem-sucedida (sempre False)
        error: Tipo do erro
        message: Mensagem de erro
        details: Detalhes adicionais do erro (opcional)
        timestamp: Timestamp da resposta
    """
    success: bool = Field(default=False, description="Indica falha da operação")
    error: str = Field(description="Tipo do erro")
    message: str = Field(description="Mensagem de erro")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Detalhes adicionais")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da resposta")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Resposta paginada.
    
    Args:
        items: Lista de itens da página atual
        total: Total de itens disponíveis
        page: Página atual (1-indexed)
        page_size: Tamanho da página
        total_pages: Total de páginas
        has_next: Indica se há próxima página
        has_previous: Indica se há página anterior
    """
    items: List[T] = Field(description="Itens da página atual")
    total: int = Field(description="Total de itens disponíveis")
    page: int = Field(ge=1, description="Página atual (1-indexed)")
    page_size: int = Field(ge=1, description="Tamanho da página")
    total_pages: int = Field(description="Total de páginas")
    has_next: bool = Field(description="Indica se há próxima página")
    has_previous: bool = Field(description="Indica se há página anterior")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """
        Factory method para criar resposta paginada.
        
        Args:
            items: Lista de itens
            total: Total de itens
            page: Página atual
            page_size: Tamanho da página
            
        Returns:
            Resposta paginada
        """
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )


class MessageResponse(BaseModel):
    """
    Resposta simples com mensagem.
    
    Args:
        success: Indica sucesso da operação
        message: Mensagem da resposta
        timestamp: Timestamp da resposta
    """
    success: bool = Field(description="Indica sucesso da operação")
    message: str = Field(description="Mensagem da resposta")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da resposta")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

