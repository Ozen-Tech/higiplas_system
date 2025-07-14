# /backend/app/prestart.py

import logging
import time
import json
import os
import traceback
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect

from app.db.connection import engine, SessionLocal
from app.db.models import Base, VendaHistorica, Empresa

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_db_connection(db: Session, max_retries=15, wait=2):
    """Tenta conectar ao banco de dados com múltiplas tentativas."""
    logger.info("Verificando conexão com o banco de dados...")
    for i in range(max_retries):
        try:
            db.execute(text("SELECT 1"))
            logger.info("✅ Conexão com o banco de dados bem-sucedida!")
            return True
        except Exception as e:
            logger.warning(f"Tentativa {i+1}/{max_retries} falhou. Banco de dados indisponível: {e}")
            time.sleep(wait)
    logger.error("❌ FALHA CRÍTICA: Não foi possível conectar ao banco de dados.")
    return False

def ensure_tables_exist():
    """Garante que todas as tabelas definidas em Base.metadata existam."""
    logger.info("Verificando e criando tabelas, se necessário...")
    try:
        # Inspeciona o banco para ver se a tabela já existe antes de tentar criar
        inspector = inspect(engine)
        if not inspector.has_table(VendaHistorica.__tablename__):
             logger.info(f"Tabela '{VendaHistorica.__tablename__}' não encontrada. Criando todas as tabelas...")
             Base.metadata.create_all(bind=engine)
             logger.info("✅ Todas as tabelas foram criadas/verificadas com sucesso.")
        else:
             logger.info(f"✅ Tabela '{VendaHistorica.__tablename__}' já existe.")
             # Você ainda pode rodar o create_all para garantir outras tabelas
             Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"❌ Erro ao criar as tabelas: {e}")
        traceback.print_exc()
        raise

def seed_data_if_empty(db: Session):
    """Popula a tabela de vendas históricas apenas se ela estiver completamente vazia."""
    logger.info("Iniciando verificação de dados históricos...")
    try:
        count = db.query(VendaHistorica).count()
        if count > 0:
            logger.info(f"Tabela 'vendas_historicas' já possui {count} registros. Seeding não é necessário.")
            return

        logger.info("Tabela 'vendas_historicas' está vazia. Procurando pelo arquivo de dados...")
        
        # O caminho é relativo ao WORKDIR, que é /code no Dockerfile.
        json_path = "app/dados_historicos_vendas.json" 
        
        if not os.path.exists(json_path):
             logger.error(f"❌ ARQUIVO NÃO ENCONTRADO em '{json_path}'. O seeding não pode continuar. Faça o commit do arquivo JSON.")
             return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"Arquivo JSON encontrado com {len(data)} registros. Iniciando inserção no banco...")

        for item in data:
            db_item = VendaHistorica(
                ident_antigo=item['ident_antigo'],
                descricao=item['descricao'],
                quantidade_vendida_total=item['quantidade_vendida_total'],
                custo_compra_total=item.get('custo_compra_total', 0), # Usar .get com valor padrão
                valor_vendido_total=item.get('valor_vendido_total', 0),
                lucro_bruto_total=item.get('lucro_bruto_total', 0),
                margem_lucro_percentual=item.get('margem_lucro_percentual', 0)
            )
            db.add(db_item)
        
        db.commit()
        logger.info(f"✅ Seeding concluído! {len(data)} registros inseridos com sucesso em 'vendas_historicas'.")

    except Exception as e:
        logger.error(f"❌ Erro durante o processo de seeding: {e}")
        traceback.print_exc()
        db.rollback()


def main():
    logger.info("🚀 Iniciando processo de pré-inicialização...")
    db_session = SessionLocal()
    try:
        if check_db_connection(db_session):
            ensure_tables_exist()
            seed_data_if_empty(db_session)
    finally:
        db_session.close()
    logger.info("🏁 Processo de pré-inicialização finalizado.")

if __name__ == "__main__":
    main()