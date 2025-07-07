# /backend/app/crud/usuario.py

from sqlalchemy.orm import Session
from app.db import models
from app.schemas import usuario as schemas_usuario

# Importa as funções de segurança necessárias do local correto.
from app.core.hashing import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> models.Usuario | None:
    """Busca um usuário pelo e-mail."""
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def create_user(db: Session, user_in: schemas_usuario.UsuarioCreate, empresa_id: int) -> models.Usuario:
    """Cria um novo usuário no banco de dados."""
    hashed_password = get_password_hash(user_in.password)
    
    db_user = models.Usuario(
        email=user_in.email,
        hashed_password=hashed_password,
        nome=user_in.nome,
        empresa_id=empresa_id,
        perfil=user_in.perfil
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> models.Usuario | None:
    """
    Autentica um usuário. Retorna o objeto do usuário se as credenciais forem válidas,
    caso contrário, retorna None.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user