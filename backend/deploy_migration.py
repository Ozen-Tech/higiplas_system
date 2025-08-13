#!/usr/bin/env python3
"""
Script para aplicar migração no banco de produção do Render.
"""

import os
import subprocess
import sys

def run_migration_on_render():
    """Executa a migração no ambiente de produção do Render."""
    
    print("=== APLICANDO MIGRAÇÃO NO RENDER ===")
    print("Este script irá aplicar a migração que adiciona as colunas faltantes")
    print("na tabela historico_pagamentos no banco de produção.")
    print()
    
    # Verifica se estamos no diretório correto
    if not os.path.exists('alembic.ini'):
        print("❌ Arquivo alembic.ini não encontrado. Execute este script no diretório backend.")
        return False
    
    try:
        # Primeiro, vamos fazer commit e push das alterações
        print("📤 Fazendo commit das alterações da migração...")
        
        # Add files
        subprocess.run(['git', 'add', '.'], check=True, cwd='.')
        
        # Commit
        commit_result = subprocess.run([
            'git', 'commit', '-m', 
            'fix: add missing columns to historico_pagamentos table\n\n- Add data_vencimento column\n- Add numero_nf column\n- Add data_criacao column\n- Add orcamento_id column and foreign key\n- Fix schema validation error in production'
        ], cwd='.', capture_output=True, text=True)
        
        if commit_result.returncode == 0:
            print("✅ Commit realizado com sucesso")
        else:
            print(f"⚠️  Commit: {commit_result.stdout} {commit_result.stderr}")
        
        # Push
        print("📤 Fazendo push para o repositório...")
        push_result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                   check=True, cwd='.', capture_output=True, text=True)
        print("✅ Push realizado com sucesso")
        
        print("\n🚀 Alterações enviadas para o repositório!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Acesse o dashboard do Render: https://dashboard.render.com")
        print("2. Vá para o seu serviço 'higiplas-system'")
        print("3. Clique em 'Manual Deploy' -> 'Deploy latest commit'")
        print("4. Aguarde o deploy terminar")
        print("5. Acesse os logs do serviço para verificar se a migração foi aplicada")
        print("\n⚠️  IMPORTANTE: A migração será aplicada automaticamente durante o deploy")
        print("   pois o comando 'alembic upgrade head' está no script de inicialização.")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar comando: {e}")
        print(f"Saída: {e.stdout if hasattr(e, 'stdout') else 'N/A'}")
        print(f"Erro: {e.stderr if hasattr(e, 'stderr') else 'N/A'}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def show_manual_instructions():
    """Mostra instruções manuais caso o script automático falhe."""
    print("\n=== INSTRUÇÕES MANUAIS ===")
    print("Se preferir fazer manualmente:")
    print()
    print("1. Commit e push das alterações:")
    print("   git add .")
    print("   git commit -m 'fix: add missing columns to historico_pagamentos table'")
    print("   git push origin main")
    print()
    print("2. No Render Dashboard:")
    print("   - Acesse https://dashboard.render.com")
    print("   - Vá para o serviço 'higiplas-system'")
    print("   - Clique em 'Manual Deploy' -> 'Deploy latest commit'")
    print()
    print("3. Monitore os logs durante o deploy para verificar se a migração foi aplicada.")

if __name__ == "__main__":
    print("🔧 CORREÇÃO DO BANCO DE DADOS DE PRODUÇÃO")
    print("Este script irá preparar e aplicar a correção no Render.")
    print()
    
    resposta = input("Deseja continuar com o deploy automático? (s/N): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        success = run_migration_on_render()
        if not success:
            show_manual_instructions()
    else:
        show_manual_instructions()