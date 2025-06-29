from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
from jose import JWTError, jwt # <<< MELHORIA: Import combinado
from datetime import timedelta

from app.schemas.usuario import Usuario, UsuarioCreate, Token, TokenData
from app.crud import usuario as crud_usuario
from app.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

router = APIRouter(
    tags=["Autenticação"]
)

# <<< MOVIDO PARA FORA da função e para o nível principal do módulo
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Endpoint de Login
@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud_usuario.get_user_by_email(email=form_data.username)
    if not user or not verify_password(form_data.password, user['senha_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['email']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint de Cadastro de Usuário
@router.post("/users/", response_model=Usuario, status_code=201)
def create_new_user(user: UsuarioCreate):
    db_user = crud_usuario.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    new_user_data = crud_usuario.create_user(user)
    # Esta conversão é necessária porque o CRUD retorna uma tupla do banco
    column_names = [desc[0] for desc in new_user_data.cursor.description]
    return Usuario.model_validate(dict(zip(column_names, new_user_data)))

# <<< MOVIDO PARA FORA da função e para o nível principal do módulo
def get_current_user(token: str = Depends(oauth2_scheme)) -> Usuario:
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
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user_dict = crud_usuario.get_user_by_email(email=token_data.email)
    if user_dict is None:
        raise credentials_exception
    
    if not user_dict.get('is_active'):
         raise HTTPException(status_code=400, detail="Usuário inativo")

    return Usuario.model_validate(user_dict)

# <<< MELHORIA: Endpoint de teste para verificar o usuário logado
@router.get("/users/me/", response_model=Usuario)
def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna os dados do usuário atualmente autenticado.
    Ótimo para testar se o token está funcionando.
    """
    return current_user