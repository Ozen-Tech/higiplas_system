-- Script para adicionar colunas de reversão em movimentacoes_estoque
-- Execute este script no banco de dados PostgreSQL se as colunas não existirem

-- Adicionar cada coluna apenas se não existir
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

-- Criar foreign keys apenas se não existirem
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

-- Criar índices apenas se não existirem
CREATE INDEX IF NOT EXISTS ix_movimentacoes_estoque_reversao_de_id 
ON movimentacoes_estoque(reversao_de_id);

CREATE INDEX IF NOT EXISTS ix_movimentacoes_estoque_revertida 
ON movimentacoes_estoque(revertida);
