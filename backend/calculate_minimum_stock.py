#!/usr/bin/env python3
"""
Script para calcular estoque mínimo baseado nos dados de vendas dos PDFs
e importar clientes automaticamente para o sistema.
"""

import sys
import os
import json
from datetime import datetime
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import text

# Adicionar o diretório do backend ao path
sys.path.append('/Users/ozen/higiplas_system/backend')

from app.db.connection import engine
from app.db.models import Produto, Cliente
from app.crud.cliente import create_cliente
from app.schemas.cliente import ClienteCreate, EmpresaVinculada, StatusPagamento

def load_sales_data():
    """Carrega os dados de vendas processados dos PDFs"""
    try:
        with open('/Users/ozen/higiplas_system/backend/app/dados_vendas_pdf_processados.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Arquivo de dados de vendas não encontrado!")
        return None

def calculate_minimum_stock(sales_data):
    """Calcula o estoque mínimo baseado no histórico de vendas"""
    # Agrupar vendas por produto
    product_sales = defaultdict(list)
    
    for sale in sales_data['sales_data']:
        product_key = f"{sale['codigo']}_{sale['produto']}"
        product_sales[product_key].append({
            'quantidade': sale['quantidade'],
            'cliente': sale['cliente'],
            'empresa': sale['empresa'],
            'valor': sale['valor']
        })
    
    minimum_stock_suggestions = []
    
    for product_key, sales in product_sales.items():
        codigo, produto = product_key.split('_', 1)
        
        # Calcular estatísticas de vendas
        total_quantity = sum(sale['quantidade'] for sale in sales)
        num_transactions = len(sales)
        avg_per_transaction = total_quantity / num_transactions if num_transactions > 0 else 0
        max_transaction = max(sale['quantidade'] for sale in sales) if sales else 0
        
        # Período de análise (3 meses)
        period_months = 3
        monthly_avg = total_quantity / period_months
        
        # Cálculo do estoque mínimo:
        # - Considerar a demanda média mensal
        # - Adicionar margem de segurança baseada na maior transação
        # - Considerar lead time de reposição (assumindo 1 mês)
        safety_stock = max_transaction * 0.5  # 50% da maior transação como margem
        lead_time_demand = monthly_avg  # Demanda durante 1 mês de lead time
        minimum_stock = int(lead_time_demand + safety_stock)
        
        # Estoque mínimo não pode ser menor que a maior transação
        minimum_stock = max(minimum_stock, int(max_transaction))
        
        # Calcular valor médio unitário
        total_value = sum(sale['valor'] for sale in sales)
        avg_unit_price = total_value / total_quantity if total_quantity > 0 else 0
        
        minimum_stock_suggestions.append({
            'codigo': codigo,
            'produto': produto,
            'total_vendido_periodo': total_quantity,
            'num_transacoes': num_transactions,
            'media_por_transacao': round(avg_per_transaction, 2),
            'maior_transacao': max_transaction,
            'media_mensal': round(monthly_avg, 2),
            'estoque_minimo_sugerido': minimum_stock,
            'valor_unitario_medio': round(avg_unit_price, 2),
            'valor_estoque_minimo': round(minimum_stock * avg_unit_price, 2),
            'clientes_compradores': list(set(sale['cliente'] for sale in sales)),
            'empresas_vendedoras': list(set(sale['empresa'] for sale in sales))
        })
    
    # Ordenar por quantidade total vendida (produtos mais importantes primeiro)
    minimum_stock_suggestions.sort(key=lambda x: x['total_vendido_periodo'], reverse=True)
    
    return minimum_stock_suggestions

def extract_unique_clients(sales_data):
    """Extrai clientes únicos dos dados de vendas"""
    clients = set()
    for sale in sales_data['sales_data']:
        clients.add(sale['cliente'])
    
    return sorted(list(clients))

def import_clients_to_database(clients):
    """Importa clientes para o banco de dados"""
    db = Session(engine)
    imported_count = 0
    skipped_count = 0
    
    try:
        for client_name in clients:
            # Verificar se o cliente já existe
            existing_client = db.query(Cliente).filter(
                Cliente.razao_social == client_name
            ).first()
            
            if existing_client:
                print(f"   ⚠️  Cliente já existe: {client_name}")
                skipped_count += 1
                continue
            
            # Criar novo cliente
            client_data = ClienteCreate(
                razao_social=client_name,
                cnpj=None,  # CNPJ não disponível nos PDFs - usar None em vez de string vazia
                email=None,
                telefone=None,
                endereco=None,
                empresa_vinculada=EmpresaVinculada.HIGIPLAS,  # Usar enum
                status_pagamento=StatusPagamento.BOM_PAGADOR  # Usar enum
            )
            
            # Usar a função CRUD para criar o cliente
            # Assumindo empresa_id = 1 (HIGIPLAS)
            new_client = create_cliente(db, client_data, empresa_id=1)
            imported_count += 1
            print(f"   ✅ Cliente importado: {client_name} (ID: {new_client.id})")
            
    except Exception as e:
        print(f"❌ Erro ao importar clientes: {e}")
        db.rollback()
    finally:
        db.close()
    
    print(f"\n📊 Resumo da importação de clientes:")
    print(f"   ✅ Importados: {imported_count}")
    print(f"   ⚠️  Já existiam: {skipped_count}")

def save_minimum_stock_report(minimum_stock_data):
    """Salva o relatório de estoque mínimo em arquivo JSON"""
    report = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_products': len(minimum_stock_data),
            'calculation_method': 'Historical sales analysis with safety stock',
            'period_analyzed': '3 months (May-July 2025)',
            'lead_time_assumption': '1 month'
        },
        'minimum_stock_suggestions': minimum_stock_data
    }
    
    with open('/Users/ozen/higiplas_system/backend/app/estoque_minimo_sugerido.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"Relatório de estoque mínimo salvo em: estoque_minimo_sugerido.json")

def main():
    print("=== Calculadora de Estoque Mínimo e Importador de Clientes ===")
    print("Carregando dados de vendas...")
    
    # Carregar dados de vendas
    sales_data = load_sales_data()
    if not sales_data:
        return
    
    print(f"Dados carregados: {sales_data['metadata']['total_sales_records']} registros de vendas")
    
    # Calcular estoque mínimo
    print("\nCalculando estoque mínimo...")
    minimum_stock_data = calculate_minimum_stock(sales_data)
    
    # Salvar relatório
    save_minimum_stock_report(minimum_stock_data)
    
    # Mostrar resumo dos top 10 produtos
    print("\n=== TOP 10 PRODUTOS COM MAIOR NECESSIDADE DE ESTOQUE ===")
    for i, product in enumerate(minimum_stock_data[:10], 1):
        print(f"{i:2d}. {product['produto']} (Cód: {product['codigo']})")
        print(f"    Vendido no período: {product['total_vendido_periodo']} unidades")
        print(f"    Estoque mínimo sugerido: {product['estoque_minimo_sugerido']} unidades")
        print(f"    Valor do estoque mínimo: R$ {product['valor_estoque_minimo']:.2f}")
        print(f"    Número de clientes: {len(product['clientes_compradores'])}")
        print()
    
    # Extrair e importar clientes
    print("\n=== IMPORTAÇÃO DE CLIENTES ===")
    clients = extract_unique_clients(sales_data)
    print(f"Encontrados {len(clients)} clientes únicos nas notas fiscais")
    
    print("\nImportando clientes para o banco de dados...")
    import_clients_to_database(clients)
    
    # Calcular valor total do estoque mínimo
    total_minimum_stock_value = sum(product['valor_estoque_minimo'] for product in minimum_stock_data)
    print(f"\n=== RESUMO GERAL ===")
    print(f"Total de produtos analisados: {len(minimum_stock_data)}")
    print(f"Valor total do estoque mínimo sugerido: R$ {total_minimum_stock_value:.2f}")
    print(f"Clientes únicos encontrados: {len(clients)}")

if __name__ == "__main__":
    main()