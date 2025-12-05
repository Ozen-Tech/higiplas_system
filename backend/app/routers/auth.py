# /backend/app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from ..db import models

# Importações necessárias e limpas
from app.db.connection import get_db
from app.db import models
from ..schemas import usuario as schemas_usuario
from ..crud import usuario as crud_usuario
from app.dependencies import create_access_token, get_current_user, get_admin_user
from app.core.config import settings

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
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


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

@router.put("/me", response_model=schemas_usuario.Usuario, summary="Atualizar perfil do usuário")
def update_user_profile(
    user_update: schemas_usuario.UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Atualiza os dados do perfil do usuário (nome, email, foto_perfil).
    """
    try:
        updated_user = crud_usuario.update_user_profile(
            db=db,
            user_id=current_user.id,
            user_update=user_update
        )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/me/password", response_model=schemas_usuario.Usuario, summary="Alterar senha do usuário")
def update_user_password(
    password_update: schemas_usuario.UsuarioUpdateSenha,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Altera a senha do usuário após validar a senha atual.
    """
    try:
        updated_user = crud_usuario.update_user_password(
            db=db,
            user_id=current_user.id,
            senha_atual=password_update.senha_atual,
            nova_senha=password_update.nova_senha
        )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/admin/create", response_model=schemas_usuario.Usuario, status_code=status.HTTP_201_CREATED)
def create_user_admin(
    user: schemas_usuario.UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_admin_user)
):
    """
    Cria um novo usuário no sistema.
    Apenas o administrador (enzo.alverde@gmail.com) pode acessar esta rota.
    """
    # Verifica se o email já existe
    db_user = crud_usuario.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já registrado."
        )
    
    # Cria o usuário
    return crud_usuario.create_user(db=db, user_in=user, empresa_id=user.empresa_id)