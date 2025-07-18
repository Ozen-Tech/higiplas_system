# /backend/app/prestart.py

import logging
import time
import json
import os
import traceback
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect

# Importações limpas dos módulos do seu projeto
from app.db.connection import engine, SessionLocal
from app.db.models import Base, VendaHistorica, Empresa # Certifique-se de importar tudo que precisa

# Configuração do logging
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
        # A forma mais simples e idempotente de garantir que todas as tabelas existem
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Todas as tabelas foram criadas/verificadas com sucesso.")
    except Exception as e:
        logger.error(f"❌ Erro ao criar as tabelas: {e}")
        traceback.print_exc()
        raise


def seed_historical_data(db: Session):
    """
    Popula a tabela 'vendas_historicas' com dados de um arquivo JSON,
    mas somente se a tabela estiver completamente vazia.
    """
    logger.info("Iniciando verificação de dados de vendas históricas ('seeding')...")
    
    # 1. Checa se a tabela já tem algum dado. Se tiver, sai da função.
    if db.query(VendaHistorica).count() > 0:
        logger.info("--> Tabela 'vendas_historicas' já populada. Nenhuma ação necessária.")
        return

    # 2. Se a tabela está vazia, tenta encontrar e ler o arquivo JSON.
    logger.info("--> Tabela 'vendas_historicas' vazia. Procurando pelo arquivo de dados...")
    
    # O WORKDIR do Docker é /code. Se seus scripts estão em /code/app, o caminho
    # a partir de lá deve ser '../dados_historicos_vendas.json',
    # ou podemos colocar o json dentro da pasta app.
    # Coloque seu `dados_historicos_vendas.json` dentro da pasta `backend/app/`
    json_path = "app/dados_historicos_vendas.json" 

    if not os.path.exists(json_path):
        logger.error(f"❌ ARQUIVO NÃO ENCONTRADO em '{json_path}'. Mova o 'dados_historicos_vendas.json' para a pasta 'backend/app/'.")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"Arquivo JSON encontrado com {len(data)} registros. Iniciando inserção no banco...")
        
        # 3. Itera e insere, evitando duplicatas do PRÓPRIO arquivo.
        ids_no_json = set()
        novos_registros = []
        for item in data:
            ident_antigo = item.get("ident_antigo")
            if ident_antigo and ident_antigo not in ids_no_json:
                db_item = VendaHistorica(
                    ident_antigo=ident_antigo,
                    descricao=item.get('descricao'),
                    quantidade_vendida_total=item.get('quantidade_vendida_total', 0),
                    custo_compra_total=item.get('custo_compra_total', 0),
                    valor_vendido_total=item.get('valor_vendido_total', 0),
                    lucro_bruto_total=item.get('lucro_bruto_total', 0),
                    margem_lucro_percentual=item.get('margem_lucro_percentual', 0)
                )
                novos_registros.append(db_item)
                ids_no_json.add(ident_antigo)
        
        # 4. Insere todos os novos registros de uma vez só (bulk insert)
        db.bulk_save_objects(novos_registros)
        db.commit()
        logger.info(f"✅ Seeding concluído! {len(novos_registros)} registros inseridos com sucesso em 'vendas_historicas'.")

    except Exception as e:
        logger.error(f"❌ Erro durante o processo de seeding: {e}")
        traceback.print_exc()
        db.rollback()


def seed_initial_company(db: Session):
    """Popula a tabela de empresas com um registro padrão se ela estiver vazia."""
    logger.info("Verificando se a empresa padrão existe...")
    if db.query(Empresa).count() == 0:
        logger.info("--> Nenhuma empresa encontrada. Criando empresa 'Higiplas Padrão'...")
        empresa_padrao = Empresa(nome="Higiplas Padrão", cnpj="00.000.000/0001-00")
        db.add(empresa_padrao)
        db.commit()
        logger.info("--> Empresa padrão criada com sucesso.")
    else:
        logger.info("--> Empresa já existe. Nenhuma ação necessária.")


def main():
    logger.info("🚀 Iniciando processo de pré-inicialização...")
    db_session = SessionLocal()
    try:
        if check_db_connection(db_session):
            ensure_tables_exist()

            
            seed_initial_company(db_session) # Deixe a da empresa se quiser
            
    finally:
        db_session.close()
    logger.info("🏁 Processo de pré-inicialização finalizado.")

if __name__ == "__main__":
    main()