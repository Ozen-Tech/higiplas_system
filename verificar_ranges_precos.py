#!/usr/bin/env python3
"""
Script para verificar e popular a tabela de ranges de preços (PrecoClienteProduto)
"""
import sys
import os

# Adicionar o diretório backend ao path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

from app.db.connection import SessionLocal
from app.db import models

def main():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("VERIFICAÇÃO DE RANGES DE PREÇOS")
        print("=" * 60)
        
        # 1. Verificar quantos registros existem na tabela PrecoClienteProduto
        count_precos = db.query(models.PrecoClienteProduto).count()
        print(f"\n📊 Total de registros em PrecoClienteProduto: {count_precos}")
        
        # 2. Mostrar alguns exemplos se existir
        if count_precos > 0:
            exemplos = db.query(models.PrecoClienteProduto).limit(10).all()
            print("\n✅ Exemplos de registros encontrados:")
            for p in exemplos:
                cliente = db.query(models.Cliente).filter(models.Cliente.id == p.cliente_id).first()
                produto = db.query(models.Produto).filter(models.Produto.id == p.produto_id).first()
                cliente_nome = cliente.nome if cliente else "Desconhecido"
                produto_nome = produto.nome if produto else "Desconhecido"
                print(f"  • {cliente_nome} → {produto_nome}")
                print(f"    Min: R$ {p.preco_minimo or 0:.2f} | Max: R$ {p.preco_maximo or 0:.2f} | Vendas: {p.total_vendas}")
        
        # 3. Verificar quantos orçamentos finalizados existem
        orcamentos_finalizados = db.query(models.Orcamento).filter(
            models.Orcamento.status.in_(['FINALIZADO', 'APROVADO'])
        ).count()
        print(f"\n📋 Orçamentos finalizados/aprovados no sistema: {orcamentos_finalizados}")
        
        # 4. Se a tabela estiver vazia mas houver orçamentos, sugerir recálculo
        if count_precos == 0 and orcamentos_finalizados > 0:
            print("\n" + "=" * 60)
            print("⚠️  ATENÇÃO: Tabela de ranges vazia mas há orçamentos!")
            print("=" * 60)
            print("\nVocê precisa executar o endpoint de recálculo:")
            print("  POST /api/orcamentos/admin/recalcular-precos")
            print("\nOu executar o script de recálculo:")
            print("  python3 recalcular_ranges_precos.py")
            return False
        
        # 5. Se não há orçamentos, informar
        if orcamentos_finalizados == 0:
            print("\n" + "=" * 60)
            print("ℹ️  Não há orçamentos finalizados ainda")
            print("=" * 60)
            print("\nOs ranges de preços serão calculados automaticamente quando você:")
            print("  1. Finalizar orçamentos (status FINALIZADO ou APROVADO)")
            print("  2. Executar o endpoint de recálculo")
            return True
        
        # 6. Tudo OK
        if count_precos > 0:
            print("\n" + "=" * 60)
            print("✅ Sistema de ranges de preços está funcionando!")
            print("=" * 60)
            return True
            
    except Exception as e:
        print(f"\n❌ Erro ao verificar: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

