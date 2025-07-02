# backend/app/prestart.py

import logging
import time
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.models import Base
from app.db.connection import engine, SessionLocal
from app.crud import empresa as crud_empresa
from app.schemas.empresa import EmpresaCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5
wait_seconds = 1

def create_initial_data(db: Session):
    logger.info("Verificando dados iniciais...")
    empresa = crud_empresa.get_empresa(db, empresa_id=1)
    if not empresa:
        logger.info("Empresa principal não encontrada. Criando 'HIGIPLAS'...")
        empresa_in = EmpresaCreate(nome="HIGIPLAS")
        crud_empresa.create_empresa(db, empresa=empresa_in)
        logger.info("Empresa 'HIGIPLAS' criada com sucesso.")
    else:
        logger.info("Empresa principal já existe.")

def init():
    db = SessionLocal()
    try:
        logger.info("Aguardando o banco de dados ficar disponível...")
        tries = 0
        while tries < max_tries:
            try:
                db.execute(text("SELECT 1"))
                logger.info("Conexão com o banco de dados bem-sucedida!")
                
                logger.info("Criando tabelas (se não existirem)...")
                Base.metadata.create_all(bind=engine)
                logger.info("Tabelas verificadas/criadas com sucesso!")
                
                create_initial_data(db)
                
                return
            except (OperationalError, ConnectionRefusedError):
                tries += 1
                logger.info(f"Banco de dados indisponível. Tentativa {tries}/{max_tries}. Tentando novamente em {wait_seconds}s...")
                time.sleep(wait_seconds)
        
        raise Exception("FALHA: Não foi possível conectar ao banco de dados.")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Iniciando script de pré-inicialização da API...")
    init()
    logger.info("Script de pré-inicialização concluído. Iniciando a aplicação principal.")