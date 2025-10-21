from datetime import datetime, timedelta, timezone
import secrets
import logging
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

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

def create_access_token(data: dict) -> str:
    """Cria um novo token de acesso JWT."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(db: Session, usuario_id: int) -> str:
    """Cria um novo refresh token e salva no banco de dados."""
    # Gera um token aleatório seguro
    token = secrets.token_urlsafe(32)

    # Define a data de expiração
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    # Cria o registro no banco de dados
    db_refresh_token = models.RefreshToken(
        token=token,
        usuario_id=usuario_id,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    db.commit()
    db.refresh(db_refresh_token)

    return token

def verify_refresh_token(db: Session, token: str) -> models.Usuario | None:
    """Verifica se o refresh token é válido e retorna o usuário associado."""
    # Busca o token no banco de dados
    db_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == token,
        models.RefreshToken.revoked == False
    ).first()

    if not db_token:
        logger.warning(f"Refresh token não encontrado ou revogado")
        return None

    # Verifica se o token expirou
    if db_token.expires_at < datetime.now(timezone.utc):
        logger.warning(f"Refresh token expirado")
        # Marca o token como revogado
        db_token.revoked = True
        db.commit()
        return None

    # Busca o usuário associado
    usuario = db.query(models.Usuario).filter(models.Usuario.id == db_token.usuario_id).first()

    if not usuario:
        logger.error(f"Usuário não encontrado para refresh token")
        return None

    return usuario

def revoke_refresh_token(db: Session, token: str) -> bool:
    """Revoga um refresh token."""
    db_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == token
    ).first()

    if db_token:
        db_token.revoked = True
        db.commit()
        return True

    return False

def revoke_all_user_tokens(db: Session, usuario_id: int) -> int:
    """Revoga todos os refresh tokens de um usuário."""
    count = db.query(models.RefreshToken).filter(
        models.RefreshToken.usuario_id == usuario_id,
        models.RefreshToken.revoked == False
    ).update({"revoked": True})
    db.commit()
    return count

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Usuario:
    """
    Decodifica o token JWT e retorna o usuário do banco de dados correspondente.
    Esta é a dependência principal para proteger rotas.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expirado ou inválido. Por favor, faça login novamente.",
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
