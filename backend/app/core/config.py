import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str

    # Database fields
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    GOOGLE_API_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutos para access token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 dias para refresh token

    # API URL
    NEXT_PUBLIC_API_URL: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()