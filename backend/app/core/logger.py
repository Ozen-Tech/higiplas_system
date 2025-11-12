"""
Sistema de logging centralizado para o Higiplas.

Fornece loggers específicos por módulo com contexto (request_id, user_id),
formatação estruturada e rotação de arquivos.
"""

import logging
import os
import uuid
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional
from contextvars import ContextVar

from .config import settings

# Contexto para request_id e user_id
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[int]] = ContextVar('user_id', default=None)

logs_dir = "logs"
os.makedirs(logs_dir, exist_ok=True)


class ContextualFormatter(logging.Formatter):
    """Formatter que inclui contexto (request_id, user_id) nos logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Adiciona contexto aos logs."""
        # Adicionar request_id se disponível
        request_id = request_id_var.get()
        if request_id:
            record.request_id = request_id
        else:
            record.request_id = "N/A"
        
        # Adicionar user_id se disponível
        user_id = user_id_var.get()
        if user_id:
            record.user_id = user_id
        else:
            record.user_id = "N/A"
        
        return super().format(record)


def setup_logger(
    name: str,
    log_file: str,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Configura um logger com formatação contextual e rotação de arquivos.
    
    Args:
        name: Nome do logger
        log_file: Nome do arquivo de log
        level: Nível de log (padrão: INFO)
        
    Returns:
        Logger configurado
    """
    # Formatter com contexto
    formatter = ContextualFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - [request_id:%(request_id)s] [user_id:%(user_id)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File handler com rotação
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, log_file),
        maxBytes=settings.LOG_FILE_MAX_BYTES,
        backupCount=settings.LOG_FILE_BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Criar logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicação de handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    # Evitar propagação para root logger
    logger.propagate = False
    
    return logger


def get_request_id() -> str:
    """Gera ou retorna o request_id atual."""
    request_id = request_id_var.get()
    if not request_id:
        request_id = str(uuid.uuid4())[:8]
        request_id_var.set(request_id)
    return request_id


def set_request_context(request_id: Optional[str] = None, user_id: Optional[int] = None):
    """
    Define o contexto da requisição atual.
    
    Args:
        request_id: ID da requisição (gera novo se None)
        user_id: ID do usuário
    """
    if request_id:
        request_id_var.set(request_id)
    else:
        request_id_var.set(get_request_id())
    
    if user_id:
        user_id_var.set(user_id)


# Loggers específicos por módulo
stock_automation_logger = setup_logger("stock_automation", "stock_automation.log")
stock_operations_logger = setup_logger("stock_operations", "stock_operations.log")
sales_logger = setup_logger("sales", "sales.log")
orcamento_logger = setup_logger("orcamento", "orcamento.log")
auth_logger = setup_logger("auth", "auth.log")
api_logger = setup_logger("api", "api.log")

# Logger principal da aplicação
app_logger = setup_logger("higiplas", "app.log")
