CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cnpj VARCHAR(18) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    codigo VARCHAR(50) UNIQUE,
    empresa_id INTEGER NOT NULL REFERENCES empresas(id),
    categoria_id INTEGER REFERENCES categorias(id),
    estoque_minimo INTEGER DEFAULT 0,
    unidade VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para registrar movimentações de estoque
CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER NOT NULL,
    tipo_movimentacao VARCHAR(7) NOT NULL, -- 'ENTRADA' ou 'SAIDA'
    quantidade INTEGER NOT NULL,
    data_movimentacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER, -- Opcional, mas bom para rastrear quem fez
    observacao TEXT,
    CONSTRAINT fk_produto
        FOREIGN KEY(produto_id) 
        REFERENCES produtos(id)
        ON DELETE CASCADE, -- Se um produto for deletado, suas movimentações também são.
    CONSTRAINT fk_usuario
        FOREIGN KEY(usuario_id)
        REFERENCES usuarios(id)
        ON DELETE SET NULL, -- Se o usuário for deletado, a movimentação não é perdida.
    CONSTRAINT chk_tipo_movimentacao CHECK (tipo_movimentacao IN ('ENTRADA', 'SAIDA')),
    CONSTRAINT chk_quantidade_positiva CHECK (quantidade > 0)
);

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    empresa_id INTEGER NOT NULL REFERENCES empresas(id),
    perfil VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Inserindo dados iniciais para teste
INSERT INTO empresas (nome, cnpj) VALUES ('Higiplas', '22.599.389/0001-76'), ('Higitech', '58.142.239/0001-86');
INSERT INTO categorias (nome) VALUES ('Limpeza Geral'), ('Descartáveis'), ('Químicos Concentrados');