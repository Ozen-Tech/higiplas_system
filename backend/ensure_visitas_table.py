#!/usr/bin/env python3
"""
Script para garantir que a tabela visitas_vendedor existe no banco de dados.
Executa diretamente via SQL, independente do estado das migrações Alembic.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

def ensure_visitas_table():
    """Garante que a tabela visitas_vendedor existe."""
    
    try:
        # Criar engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.begin() as conn:
            # Verificar se a tabela existe
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if 'visitas_vendedor' in tables:
                print("✓ Tabela visitas_vendedor já existe")
                return True
            
            print("⚠ Tabela visitas_vendedor não existe. Criando...")
            
            # Criar tabela
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS visitas_vendedor (
                    id SERIAL PRIMARY KEY,
                    vendedor_id INTEGER NOT NULL,
                    cliente_id INTEGER,
                    data_visita TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    latitude DOUBLE PRECISION NOT NULL,
                    longitude DOUBLE PRECISION NOT NULL,
                    endereco_completo VARCHAR,
                    motivo_visita VARCHAR,
                    observacoes VARCHAR,
                    foto_comprovante VARCHAR,
                    confirmada BOOLEAN NOT NULL DEFAULT FALSE,
                    empresa_id INTEGER NOT NULL,
                    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    CONSTRAINT fk_visitas_vendedor FOREIGN KEY (vendedor_id) REFERENCES usuarios(id),
                    CONSTRAINT fk_visitas_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                    CONSTRAINT fk_visitas_empresa FOREIGN KEY (empresa_id) REFERENCES empresas(id)
                );
            """))
            
            # Criar índices
            indices = [
                "CREATE INDEX IF NOT EXISTS ix_visitas_vendedor_id ON visitas_vendedor(id);",
                "CREATE INDEX IF NOT EXISTS ix_visitas_vendedor_vendedor_id ON visitas_vendedor(vendedor_id);",
                "CREATE INDEX IF NOT EXISTS ix_visitas_vendedor_cliente_id ON visitas_vendedor(cliente_id);",
                "CREATE INDEX IF NOT EXISTS ix_visitas_vendedor_data_visita ON visitas_vendedor(data_visita);",
                "CREATE INDEX IF NOT EXISTS ix_visitas_vendedor_confirmada ON visitas_vendedor(confirmada);",
                "CREATE INDEX IF NOT EXISTS ix_visitas_vendedor_empresa_id ON visitas_vendedor(empresa_id);",
                "CREATE INDEX IF NOT EXISTS idx_visita_vendedor_data ON visitas_vendedor(vendedor_id, data_visita);",
                "CREATE INDEX IF NOT EXISTS idx_visita_cliente ON visitas_vendedor(cliente_id, data_visita);",
                "CREATE INDEX IF NOT EXISTS idx_visita_empresa_confirmada ON visitas_vendedor(empresa_id, confirmada, data_visita);",
            ]
            
            for index_sql in indices:
                try:
                    conn.execute(text(index_sql))
                except Exception as e:
                    print(f"⚠ Aviso ao criar índice: {e}")
            
            conn.commit()
            print("✓ Tabela visitas_vendedor criada com sucesso!")
            return True
            
    except Exception as e:
        print(f"✗ Erro ao garantir tabela visitas_vendedor: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = ensure_visitas_table()
    sys.exit(0 if success else 1)
