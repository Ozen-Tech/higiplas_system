-- Tabela de Empresas (Versão única e completa)
CREATE TABLE IF NOT EXISTS empresas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cnpj VARCHAR(18) UNIQUE, -- CNPJ é útil, mas pode ser opcional
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Categorias de Produtos
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

-- Tabela de Usuários (Versão única e completa)
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL, -- Nome mais padrão para o hash
    empresa_id INTEGER NOT NULL REFERENCES empresas(id),
    perfil VARCHAR(50) NOT NULL, -- Mantive o perfil, é uma boa ideia
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Produtos (Versão única e completa)
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    empresa_id INTEGER REFERENCES empresas(id),
    categoria_id INTEGER REFERENCES categorias(id),
    estoque_minimo INTEGER DEFAULT 0,
    estoque_atual INTEGER NOT NULL DEFAULT 0, -- <<< ADICIONE ESTA LINHA
    unidade VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Movimentações de Estoque (Sua versão com constraints é ótima)
CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
    tipo_movimentacao VARCHAR(7) NOT NULL CHECK (tipo_movimentacao IN ('ENTRADA', 'SAIDA')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    data_movimentacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    observacao TEXT
);

-- Inserindo dados iniciais para teste (Agora vai funcionar)
-- Usamos ON CONFLICT para não dar erro se tentarmos rodar o script de novo
INSERT INTO empresas (nome, cnpj) VALUES ('Higiplas', '22.599.389/0001-76'), ('Higitech', '58.142.239/0001-86') ON CONFLICT (cnpj) DO NOTHING;
INSERT INTO categorias (nome) VALUES ('Limpeza Geral'), ('Descartáveis'), ('Químicos Concentrados') ON CONFLICT (nome) DO NOTHING;