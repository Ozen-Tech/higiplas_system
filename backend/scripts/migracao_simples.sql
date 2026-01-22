-- Script SQL simples para aplicar migração de reversão
-- Execute no psql do Render: psql $DATABASE_URL -f backend/scripts/migracao_simples.sql
-- Ou copie e cole os comandos abaixo diretamente no psql

-- 1. Adicionar colunas de reversão
ALTER TABLE movimentacoes_estoque 
ADD COLUMN IF NOT EXISTS reversao_de_id INTEGER,
ADD COLUMN IF NOT EXISTS revertida BOOLEAN DEFAULT FALSE NOT NULL,
ADD COLUMN IF NOT EXISTS data_reversao TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS revertida_por_id INTEGER;

-- 2. Criar foreign keys
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_movimentacao_reversao_de') THEN
        ALTER TABLE movimentacoes_estoque
        ADD CONSTRAINT fk_movimentacao_reversao_de
        FOREIGN KEY (reversao_de_id) REFERENCES movimentacoes_estoque(id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_movimentacao_revertida_por') THEN
        ALTER TABLE movimentacoes_estoque
        ADD CONSTRAINT fk_movimentacao_revertida_por
        FOREIGN KEY (revertida_por_id) REFERENCES usuarios(id);
    END IF;
END $$;

-- 3. Criar índices
CREATE INDEX IF NOT EXISTS ix_movimentacoes_estoque_reversao_de_id ON movimentacoes_estoque(reversao_de_id);
CREATE INDEX IF NOT EXISTS ix_movimentacoes_estoque_revertida ON movimentacoes_estoque(revertida);

-- 4. Criar tipos ENUM
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_arquivo_enum') THEN
        CREATE TYPE tipo_arquivo_enum AS ENUM ('PDF', 'XML');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_mov_arquivo_enum') THEN
        CREATE TYPE tipo_mov_arquivo_enum AS ENUM ('ENTRADA', 'SAIDA');
    END IF;
END $$;

-- 5. Criar tabela arquivos_processados
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

-- 6. Criar índices para arquivos_processados
CREATE INDEX IF NOT EXISTS ix_arquivos_processados_nome_arquivo ON arquivos_processados(nome_arquivo);
CREATE INDEX IF NOT EXISTS ix_arquivos_processados_hash_arquivo ON arquivos_processados(hash_arquivo);
CREATE INDEX IF NOT EXISTS ix_arquivos_processados_nota_fiscal ON arquivos_processados(nota_fiscal);
CREATE INDEX IF NOT EXISTS ix_arquivos_processados_data_processamento ON arquivos_processados(data_processamento);
CREATE INDEX IF NOT EXISTS ix_arquivos_processados_empresa_id ON arquivos_processados(empresa_id);
CREATE INDEX IF NOT EXISTS idx_arquivo_empresa_data ON arquivos_processados(empresa_id, data_processamento);
CREATE INDEX IF NOT EXISTS idx_arquivo_nf ON arquivos_processados(nota_fiscal, empresa_id);

-- Mensagem de sucesso
SELECT '✅ Migração aplicada com sucesso!' AS resultado;
