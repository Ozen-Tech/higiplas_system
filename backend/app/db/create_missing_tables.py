"""
Script para criar tabelas faltantes no banco de dados.
Executado automaticamente no startup da aplicação.
"""
import logging
from sqlalchemy import text
from app.db.connection import engine

logger = logging.getLogger(__name__)


def create_historico_preco_produto_table():
    """Cria a tabela historico_preco_produto se não existir."""
    try:
        with engine.connect() as connection:
            # Verificar se a tabela já existe
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'historico_preco_produto'
                );
            """))
            exists = result.scalar()
            
            if exists:
                logger.info("✓ Tabela historico_preco_produto já existe")
                return
            
            logger.info("Criando tabela historico_preco_produto...")
            
            # Criar tabela
            connection.execute(text("""
                CREATE TABLE historico_preco_produto (
                    id SERIAL PRIMARY KEY,
                    produto_id INTEGER NOT NULL REFERENCES produtos(id),
                    preco_unitario DOUBLE PRECISION NOT NULL,
                    quantidade DOUBLE PRECISION NOT NULL,
                    valor_total DOUBLE PRECISION NOT NULL,
                    nota_fiscal VARCHAR,
                    data_venda TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    empresa_id INTEGER NOT NULL REFERENCES empresas(id),
                    cliente_id INTEGER REFERENCES clientes(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Criar índices
            connection.execute(text("CREATE INDEX ix_historico_preco_produto_produto_id ON historico_preco_produto(produto_id);"))
            connection.execute(text("CREATE INDEX ix_historico_preco_produto_nota_fiscal ON historico_preco_produto(nota_fiscal);"))
            connection.execute(text("CREATE INDEX ix_historico_preco_produto_data_venda ON historico_preco_produto(data_venda);"))
            connection.execute(text("CREATE INDEX ix_historico_preco_produto_empresa_id ON historico_preco_produto(empresa_id);"))
            connection.execute(text("CREATE INDEX ix_historico_preco_produto_cliente_id ON historico_preco_produto(cliente_id);"))
            
            connection.commit()
            logger.info("✓ Tabela historico_preco_produto criada com sucesso!")
            
    except Exception as e:
        logger.error(f"Erro ao criar tabela historico_preco_produto: {e}")
        # Não levantar exceção para não impedir o startup da aplicação
        

def create_all_missing_tables():
    """Cria todas as tabelas faltantes necessárias."""
    create_historico_preco_produto_table()
