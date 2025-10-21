# backend/migrate_propostas.py
"""
Script para criar as tabelas de Proposta e PropostaItem no banco de dados.
Execute este script após adicionar os novos models.
"""

from app.db.connection import engine, Base
from app.db.models import Proposta, PropostaItem
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """Cria as novas tabelas no banco de dados"""
    try:
        logger.info("Iniciando migração das tabelas de Proposta...")
        
        # Cria apenas as tabelas que ainda não existem
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Migração concluída com sucesso!")
        logger.info("Tabelas criadas: propostas, proposta_itens")
        
    except Exception as e:
        logger.error(f"❌ Erro durante a migração: {e}")
        raise

if __name__ == "__main__":
    migrate()
