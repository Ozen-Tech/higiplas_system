import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.schemas.usuario import Usuario
from app.crud import usuario as crud_usuario
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.config import settings
from passlib.context import CryptContext


# --- CONFIGURAÇÃO DE CRIPTOGRAFIA ---

class Settings(BaseSettings):
    # O Pydantic automaticamente lê variáveis de ambiente com esses nomes.
    # Se uma delas não for encontrada, ele levantará um erro na inicialização.
    ALGORITHM = settings.ALGORITHM
    SECRET_KEY = settings.SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


    # Esta linha faz com que ele leia de um arquivo .env se existir (para desenvolvimento local)
    model_config = SettingsConfigDict(env_file=".env")

# Crie uma instância única das configurações que será usada em toda a aplicação
settings = Settings()
# --- FUNÇÕES DE SENHA E TOKEN ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- ESQUEMA DE AUTENTICAÇÃO ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

# --- FUNÇÃO DE SEGURANÇA CENTRALIZADA ---

def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud_usuario.get_user_by_email(db, email=email)
    
    if user is None:   
        raise credentials_exception

    return user


# Cria o contexto para hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verifica se a senha fornecida corresponde à senha com hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)