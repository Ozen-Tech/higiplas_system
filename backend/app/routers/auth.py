# /backend/app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

# Importações necessárias e limpas
from app.db.connection import get_db
from app.db import models
from app.schemas import usuario as schemas_usuario
from app.crud import usuario as crud_usuario
from app.dependencies import create_access_token, get_current_user
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