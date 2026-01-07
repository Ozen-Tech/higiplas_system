#!/usr/bin/env python3
"""
Script para adicionar colunas faltantes de concorrente diretamente no banco
"""
import sys
sys.path.insert(0, '/code')

from app.db.connection import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print('=' * 60)
    print('ADICIONANDO COLUNAS FALTANTES')
    print('=' * 60)
    
    # Verificar quais colunas já existem
    result = db.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'propostas_detalhadas_itens'
        AND column_name LIKE 'concorrente%'
        ORDER BY column_name;
    """))
    
    colunas_existentes = [row[0] for row in result]
    print(f'\n📋 Colunas de concorrente existentes: {colunas_existentes}')
    
    # Adicionar colunas faltantes
    colunas_necessarias = {
        'concorrente_quantidade': 'FLOAT',
        'concorrente_dilucao_numerador': 'FLOAT',
        'concorrente_dilucao_denominador': 'FLOAT'
    }
    
    for coluna, tipo in colunas_necessarias.items():
        if coluna not in colunas_existentes:
            print(f'\n➕ Adicionando coluna: {coluna}')
            try:
                db.execute(text(f"""
                    ALTER TABLE propostas_detalhadas_itens 
                    ADD COLUMN {coluna} {tipo};
                """))
                print(f'   ✅ {coluna} adicionada com sucesso!')
            except Exception as e:
                print(f'   ⚠️  Erro ao adicionar {coluna}: {e}')
        else:
            print(f'   ✓ {coluna} já existe')
    
    db.commit()
    
    # Verificar novamente
    result = db.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'propostas_detalhadas_itens'
        AND column_name LIKE 'concorrente%'
        ORDER BY column_name;
    """))
    
    colunas_finais = [row[0] for row in result]
    
    print('\n' + '=' * 60)
    print('✅ CONCLUÍDO!')
    print('=' * 60)
    print(f'\n📊 Colunas de concorrente na tabela:')
    for col in colunas_finais:
        print(f'   • {col}')
    
    # Verificar se todas as necessárias estão presentes
    todas_presentes = all(col in colunas_finais for col in colunas_necessarias.keys())
    if todas_presentes:
        print('\n🎉 Todas as colunas necessárias estão presentes!')
    else:
        faltantes = [col for col in colunas_necessarias.keys() if col not in colunas_finais]
        print(f'\n⚠️  Colunas ainda faltando: {faltantes}')
    
except Exception as e:
    db.rollback()
    print(f'\n❌ ERRO: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()

