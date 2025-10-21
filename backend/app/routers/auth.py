# /backend/app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..db import models

# Importações necessárias e limpas
from app.db.connection import get_db
from app.db import models
from ..schemas import usuario as schemas_usuario
from ..crud import usuario as crud_usuario
from app.dependencies import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
    revoke_all_user_tokens,
    get_current_user
)

router = APIRouter(
    tags=["Autenticação e Usuários"]
)

# O esquema de autenticação é definido no router que o utiliza.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


@router.post("/token", response_model=schemas_usuario.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # A lógica de autenticação agora é uma única chamada de função limpa.
    user = crud_usuario.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Cria access token e refresh token
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(db=db, usuario_id=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=schemas_usuario.Token)
def refresh_access_token(
    refresh_request: schemas_usuario.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para renovar o access token usando um refresh token válido.
    """
    # Verifica o refresh token
    user = verify_refresh_token(db, refresh_request.refresh_token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Revoga o refresh token antigo (rotação de tokens)
    revoke_refresh_token(db, refresh_request.refresh_token)

    # Cria novos tokens
    access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(db=db, usuario_id=user.id)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(
    refresh_request: schemas_usuario.RefreshTokenRequest,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para fazer logout e revogar o refresh token.
    """
    revoke_refresh_token(db, refresh_request.refresh_token)
    return {"message": "Logout realizado com sucesso"}


@router.post("/logout-all")
def logout_all_devices(
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para fazer logout de todos os dispositivos (revoga todos os refresh tokens do usuário).
    """
    count = revoke_all_user_tokens(db, current_user.id)
    return {"message": f"Logout realizado em {count} dispositivo(s)"}


# A rota para criar usuário não precisa estar aqui, pode ir para um router de "empresas"
# ou de administração, mas vamos manter por enquanto.
@router.post("/", response_model=schemas_usuario.Usuario, status_code=status.HTTP_201_CREATED)
def create_new_user(user: schemas_usuario.UsuarioCreate, db: Session = Depends(get_db)):
    db_user = crud_usuario.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já registrado."
        )
    # Supondo que a empresa_id seja passada no corpo ou obtida de outra forma.
    # Se a empresa_id vier do usuário logado, essa rota precisaria de autenticação.
    return crud_usuario.create_user(db=db, user_in=user, empresa_id=1) # Usando 1 como placeholder


@router.get("/me", response_model=schemas_usuario.Usuario)
def read_users_me(current_user: models.Usuario = Depends(get_current_user)):
    """Retorna os dados do usuário atualmente logado."""
    return current_user