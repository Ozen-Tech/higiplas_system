# /backend/app/create_superuser.py

import logging
from sqlalchemy.orm import Session

# Importações dos seus próprios módulos
from app.db.connection import SessionLocal
from app.db import models
from app.core.config import settings
from app.core.hashing import get_password_hash
from app.schemas.usuario import PerfilUsuario 

# Configurando um logger para ver as saídas no Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_initial_superuser():

    SUPERUSER_EMAIL = settings.SUPERUSER_EMAIL 
    SUPERUSER_PASSWORD = settings.SUPERUSER_PASSWORD 

    """
    Cria o superusuário inicial a partir das variáveis de ambiente,
    se ele ainda não existir.
    """
    logger.info("Iniciando verificação de superusuário...")

    # O Pydantic já garante que essas variáveis existem, mas é uma boa prática verificar.
    if not settings.SUPERUSER_EMAIL or not settings.SUPERUSER_PASSWORD:
        logger.warning("Variáveis de ambiente do superusuário não definidas. Pulando criação.")
        return

    # Cria uma sessão com o banco de dados que será fechada no final
    db: Session = SessionLocal()
    
    try:
        # 1. Verifica se o superusuário já existe
        user = db.query(models.Usuario).filter(models.Usuario.email == settings.SUPERUSER_EMAIL).first()
        
        if user:
            logger.info(f"Superusuário com o e-mail '{settings.SUPERUSER_EMAIL}' já existe no banco de dados. Nenhuma ação necessária.")
            return

        logger.info(f"Superusuário não encontrado. Iniciando processo de criação para '{settings.SUPERUSER_EMAIL}'.")

        # 2. Garante que a "Empresa Padrão" existe ou a cria
        default_company_name = "Empresa Padrão Higiplas"
        empresa = db.query(models.Empresa).filter(models.Empresa.nome == default_company_name).first()
        if not empresa:
            logger.info(f"Criando '{default_company_name}' para o superusuário.")
            empresa = models.Empresa(nome=default_company_name)
            db.add(empresa)
            db.commit()
            db.refresh(empresa)
            logger.info(f"Empresa '{default_company_name}' criada com ID: {empresa.id}.")
        
        # 3. Cria o objeto do superusuário
        hashed_password = get_password_hash(settings.SUPERUSER_PASSWORD)
        
        superuser = models.Usuario(
            nome="Admin Higiplas",
            email=settings.SUPERUSER_EMAIL,
            hashed_password=hashed_password,
            perfil=PerfilUsuario.ADMIN, # Garante que você tenha essa enumeração
            is_active=True,
            empresa_id=empresa.id
        )
        
        db.add(superuser)
        db.commit()
        
        logger.info("Superusuário criado com sucesso!")

    except Exception as e:
        logger.error(f"Ocorreu um erro ao tentar criar o superusuário: {e}")
        db.rollback() # Desfaz qualquer mudança parcial em caso de erro

    finally:
        db.close()
        logger.info("Sessão do banco de dados para criação de superusuário fechada.")