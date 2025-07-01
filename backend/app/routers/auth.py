from typing import Annotated
from psycopg2.extensions import connection

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# --- Imports Corretos ---
# Importe os schemas específicos que você precisa, não o pacote inteiro
from app.schemas.usuario import Usuario, UsuarioCreate, Token, TokenData

# Importe as funções do CRUD
from app.crud import usuario as crud_usuario

# Importe as dependências e funções de segurança/core
from app.db.connection import get_db
from app.core import verify_password
from app.security import create_access_token, get_current_user


router = APIRouter(
    tags=["Autenticação e Usuários"] # Tag unificada para os endpoints
)

# --- Endpoint de Login ---
@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    conn: connection = Depends(get_db)
):
    """
    Autentica o usuário e retorna um token de acesso.
    """
    user = crud_usuario.get_user_by_email(conn=conn, email=form_data.username)
    
    if not user or not verify_password(form_data.password, user.get('hashed_password')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.get('email')}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# --- Endpoint de Cadastro de Usuário ---
@router.post("/users/", response_model=Usuario, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UsuarioCreate, conn: connection = Depends(get_db)):
    """
    Cria um novo usuário.
    """
    db_user = crud_usuario.get_user_by_email(conn=conn, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já registrado."
        )
    
    return crud_usuario.create_user(conn=conn, user=user)


# --- Endpoint de Teste de Autenticação ---
@router.get("/users/me/", response_model=Usuario)
def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna os dados do usuário atualmente autenticado.
    Ótimo para testar se o token está funcionando.
    """
    return current_user