import logging
import json
import os
import traceback
from sqlalchemy.orm import Session

# Precisamos configurar o caminho para que ele encontre os módulos da 'app'
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Agora podemos importar os módulos da nossa aplicação
from app.db.connection import SessionLocal
from app.db.models import VendaHistorica # Importamos o modelo específico

# Configuração do Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def seed_database():
    """
    Função principal que lê o JSON e popula o banco de dados.
    """
    db: Session | None = None
    try:
        db = SessionLocal()
        
        json_path = "app/dados_historicos_vendas.json"
        logger.info(f"Tentando ler o arquivo de dados em: '{json_path}'")

        if not os.path.exists(json_path):
            logger.error(f"❌ ARQUIVO NÃO ENCONTRADO! O caminho '{json_path}' não existe. Certifique-se de que o arquivo 'dados_historicos_vendas.json' está na pasta 'app' e foi commitado.")
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            historical_data = json.load(f)
        
        logger.info(f"Arquivo JSON carregado com sucesso, contendo {len(historical_data)} registros.")
        logger.info("Iniciando a inserção no banco de dados. Isso pode levar um momento...")

        new_entries_count = 0
        existing_entries_count = 0

        for item in historical_data:
            # Pega o ID antigo para verificação
            ident_antigo = item.get('ident_antigo')
            if not ident_antigo:
                logger.warning(f"Item sem 'ident_antigo' encontrado. Pulando: {item}")
                continue

            # Verifica se o registro já existe no banco
            exists = db.query(VendaHistorica).filter_by(ident_antigo=ident_antigo).first()
            
            if exists:
                existing_entries_count += 1
                continue
            
            # Se não existe, cria um novo objeto e adiciona à sessão
            new_record = VendaHistorica(
                ident_antigo=ident_antigo,
                descricao=item.get('descricao'),
                quantidade_vendida_total=item.get('quantidade_vendida_total', 0.0),
                custo_compra_total=item.get('custo_compra_total', 0.0),
                valor_vendido_total=item.get('valor_vendido_total', 0.0),
                lucro_bruto_total=item.get('lucro_bruto_total', 0.0),
                margem_lucro_percentual=item.get('margem_lucro_percentual', 0.0)
            )
            db.add(new_record)
            new_entries_count += 1
        
        # Faz o commit de todas as novas entradas de uma só vez
        if new_entries_count > 0:
            logger.info(f"Realizando commit de {new_entries_count} novos registros...")
            db.commit()
            logger.info("Commit realizado com sucesso!")
        else:
            logger.info("Nenhum novo registro para adicionar.")

        logger.info("\n--- ✅ PROCESSO DE SEEDING CONCLUÍDO ---")
        logger.info(f"-> Novos registros inseridos: {new_entries_count}")
        logger.info(f"-> Registros que já existiam e foram ignorados: {existing_entries_count}")

    except Exception as e:
        logger.error("❌ Ocorreu um erro catastrófico durante o seeding.")
        logger.error(traceback.format_exc())
        if db:
            db.rollback() # Desfaz qualquer mudança parcial em caso de erro
    finally:
        if db:
            db.close()
            logger.info("Sessão do banco de dados fechada.")

if __name__ == "__main__":
    seed_database()