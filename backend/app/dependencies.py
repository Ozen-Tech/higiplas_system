from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

# Importa dos novos módulos de core
from app.core.config import settings

# Importa dos outros módulos da aplicação
from app.db import models
from app.db.connection import get_db
from app.crud import usuario as crud_usuario


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

def create_access_token(data: dict) -> str:
    """Cria um novo token de acesso JWT."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Usuario:
    """
    Decodifica o token JWT e retorna o usuário do banco de dados correspondente.
    Esta é a dependência principal para proteger rotas.
    """
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