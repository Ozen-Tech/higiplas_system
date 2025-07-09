from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str

    GOOGLE_API_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 dias

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()