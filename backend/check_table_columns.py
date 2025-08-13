#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine
import sqlalchemy as sa

def check_historico_pagamentos_columns():
    """Verifica as colunas da tabela historico_pagamentos."""
    try:
        with engine.connect() as conn:
            # Verifica se a tabela existe
            result = conn.execute(sa.text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'historico_pagamentos')"
            ))
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ Tabela 'historico_pagamentos' não existe")
                return
            
            print("✅ Tabela 'historico_pagamentos' existe")
            
            # Lista as colunas
            result = conn.execute(sa.text(
                "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'historico_pagamentos' ORDER BY ordinal_position"
            ))
            
            print("\nColunas da tabela 'historico_pagamentos':")
            columns = list(result)
            if not columns:
                print("❌ Nenhuma coluna encontrada")
            else:
                for column_name, data_type, is_nullable in columns:
                    nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
                    print(f"- {column_name}: {data_type} ({nullable})")
                    
                # Verifica se data_vencimento existe
                column_names = [col[0] for col in columns]
                if 'data_vencimento' in column_names:
                    print("\n✅ Coluna 'data_vencimento' existe")
                else:
                    print("\n❌ Coluna 'data_vencimento' NÃO existe")
                    
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e}")

if __name__ == "__main__":
    check_historico_pagamentos_columns()