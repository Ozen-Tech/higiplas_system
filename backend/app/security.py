# /backend/app/security.py

from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- GERENCIADOR DE CONFIGURAÇÕES (LÊ .env e Variáveis de Ambiente) ---
class Settings(BaseSettings):
    # Variáveis de ambiente que o Pydantic vai buscar.
    # Se alguma não for encontrada, a aplicação falhará ao iniciar (o que é bom!).
    DATABASE_URL: str
    SECRET_KEY: str
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str
    
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 dias

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Instância única das configurações para ser usada em toda a aplicação.
settings = Settings()


# --- LÓGICA DE CRIPTOGRAFIA DE SENHA ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde à senha com hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)


# --- LÓGICA DE CRIAÇÃO DE TOKEN JWT ---
def create_access_token(data: dict) -> str:
    """Cria um novo token de acesso JWT."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.db import models
from app.security import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud_usuario.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt