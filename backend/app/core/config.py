"""
Configurações centralizadas do sistema.

Gerencia variáveis de ambiente, configurações de aplicação,
logging, timeouts e limites do sistema.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""
    
    # Database
    DATABASE_URL: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dias
    
    # Superuser
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str
    
    # External APIs (opcional - IA removida do sistema)
    GOOGLE_API_KEY: Optional[str] = None
    
    # Frontend
    NEXT_PUBLIC_API_URL: str
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".xlsx", ".xls"]
    
    # Timeouts
    REQUEST_TIMEOUT: int = 300  # 5 minutos
    DB_QUERY_TIMEOUT: int = 30  # 30 segundos
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000
    
    # Rate Limiting (futuro)
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # segundos

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


settings = Settings()