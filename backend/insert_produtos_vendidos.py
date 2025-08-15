#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.pdf_processor import PDFSalesProcessor
from app.db.connection import SessionLocal
from app.db.models import ProdutoMaisVendido, Produto
from datetime import datetime

def main():
    print("🔄 Processando PDFs de vendas...")
    
    # Processa os PDFs
    processor = PDFSalesProcessor()
    result = processor.process_all_pdfs()
    
    if not result['sales_data']:
        print('❌ Nenhum dado foi extraído dos PDFs')
        return
    
    print(f"✅ Extraídos {len(result['sales_data'])} registros de vendas")
    
    # Conecta ao banco
    session = SessionLocal()
    
    try:
        # Limpa dados antigos
        deleted_count = session.query(ProdutoMaisVendido).delete()
        print(f"🗑️ Removidos {deleted_count} registros antigos")
        
        # Agrupa por produto e soma as quantidades
        produtos_agrupados = {}
        for venda in result['sales_data']:
            produto = venda.get('produto', 'N/A')
            quantidade = venda.get('quantidade', 0)
            valor = venda.get('valor', 0)
            empresa = venda.get('empresa', 'HIGIPLAS')
            
            key = f'{produto}_{empresa}'
            if key in produtos_agrupados:
                produtos_agrupados[key]['quantidade'] += quantidade
                produtos_agrupados[key]['valor'] += valor
                produtos_agrupados[key]['numero_vendas'] += 1
            else:
                produtos_agrupados[key] = {
                    'produto': produto,
                    'empresa': empresa,
                    'quantidade': quantidade, 
                    'valor': valor,
                    'numero_vendas': 1
                }
        
        print(f"📊 Agrupados em {len(produtos_agrupados)} produtos únicos")
        
        # Cria produtos temporários e insere os produtos mais vendidos
        empresa_id_map = {'HIGIPLAS': 1, 'HIGITEC': 2}
        
        for i, (key, dados) in enumerate(produtos_agrupados.items()):
            # Cria um produto temporário
            produto_temp = Produto(
                nome=dados['produto'][:100],  # Limita o nome a 100 caracteres
                codigo=f"TEMP_{i+1:04d}",
                categoria="Extraído do PDF",
                preco_venda=dados['valor'] / dados['quantidade'] if dados['quantidade'] > 0 else 0,
                unidade_medida="UN",
                empresa_id=empresa_id_map.get(dados['empresa'], 1)
            )
            session.add(produto_temp)
            session.flush()  # Para obter o ID do produto
            
            # Cria o registro de produto mais vendido
            produto_mais_vendido = ProdutoMaisVendido(
                produto_id=produto_temp.id,
                ano=2025,
                quantidade_vendida=int(dados['quantidade']),
                valor_total_vendido=float(dados['valor']),
                numero_vendas=dados['numero_vendas'],
                empresa_id=empresa_id_map.get(dados['empresa'], 1),
                ultima_atualizacao=datetime.now()
            )
            session.add(produto_mais_vendido)
        
        session.commit()
        print(f'✅ Inseridos {len(produtos_agrupados)} produtos mais vendidos no banco de dados!')
        
        # Mostra os top 10
        sorted_produtos = sorted(produtos_agrupados.items(), key=lambda x: x[1]['quantidade'], reverse=True)
        print('\n=== TOP 10 PRODUTOS MAIS VENDIDOS INSERIDOS ===')
        for i, (key, dados) in enumerate(sorted_produtos[:10]):
            print(f'{i+1}. {dados["produto"]} ({dados["empresa"]}) - Qtd: {dados["quantidade"]} - Valor: R$ {dados["valor"]:.2f}')
            
    except Exception as e:
        session.rollback()
        print(f'❌ Erro ao inserir dados: {e}')
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()