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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 dias
    
    # API URL
    NEXT_PUBLIC_API_URL: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # For local development, replace higiplas_postgres with localhost
        # Only do this if we're not in production (Render sets DATABASE_URL with production values)
        if (self.DATABASE_URL and "higiplas_postgres" in self.DATABASE_URL and 
            not self.DATABASE_URL.startswith("postgresql://higiplas_postgres_prod_user")):
            self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@localhost:5432/{self.DB_NAME}"

settings = Settings()