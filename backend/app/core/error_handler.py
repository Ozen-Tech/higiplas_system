"""
Handler global de exceções para a API.

Mapeia exceções customizadas para respostas HTTP consistentes,
facilitando tratamento de erros e melhorando a experiência do usuário.
"""

import traceback
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from .exceptions import (
    BaseAppException,
    ValidationException,
    NotFoundError,
    BusinessRuleException,
    StockInsufficientError,
    PermissionDeniedError,
    OrcamentoStatusError
)
from .responses import ErrorResponse
from .logger import api_logger as logger


async def base_app_exception_handler(
    request: Request,
    exc: BaseAppException
) -> JSONResponse:
    """
    Handler para exceções customizadas da aplicação.
    
    Args:
        request: Requisição HTTP
        exc: Exceção customizada
        
    Returns:
        Resposta JSON com detalhes do erro
    """
    logger.error(
        f"Exceção customizada: {type(exc).__name__} - {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )
    
    error_response = ErrorResponse(
        error=type(exc).__name__,
        message=exc.detail,
        details={
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handler para erros de validação do Pydantic.
    
    Args:
        request: Requisição HTTP
        exc: Exceção de validação
        
    Returns:
        Resposta JSON com detalhes dos erros de validação
    """
    errors = exc.errors()
    logger.warning(
        f"Erro de validação na requisição {request.method} {request.url.path}",
        extra={"errors": errors}
    )
    
    error_response = ErrorResponse(
        error="ValidationError",
        message="Erro de validação nos dados fornecidos",
        details={
            "errors": errors,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handler para erros do SQLAlchemy.
    
    Args:
        request: Requisição HTTP
        exc: Exceção do SQLAlchemy
        
    Returns:
        Resposta JSON com detalhes do erro
    """
    logger.error(
        f"Erro de banco de dados: {type(exc).__name__} - {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    # Erro de integridade (violação de constraint)
    if isinstance(exc, IntegrityError):
        error_response = ErrorResponse(
            error="DatabaseIntegrityError",
            message="Violação de integridade de dados. Verifique se os dados fornecidos são válidos.",
            details={
                "path": request.url.path,
                "method": request.method
            }
        )
        status_code = status.HTTP_400_BAD_REQUEST
    else:
        error_response = ErrorResponse(
            error="DatabaseError",
            message="Erro ao acessar o banco de dados. Tente novamente mais tarde.",
            details={
                "path": request.url.path,
                "method": request.method
            }
        )
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump()
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handler genérico para exceções não tratadas.
    
    Args:
        request: Requisição HTTP
        exc: Exceção genérica
        
    Returns:
        Resposta JSON com mensagem genérica de erro
    """
    # Capturar traceback como string para evitar problemas de serialização
    try:
        tb_str = traceback.format_exc()
    except Exception:
        tb_str = "Erro ao formatar traceback"
    
    logger.error(
        f"Exceção não tratada: {type(exc).__name__} - {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": tb_str
        },
        exc_info=True
    )
    
    # Garantir que os detalhes sejam serializáveis
    error_details = {
        "path": str(request.url.path),
        "method": str(request.method),
        "error_type": str(type(exc).__name__),
        "error_message": str(exc)
    }
    
    error_response = ErrorResponse(
        error="InternalServerError",
        message="Erro interno do servidor. Nossa equipe foi notificada.",
        details=error_details
    )
    
    try:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump()
        )
    except Exception as e:
        # Fallback se ainda houver problema de serialização
        logger.error(f"Erro ao serializar resposta de erro: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "Erro interno do servidor."
            }
        )


def register_exception_handlers(app):
    """
    Registra todos os handlers de exceção na aplicação FastAPI.
    
    Ordem importa: handlers mais específicos devem ser registrados primeiro,
    pois o FastAPI usa o primeiro handler que corresponde à exceção.
    
    Args:
        app: Instância da aplicação FastAPI
    """
    # Handlers específicos PRIMEIRO (ordem importa - mais específicos primeiro)
    # Exceções mais específicas herdam de mais genéricas, então registramos na ordem inversa
    app.add_exception_handler(OrcamentoStatusError, base_app_exception_handler)
    app.add_exception_handler(StockInsufficientError, base_app_exception_handler)
    app.add_exception_handler(PermissionDeniedError, base_app_exception_handler)
    app.add_exception_handler(NotFoundError, base_app_exception_handler)
    app.add_exception_handler(ValidationException, base_app_exception_handler)
    app.add_exception_handler(BusinessRuleException, base_app_exception_handler)
    app.add_exception_handler(BaseAppException, base_app_exception_handler)
    
    # Handlers de framework
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # Handler genérico POR ÚLTIMO (captura tudo que não foi tratado)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers registrados com sucesso")

