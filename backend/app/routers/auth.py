# backend/app/routers/auth.py

from typing import Annotated
from sqlalchemy.orm import Session # <<< MUDANÇA AQUI

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas import usuario as schemas_usuario
from app.crud import usuario as crud_usuario
from app.db.connection import get_db
from .. import schemas, crud
from app.db import models # <<< MUDANÇA AQUI
from app.security import create_access_token, get_current_user
from app.core import verify_password

router = APIRouter(
    tags=["Autenticação e Usuários"]
)

@router.post("/token", response_model=schemas_usuario.Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db) # <<< MUDANÇA AQUI: de 'conn' para 'db'
):
    # A função CRUD agora retorna um objeto, não um dicionário
    user = crud_usuario.get_user_by_email(db=db, email=form_data.username)
    
    # Acessamos os atributos diretamente (user.hashed_password)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Usamos o atributo user.email
    access_token = create_access_token(
        data={"sub": user.email}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/", response_model=schemas_usuario.Usuario)
def create_new_user(user: schemas_usuario.UsuarioCreate, db: Session = Depends(get_db)):
    db_user = crud_usuario.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já registrado."
        )
    return crud_usuario.create_user(db=db, user=user)

@router.get("/users/me/", response_model=schemas_usuario.Usuario)
def read_users_me(current_user: models.Usuario = Depends(get_current_user)):
    return current_user