# backend/app/crud/usuario.py

from sqlalchemy.orm import Session
from app.db import models
from app.schemas import usuario as schemas
from app.core import get_password_hash

def get_user_by_email(db: Session, email: str):
    """
    Busca um usuário pelo e-mail usando o ORM do SQLAlchemy.
    """
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def create_user(db: Session, user: schemas.UsuarioCreate):
    """
    Cria um novo usuário no banco de dados usando o ORM do SQLAlchemy.
    """
    hashed_password = get_password_hash(user.password)
    
    # Cria uma instância do modelo SQLAlchemy com os dados do schema
    db_user = models.Usuario(
        email=user.email,
        hashed_password=hashed_password,
        nome=user.nome,
        empresa_id=user.empresa_id,
        perfil=user.perfil
    )
    
    # Adiciona a nova instância à sessão
    db.add(db_user)
    # Comita a transação para salvar no banco
    db.commit()
    # Atualiza a instância com os dados do banco (como o ID gerado)
    db.refresh(db_user)
    
    return db_user