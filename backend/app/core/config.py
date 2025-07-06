
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # O Pydantic lerá estas variáveis de ambiente.
    # Se alguma não for encontrada (exceto as com valor padrão), a aplicação falhará ao iniciar.
    
    # Configurações da API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configurações do Banco de Dados
    DATABASE_URL: str

    # Configurações do Superusuário
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str
    
    # Esta linha faz com que ele leia de um arquivo .env se existir (para desenvolvimento local)
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Crie uma instância única das configurações que será usada em toda a aplicação
settings = Settings()