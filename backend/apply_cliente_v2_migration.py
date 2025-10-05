#!/usr/bin/env python3
"""
Script para aplicar as alterações do cliente v2 no banco de dados
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def apply_migration():
    """Aplicar migration para cliente v2"""
    
    # Obter URL do banco
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no .env")
        return False
    
    # Se for SQLite, ajustar URL
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
    
    try:
        # Conectar ao banco
        engine = create_engine(DATABASE_URL)
        
        with engine.begin() as conn:
            print("📦 Aplicando alterações na tabela clientes...")
            
            # Verificar se as colunas já existem
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'clientes' 
                AND column_name IN ('observacoes', 'referencia_localizacao', 'vendedor_id', 'criado_em', 'atualizado_em')
            """))
            
            existing_columns = [row[0] for row in result]
            
            # Adicionar colunas que não existem
            if 'observacoes' not in existing_columns:
                conn.execute(text("ALTER TABLE clientes ADD COLUMN observacoes VARCHAR(500)"))
                print("✅ Adicionada coluna: observacoes")
            
            if 'referencia_localizacao' not in existing_columns:
                conn.execute(text("ALTER TABLE clientes ADD COLUMN referencia_localizacao VARCHAR(200)"))
                print("✅ Adicionada coluna: referencia_localizacao")
            
            if 'vendedor_id' not in existing_columns:
                conn.execute(text("ALTER TABLE clientes ADD COLUMN vendedor_id INTEGER REFERENCES usuarios(id)"))
                print("✅ Adicionada coluna: vendedor_id")
            
            if 'criado_em' not in existing_columns:
                conn.execute(text("ALTER TABLE clientes ADD COLUMN criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()"))
                print("✅ Adicionada coluna: criado_em")
            
            if 'atualizado_em' not in existing_columns:
                conn.execute(text("ALTER TABLE clientes ADD COLUMN atualizado_em TIMESTAMP WITH TIME ZONE"))
                print("✅ Adicionada coluna: atualizado_em")
            
            # Criar índices se não existirem
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_clientes_telefone ON clientes(telefone)
            """))
            print("✅ Índice criado: ix_clientes_telefone")
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_clientes_vendedor_id ON clientes(vendedor_id)
            """))
            print("✅ Índice criado: ix_clientes_vendedor_id")
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_clientes_criado_em ON clientes(criado_em)
            """))
            print("✅ Índice criado: ix_clientes_criado_em")
            
            print("\n🎉 Migration aplicada com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao aplicar migration: {e}")
        return False

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
