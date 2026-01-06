#!/usr/bin/env python3
"""
Script para recalcular ranges de preços baseado em orçamentos finalizados
"""
import sys
import os

# Adicionar o diretório backend ao path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

from app.db.connection import SessionLocal
from app.db import models

def recalcular_ranges():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("RECÁLCULO DE RANGES DE PREÇOS")
        print("=" * 60)
        
        # Buscar todos os orçamentos finalizados ou aprovados
        orcamentos = db.query(models.Orcamento).filter(
            models.Orcamento.status.in_(['FINALIZADO', 'APROVADO'])
        ).all()
        
        print(f"\n📋 Encontrados {len(orcamentos)} orçamentos finalizados/aprovados")
        
        if len(orcamentos) == 0:
            print("\n⚠️  Não há orçamentos para processar.")
            print("Finalize alguns orçamentos primeiro!")
            return True
        
        precos_atualizados = 0
        clientes_processados = set()
        
        print("\n🔄 Processando orçamentos...")
        
        for orcamento in orcamentos:
            cliente_id = orcamento.cliente_id
            
            # Processar cada item do orçamento
            for item in orcamento.itens:
                # Ignorar itens personalizados (sem produto_id)
                if not item.produto_id:
                    continue
                    
                produto_id = item.produto_id
                preco_vendido = item.preco_unitario
                
                # Buscar ou criar registro de preço cliente-produto
                preco_cliente = db.query(models.PrecoClienteProduto).filter(
                    models.PrecoClienteProduto.cliente_id == cliente_id,
                    models.PrecoClienteProduto.produto_id == produto_id
                ).first()
                
                if not preco_cliente:
                    # Criar novo registro
                    preco_cliente = models.PrecoClienteProduto(
                        cliente_id=cliente_id,
                        produto_id=produto_id,
                        preco_padrao=preco_vendido,
                        preco_minimo=preco_vendido,
                        preco_maximo=preco_vendido,
                        preco_medio=preco_vendido,
                        total_vendas=1,
                        data_ultima_venda=orcamento.data_criacao
                    )
                    db.add(preco_cliente)
                else:
                    # Atualizar registro existente
                    preco_cliente.total_vendas = (preco_cliente.total_vendas or 0) + 1
                    
                    # Atualizar mínimo se necessário
                    if preco_cliente.preco_minimo is None or preco_vendido < preco_cliente.preco_minimo:
                        preco_cliente.preco_minimo = preco_vendido
                    
                    # Atualizar máximo se necessário
                    if preco_cliente.preco_maximo is None or preco_vendido > preco_cliente.preco_maximo:
                        preco_cliente.preco_maximo = preco_vendido
                    
                    # Atualizar média (média ponderada simplificada)
                    if preco_cliente.preco_medio:
                        preco_cliente.preco_medio = (
                            (preco_cliente.preco_medio * (preco_cliente.total_vendas - 1) + preco_vendido) 
                            / preco_cliente.total_vendas
                        )
                    else:
                        preco_cliente.preco_medio = preco_vendido
                    
                    # Atualizar último preço e data
                    preco_cliente.preco_padrao = preco_vendido
                    if orcamento.data_criacao:
                        if preco_cliente.data_ultima_venda is None or orcamento.data_criacao > preco_cliente.data_ultima_venda:
                            preco_cliente.data_ultima_venda = orcamento.data_criacao
                
                precos_atualizados += 1
                clientes_processados.add(cliente_id)
        
        # Salvar no banco
        db.commit()
        
        print("\n" + "=" * 60)
        print("✅ RECÁLCULO CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print(f"\n📊 Estatísticas:")
        print(f"  • Orçamentos processados: {len(orcamentos)}")
        print(f"  • Clientes com histórico: {len(clientes_processados)}")
        print(f"  • Registros de preços atualizados: {precos_atualizados}")
        
        # Mostrar alguns exemplos
        print("\n📋 Exemplos de ranges calculados:")
        exemplos = db.query(models.PrecoClienteProduto).limit(5).all()
        for p in exemplos:
            cliente = db.query(models.Cliente).filter(models.Cliente.id == p.cliente_id).first()
            produto = db.query(models.Produto).filter(models.Produto.id == p.produto_id).first()
            cliente_nome = cliente.nome if cliente else "Desconhecido"
            produto_nome = produto.nome if produto else "Desconhecido"
            print(f"  • {cliente_nome} → {produto_nome}")
            print(f"    Min: R$ {p.preco_minimo:.2f} | Max: R$ {p.preco_maximo:.2f} | Vendas: {p.total_vendas}")
        
        print("\n🎉 Agora os vendedores verão os ranges de preços ao criar orçamentos!")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro ao recalcular: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = recalcular_ranges()
    sys.exit(0 if success else 1)

