import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from psycopg2.extensions import connection
from app.db.connection import get_db
from app.schemas.usuario import Usuario
from app.crud import usuario as crud_usuario
from app.core import verify_password

# --- CONFIGURAÇÃO DE CRIPTOGRAFIA ---

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
    conn: connection = Depends(get_db), 
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
    
    user_data = crud_usuario.get_user_by_email(conn, email=email)
    user = crud_usuario.get_user_by_email(conn, email=email)
    
    if user_data is None:   
            raise credentials_exception
        

    return user