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
    
    # Verifica se o hash da senha é válido antes de tentar verificar
    if not user.hashed_password:
        return None
    
    try:
        if not verify_password(password, user.hashed_password):
            return None
    except Exception as e:
        # Log do erro mas não expõe detalhes
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao verificar senha do usuário {email}: {e}")
        return None
    
    return user

def update_user_profile(
    db: Session,
    user_id: int,
    user_update: schemas_usuario.UsuarioUpdate
) -> models.Usuario:
    """
    Atualiza os dados do perfil do usuário (nome, email, foto_perfil).
    """
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise ValueError("Usuário não encontrado")
    
    # Verificar se o email já está em uso por outro usuário
    if user_update.email and user_update.email != user.email:
        existing_user = get_user_by_email(db, email=user_update.email)
        if existing_user and existing_user.id != user_id:
            raise ValueError("E-mail já está em uso por outro usuário")
    
    # Atualizar campos fornecidos
    if user_update.nome is not None:
        user.nome = user_update.nome
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.foto_perfil is not None:
        user.foto_perfil = user_update.foto_perfil
    
    db.commit()
    db.refresh(user)
    return user

def update_user_password(
    db: Session,
    user_id: int,
    senha_atual: str,
    nova_senha: str
) -> models.Usuario:
    """
    Atualiza a senha do usuário após validar a senha atual.
    """
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise ValueError("Usuário não encontrado")
    
    # Verificar senha atual
    if not verify_password(senha_atual, user.hashed_password):
        raise ValueError("Senha atual incorreta")
    
    # Atualizar senha
    user.hashed_password = get_password_hash(nova_senha)
    db.commit()
    db.refresh(user)
    return user