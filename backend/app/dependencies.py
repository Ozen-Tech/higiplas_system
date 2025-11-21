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
    import logging
    logger = logging.getLogger(__name__)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.info(f"Tentando decodificar token: {token[:20]}...")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str | None = payload.get("sub")
        logger.info(f"Token decodificado com sucesso. Email: {email}")
        if email is None:
            logger.error("Email não encontrado no payload do token")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"Erro ao decodificar token JWT: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Erro inesperado ao validar token: {str(e)}")
        raise credentials_exception
    
    user = crud_usuario.get_user_by_email(db, email=email)
    if user is None:
        logger.error(f"Usuário não encontrado no banco de dados: {email}")
        raise credentials_exception
    
    logger.info(f"Usuário autenticado com sucesso: {user.email}")
    return user


def get_current_vendedor(
    current_user: models.Usuario = Depends(get_current_user)
) -> models.Usuario:
    """
    Valida se o usuário autenticado tem perfil de vendedor.
    Retorna HTTP 403 se o usuário não for vendedor.
    """
    # Verifica se o perfil contém "vendedor" (case-insensitive)
    perfil_lower = current_user.perfil.lower() if current_user.perfil else ""
    if "vendedor" not in perfil_lower:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas vendedores podem acessar este recurso.",
        )
    return current_user


def get_admin_user(
    current_user: models.Usuario = Depends(get_current_user)
) -> models.Usuario:
    """
    Valida se o usuário autenticado tem perfil de administrador ou gestor.
    """
    perfil = (current_user.perfil or "").upper()
    if perfil not in ["ADMIN", "GESTOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores ou gestores podem acessar este recurso."
        )
    return current_user


def get_current_operador(
    current_user: models.Usuario = Depends(get_current_user)
) -> models.Usuario:
    """
    Valida se o usuário autenticado tem perfil de operador (entregador).
    Retorna HTTP 403 se o usuário não for operador.
    """
    perfil = (current_user.perfil or "").upper()
    if perfil != "OPERADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas operadores (entregadores) podem acessar este recurso.",
        )
    return current_user
