-- Script para criar a tabela historico_preco_produto
-- Execute este script no banco de dados do Render

-- Criar tabela historico_preco_produto se não existir
CREATE TABLE IF NOT EXISTS historico_preco_produto (
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

-- Criar índices
CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_produto_id ON historico_preco_produto(produto_id);
CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_nota_fiscal ON historico_preco_produto(nota_fiscal);
CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_data_venda ON historico_preco_produto(data_venda);
CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_empresa_id ON historico_preco_produto(empresa_id);
CREATE INDEX IF NOT EXISTS ix_historico_preco_produto_cliente_id ON historico_preco_produto(cliente_id);

-- Verificar se a tabela foi criada
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'historico_preco_produto';
