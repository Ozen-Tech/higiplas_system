# /backend/app/prestart.py

import logging
import time
import json
import os
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy import text
import traceback # Para logs de erro detalhados

# Importações dos seus módulos da aplicação
from app.db.connection import engine, SessionLocal
from app.db.models import Base, VendaHistorica, Empresa # Importe os modelos que você vai usar
from app.crud import empresa as crud_empresa
from app.schemas.empresa import EmpresaCreate

# --- Configuração do Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Constantes de Configuração ---
MAX_DB_RETRIES = 60 # Total de tentativas para conectar ao banco (ex: 60 segundos)
WAIT_SECONDS = 1
HISTORICAL_DATA_FILE = "dados_historicos_vendas.json"

# --- Funções de Inicialização de Dados ---

def create_initial_company(db: Session):
    """
    Cria a empresa principal ('HIGIPLAS') se ela não existir.
    Isso garante que os usuários tenham uma empresa para se associar.
    """
    logger.info("Verificando se a empresa principal existe...")
    # Assume-se que a empresa principal sempre terá o ID 1
    main_company = db.query(Empresa).filter_by(id=1).first()
    if not main_company:
        logger.warning("Empresa principal não encontrada. Criando 'HIGIPLAS' com ID 1...")
        empresa_in = EmpresaCreate(nome="HIGIPLAS")
        crud_empresa.create_empresa(db, empresa=empresa_in)
        logger.info("✅ Empresa 'HIGIPLAS' criada com sucesso.")
    else:
        logger.info("Empresa principal já existe. Nenhuma ação necessária.")


def seed_historical_data(db: Session):
    """
    Lê o arquivo JSON com dados históricos de vendas e popula a tabela 
    'vendas_historicas' caso ela esteja vazia, para evitar duplicação.
    """
    logger.info("Verificando dados históricos de vendas...")
    
    # Esta verificação é crucial para não reinserir os dados a cada deploy
    if db.query(VendaHistorica).first():
        logger.info("Tabela 'vendas_historicas' já contém dados. Pulando seeding.")
        return

    logger.info("Tabela 'vendas_historicas' está vazia. Iniciando processo de seeding...")
    
    try:
        # O Dockerfile define o WORKDIR como /code, então o caminho relativo é app/
        file_path = os.path.join("app", HISTORICAL_DATA_FILE) 
        with open(file_path, 'r', encoding='utf-8') as f:
            historical_data = json.load(f)

        if not historical_data:
            logger.warning("Arquivo de dados históricos está vazio.")
            return

        for item in historical_data:
            # Constrói o objeto do modelo a partir dos dados do JSON
            db_item = VendaHistorica(
                ident_antigo=item.get('ident_antigo'),
                descricao=item.get('descricao'),
                quantidade_vendida_total=item.get('quantidade_vendida_total'),
                custo_compra_total=item.get('custo_compra_total'),
                valor_vendido_total=item.get('valor_vendido_total'),
                lucro_bruto_total=item.get('lucro_bruto_total'),
                margem_lucro_percentual=item.get('margem_lucro_percentual')
            )
            db.add(db_item)
        
        db.commit()
        logger.info(f"✅ Seeding de {len(historical_data)} registros históricos concluído!")

    except FileNotFoundError:
        logger.error(f"❌ ERRO CRÍTICO DE SEEDING: O arquivo '{file_path}' não foi encontrado! Certifique-se de que 'dados_historicos_vendas.json' está na pasta 'app/' e foi commitado.")
    except Exception as e:
        logger.error("❌ Ocorreu um erro inesperado durante o seeding de dados históricos:")
        logger.error(traceback.format_exc())
        db.rollback()

# --- Função Principal de Inicialização ---

def init_db():
    db_session: Session | None = None
    try:
        logger.info("Iniciando a verificação do banco de dados...")
        
        # Tentativas de conexão com o banco
        for i in range(MAX_DB_RETRIES):
            try:
                db_session = SessionLocal()
                # Testa a conexão com uma query simples
                db_session.execute(text("SELECT 1"))
                logger.info("✅ Conexão com o banco de dados estabelecida com sucesso!")
                
                # ---- Se a conexão funcionou, executa as tarefas ----
                logger.info("Iniciando criação de tabelas (se necessário)...")
                Base.metadata.create_all(bind=engine)
                logger.info("✅ Tabelas verificadas/criadas.")
                
                # 1. Garante que a empresa principal existe
                create_initial_company(db_session)
                
                # 2. Popula com os dados históricos se necessário
                seed_historical_data(db_session)
                
                # Se tudo deu certo, sai do loop
                return
            
            except OperationalError:
                logger.warning(f"Banco de dados indisponível. Tentativa {i + 1}/{MAX_DB_RETRIES}. Tentando novamente em {WAIT_SECONDS}s...")
                time.sleep(WAIT_SECONDS)
        
        # Se saiu do loop sem sucesso, lança um erro
        raise ConnectionError("FALHA: Não foi possível conectar ao banco de dados após múltiplas tentativas.")

    finally:
        # Garante que a sessão seja sempre fechada
        if db_session:
            db_session.close()

# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    logger.info("🚀 Iniciando script de pré-inicialização da API...")
    init_db()
    logger.info("🏁 Script de pré-inicialização concluído.")