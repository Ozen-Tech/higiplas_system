# backend/app/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db.connection import engine, get_db
from app.dependencies import get_current_user
from ..db import models
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={404: {"description": "Não encontrado"}},
)


@router.post("/aplicar-migracao-reversao")
async def aplicar_migracao_reversao(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Aplica a migração de colunas de reversão e tabela arquivos_processados.
    Apenas usuários ADMIN podem executar.
    """
    
    # Verificar se é admin
    if current_user.perfil not in ['ADMIN', 'GERENTE']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem executar migrações"
        )
    
    try:
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                logger.info("🔄 Aplicando migração de reversão...")
                
                # 1. Adicionar colunas de reversão
                connection.execute(text("""
                    ALTER TABLE movimentacoes_estoque 
                    ADD COLUMN IF NOT EXISTS reversao_de_id INTEGER,
                    ADD COLUMN IF NOT EXISTS revertida BOOLEAN DEFAULT FALSE NOT NULL,
                    ADD COLUMN IF NOT EXISTS data_reversao TIMESTAMP WITH TIME ZONE,
                    ADD COLUMN IF NOT EXISTS revertida_por_id INTEGER;
                """))
                
                # 2. Criar foreign keys
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
                    END $$;
                """))
                
                connection.execute(text("""
                    DO $$
                    BEGIN
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
                
                # 3. Criar índices
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_movimentacoes_estoque_reversao_de_id 
                    ON movimentacoes_estoque(reversao_de_id);
                """))
                
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_movimentacoes_estoque_revertida 
                    ON movimentacoes_estoque(revertida);
                """))
                
                # 4. Criar tipos ENUM
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
                
                # 5. Criar tabela arquivos_processados
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS arquivos_processados (
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
                
                # 6. Criar índices para arquivos_processados
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_arquivos_processados_nome_arquivo 
                    ON arquivos_processados(nome_arquivo);
                """))
                
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_arquivos_processados_hash_arquivo 
                    ON arquivos_processados(hash_arquivo);
                """))
                
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_arquivos_processados_nota_fiscal 
                    ON arquivos_processados(nota_fiscal);
                """))
                
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_arquivos_processados_data_processamento 
                    ON arquivos_processados(data_processamento);
                """))
                
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_arquivos_processados_empresa_id 
                    ON arquivos_processados(empresa_id);
                """))
                
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_arquivo_empresa_data 
                    ON arquivos_processados(empresa_id, data_processamento);
                """))
                
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_arquivo_nf 
                    ON arquivos_processados(nota_fiscal, empresa_id);
                """))
                
                trans.commit()
                
                logger.info("✅ Migração aplicada com sucesso!")
                
                return {
                    "sucesso": True,
                    "mensagem": "Migração aplicada com sucesso! Colunas de reversão e tabela arquivos_processados criadas.",
                    "colunas_criadas": [
                        "reversao_de_id",
                        "revertida",
                        "data_reversao",
                        "revertida_por_id"
                    ],
                    "tabela_criada": "arquivos_processados"
                }
                
            except Exception as e:
                trans.rollback()
                logger.error(f"❌ Erro ao aplicar migração: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao aplicar migração: {str(e)}"
                )
                
    except Exception as e:
        logger.error(f"❌ Erro de conexão: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro de conexão: {str(e)}"
        )
