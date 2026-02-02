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
        

def create_reversao_columns_and_tables():
    """Adiciona colunas de reversão em movimentacoes_estoque e cria tabela arquivos_processados."""
    try:
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                # Verificar e adicionar colunas de reversão
                logger.info("Verificando colunas de reversão em movimentacoes_estoque...")
                
                # Adicionar cada coluna apenas se não existir usando DO blocks
                # Isso garante que todas as colunas sejam criadas mesmo se algumas já existirem
                connection.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = 'movimentacoes_estoque'
                            AND column_name = 'reversao_de_id'
                        ) THEN
                            ALTER TABLE movimentacoes_estoque 
                            ADD COLUMN reversao_de_id INTEGER;
                        END IF;
                        
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = 'movimentacoes_estoque'
                            AND column_name = 'revertida'
                        ) THEN
                            ALTER TABLE movimentacoes_estoque 
                            ADD COLUMN revertida BOOLEAN DEFAULT FALSE NOT NULL;
                        END IF;
                        
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = 'movimentacoes_estoque'
                            AND column_name = 'data_reversao'
                        ) THEN
                            ALTER TABLE movimentacoes_estoque 
                            ADD COLUMN data_reversao TIMESTAMP WITH TIME ZONE;
                        END IF;
                        
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = 'movimentacoes_estoque'
                            AND column_name = 'revertida_por_id'
                        ) THEN
                            ALTER TABLE movimentacoes_estoque 
                            ADD COLUMN revertida_por_id INTEGER;
                        END IF;
                    END $$;
                """))
                
                # Criar foreign keys apenas se não existirem
                connection.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_constraint 
                            WHERE conname = 'fk_movimentacao_reversao_de'
                        ) THEN
                            ALTER TABLE movimentacoes_estoque
                            ADD CONSTRAINT fk_movimentacao_reversao_de
                            FOREIGN KEY (reversao_de_id) REFERENCES movimentacoes_estoque(id);
                        END IF;
                        
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_constraint 
                            WHERE conname = 'fk_movimentacao_revertida_por'
                        ) THEN
                            ALTER TABLE movimentacoes_estoque
                            ADD CONSTRAINT fk_movimentacao_revertida_por
                            FOREIGN KEY (revertida_por_id) REFERENCES usuarios(id);
                        END IF;
                    END $$;
                """))
                
                # Criar índices apenas se não existirem
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_movimentacoes_estoque_reversao_de_id 
                    ON movimentacoes_estoque(reversao_de_id);
                """))
                
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_movimentacoes_estoque_revertida 
                    ON movimentacoes_estoque(revertida);
                """))
                
                logger.info("✓ Colunas de reversão verificadas/criadas com sucesso!")
                
                # Criar tipos ENUM se não existirem
                connection.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_arquivo_enum') THEN
                            CREATE TYPE tipo_arquivo_enum AS ENUM ('PDF', 'XML');
                        END IF;
                        
                        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_mov_arquivo_enum') THEN
                            CREATE TYPE tipo_mov_arquivo_enum AS ENUM ('ENTRADA', 'SAIDA');
                        END IF;
                    END $$;
                """))
                
                # Verificar se a tabela arquivos_processados existe
                result = connection.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'arquivos_processados'
                    );
                """))
                tabela_existe = result.scalar()
                
                if not tabela_existe:
                    logger.info("Criando tabela arquivos_processados...")
                    connection.execute(text("""
                        CREATE TABLE arquivos_processados (
                            id SERIAL PRIMARY KEY,
                            nome_arquivo VARCHAR NOT NULL,
                            hash_arquivo VARCHAR NOT NULL UNIQUE,
                            nota_fiscal VARCHAR,
                            tipo_arquivo tipo_arquivo_enum NOT NULL,
                            tipo_movimentacao tipo_mov_arquivo_enum NOT NULL,
                            data_processamento TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
                            empresa_id INTEGER NOT NULL REFERENCES empresas(id),
                            total_produtos INTEGER NOT NULL DEFAULT 0,
                            total_movimentacoes INTEGER NOT NULL DEFAULT 0
                        );
                    """))
                    
                    # Criar índices
                    connection.execute(text("""
                        CREATE INDEX ix_arquivos_processados_nome_arquivo 
                        ON arquivos_processados(nome_arquivo);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX ix_arquivos_processados_hash_arquivo 
                        ON arquivos_processados(hash_arquivo);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX ix_arquivos_processados_nota_fiscal 
                        ON arquivos_processados(nota_fiscal);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX ix_arquivos_processados_data_processamento 
                        ON arquivos_processados(data_processamento);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX ix_arquivos_processados_empresa_id 
                        ON arquivos_processados(empresa_id);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX idx_arquivo_empresa_data 
                        ON arquivos_processados(empresa_id, data_processamento);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX idx_arquivo_nf 
                        ON arquivos_processados(nota_fiscal, empresa_id);
                    """))
                    
                    logger.info("✓ Tabela arquivos_processados criada com sucesso!")
                else:
                    logger.info("✓ Tabela arquivos_processados já existe")
                
                trans.commit()
                
            except Exception as e:
                trans.rollback()
                raise e
                
    except Exception as e:
        logger.error(f"Erro ao criar colunas de reversão e tabela arquivos_processados: {e}")
        # Não levantar exceção para não impedir o startup da aplicação


def create_regras_sugestao_compra_table():
    """Cria a tabela regras_sugestao_compra se não existir."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'regras_sugestao_compra'
                );
            """))
            if result.scalar():
                logger.info("✓ Tabela regras_sugestao_compra já existe")
                return
            logger.info("Criando tabela regras_sugestao_compra...")
            connection.execute(text("""
                CREATE TABLE regras_sugestao_compra (
                    id SERIAL PRIMARY KEY,
                    empresa_id INTEGER NOT NULL UNIQUE REFERENCES empresas(id),
                    lead_time_dias INTEGER NOT NULL DEFAULT 7,
                    cobertura_dias INTEGER NOT NULL DEFAULT 14,
                    dias_analise INTEGER NOT NULL DEFAULT 90,
                    min_vendas_historico INTEGER NOT NULL DEFAULT 2,
                    margem_seguranca DOUBLE PRECISION NOT NULL DEFAULT 1.2,
                    margem_adicional_cobertura DOUBLE PRECISION NOT NULL DEFAULT 1.15,
                    dias_antecedencia_cliente INTEGER NOT NULL DEFAULT 7
                );
                CREATE INDEX ix_regras_sugestao_compra_empresa_id ON regras_sugestao_compra(empresa_id);
            """))
            connection.commit()
            logger.info("✓ Tabela regras_sugestao_compra criada com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao criar tabela regras_sugestao_compra: {e}")


def create_all_missing_tables():
    """Cria todas as tabelas faltantes necessárias."""
    create_historico_preco_produto_table()
    create_reversao_columns_and_tables()
    create_regras_sugestao_compra_table()