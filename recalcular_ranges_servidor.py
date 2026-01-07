#!/usr/bin/env python3
"""
Script otimizado para executar no servidor de produção
"""
import sys
sys.path.insert(0, '/code')

from app.db.connection import SessionLocal
from app.db import models

db = SessionLocal()
try:
    print('=' * 60)
    print('RECALCULANDO RANGES DE PREÇOS')
    print('=' * 60)
    
    orcamentos = db.query(models.Orcamento).filter(
        models.Orcamento.status.in_(['FINALIZADO', 'APROVADO'])
    ).all()
    
    print(f'\n📋 Encontrados {len(orcamentos)} orçamentos finalizados/aprovados')
    
    if len(orcamentos) == 0:
        print('⚠️  Nenhum orçamento para processar')
        exit(0)
    
    precos_atualizados = 0
    clientes_processados = set()
    erros = 0
    
    for orcamento in orcamentos:
        cliente_id = orcamento.cliente_id
        
        for item in orcamento.itens:
            if not item.produto_id:
                continue
            
            try:
                produto_id = item.produto_id
                preco_vendido = item.preco_unitario_congelado  # CAMPO CORRETO!
                
                pc = db.query(models.PrecoClienteProduto).filter(
                    models.PrecoClienteProduto.cliente_id == cliente_id,
                    models.PrecoClienteProduto.produto_id == produto_id
                ).first()
                
                if not pc:
                    # Criar novo registro
                    pc = models.PrecoClienteProduto(
                        cliente_id=cliente_id,
                        produto_id=produto_id,
                        preco_padrao=preco_vendido,
                        preco_minimo=preco_vendido,
                        preco_maximo=preco_vendido,
                        preco_medio=preco_vendido,
                        total_vendas=1,
                        data_ultima_venda=orcamento.data_criacao
                    )
                    db.add(pc)
                else:
                    # Atualizar existente
                    pc.total_vendas = (pc.total_vendas or 0) + 1
                    
                    if pc.preco_minimo is None or preco_vendido < pc.preco_minimo:
                        pc.preco_minimo = preco_vendido
                    
                    if pc.preco_maximo is None or preco_vendido > pc.preco_maximo:
                        pc.preco_maximo = preco_vendido
                    
                    if pc.preco_medio:
                        pc.preco_medio = (
                            (pc.preco_medio * (pc.total_vendas - 1) + preco_vendido) 
                            / pc.total_vendas
                        )
                    else:
                        pc.preco_medio = preco_vendido
                    
                    pc.preco_padrao = preco_vendido
                    
                    if orcamento.data_criacao:
                        if pc.data_ultima_venda is None or orcamento.data_criacao > pc.data_ultima_venda:
                            pc.data_ultima_venda = orcamento.data_criacao
                
                precos_atualizados += 1
                clientes_processados.add(cliente_id)
                
            except Exception as e:
                erros += 1
                print(f'⚠️  Erro no item: {e}')
    
    db.commit()
    
    print('\n' + '=' * 60)
    print('✅ RECÁLCULO CONCLUÍDO!')
    print('=' * 60)
    print(f'\n📊 Estatísticas:')
    print(f'  • Orçamentos processados: {len(orcamentos)}')
    print(f'  • Clientes com histórico: {len(clientes_processados)}')
    print(f'  • Registros atualizados: {precos_atualizados}')
    if erros > 0:
        print(f'  • Erros encontrados: {erros}')
    
    # Mostrar exemplos
    print('\n📋 Exemplos de ranges calculados:')
    exemplos = db.query(models.PrecoClienteProduto).limit(5).all()
    for p in exemplos:
        cliente = db.query(models.Cliente).filter(models.Cliente.id == p.cliente_id).first()
        produto = db.query(models.Produto).filter(models.Produto.id == p.produto_id).first()
        cliente_nome = cliente.nome if cliente else "Desconhecido"
        produto_nome = produto.nome if produto else "Desconhecido"
        print(f'  • {cliente_nome[:30]} → {produto_nome[:30]}')
        print(f'    Min: R$ {p.preco_minimo:.2f} | Max: R$ {p.preco_maximo:.2f} | Vendas: {p.total_vendas}')
    
    print('\n🎉 Ranges de preços agora estão disponíveis no sistema!')
    
except Exception as e:
    db.rollback()
    print(f'\n❌ ERRO FATAL: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()

