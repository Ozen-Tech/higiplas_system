#!/usr/bin/env python3
"""
Script para corrigir o banco de dados de produção no Render.
Adiciona as colunas faltantes na tabela historico_pagamentos.
"""

import os
import sys
import sqlalchemy as sa
from sqlalchemy import create_engine, text

def get_production_db_url():
    """Obtém a URL do banco de produção."""
    # URL do banco de produção no Render
    return os.getenv('DATABASE_URL') or input("Digite a URL do banco de produção: ")

def fix_production_database():
    """Corrige o banco de dados de produção."""
    try:
        # Conecta ao banco de produção
        db_url = get_production_db_url()
        if not db_url:
            print("❌ URL do banco de dados não fornecida")
            return False
            
        print(f"🔗 Conectando ao banco de produção...")
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Verifica se a tabela existe
            result = conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'historico_pagamentos')"
            ))
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ Tabela 'historico_pagamentos' não existe no banco de produção")
                return False
            
            print("✅ Tabela 'historico_pagamentos' encontrada")
            
            # Verifica quais colunas existem
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'historico_pagamentos'"
            ))
            existing_columns = [row[0] for row in result]
            print(f"📋 Colunas existentes: {existing_columns}")
            
            # Lista de colunas que devem existir
            required_columns = {
                'data_vencimento': 'DATE NOT NULL DEFAULT \'2024-01-01\'',
                'numero_nf': 'VARCHAR',
                'data_criacao': 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()',
                'orcamento_id': 'INTEGER'
            }
            
            # Adiciona colunas faltantes
            columns_added = []
            for column_name, column_def in required_columns.items():
                if column_name not in existing_columns:
                    print(f"➕ Adicionando coluna '{column_name}'...")
                    
                    # Comando SQL para adicionar a coluna
                    if column_name == 'data_vencimento':
                        # Adiciona com valor padrão temporário
                        conn.execute(text(f"ALTER TABLE historico_pagamentos ADD COLUMN {column_name} {column_def}"))
                        # Remove o valor padrão
                        conn.execute(text(f"ALTER TABLE historico_pagamentos ALTER COLUMN {column_name} DROP DEFAULT"))
                    else:
                        conn.execute(text(f"ALTER TABLE historico_pagamentos ADD COLUMN {column_name} {column_def}"))
                    
                    columns_added.append(column_name)
                    print(f"✅ Coluna '{column_name}' adicionada")
                else:
                    print(f"✅ Coluna '{column_name}' já existe")
            
            # Adiciona foreign key para orcamento_id se não existir
            if 'orcamento_id' in columns_added:
                try:
                    print("🔗 Adicionando foreign key para orcamento_id...")
                    conn.execute(text(
                        "ALTER TABLE historico_pagamentos ADD CONSTRAINT fk_historico_pagamentos_orcamento_id "
                        "FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id)"
                    ))
                    print("✅ Foreign key adicionada")
                except Exception as e:
                    print(f"⚠️  Aviso: Não foi possível adicionar foreign key: {e}")
            
            # Commit das alterações
            conn.commit()
            
            if columns_added:
                print(f"\n🎉 Banco de dados corrigido! Colunas adicionadas: {columns_added}")
            else:
                print("\n✅ Banco de dados já estava correto!")
            
            # Verifica o resultado final
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'historico_pagamentos' ORDER BY ordinal_position"
            ))
            final_columns = [row[0] for row in result]
            print(f"📋 Colunas finais: {final_columns}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao corrigir banco de dados: {e}")
        return False

if __name__ == "__main__":
    print("=== CORREÇÃO DO BANCO DE DADOS DE PRODUÇÃO ===")
    print("Este script irá adicionar as colunas faltantes na tabela historico_pagamentos")
    print()
    
    # Verifica se a URL foi fornecida como variável de ambiente
    if not os.getenv('DATABASE_URL'):
        print("⚠️  Variável DATABASE_URL não encontrada")
        print("Você pode:")
        print("1. Definir a variável: export DATABASE_URL='sua_url_aqui'")
        print("2. Fornecer a URL quando solicitado")
        print()
    
    resposta = input("Deseja continuar? (s/N): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        success = fix_production_database()
        if success:
            print("\n🎉 Correção concluída com sucesso!")
            print("O backend agora deve funcionar corretamente.")
        else:
            print("\n❌ Correção falhou. Verifique os logs acima.")
            sys.exit(1)
    else:
        print("Operação cancelada.")