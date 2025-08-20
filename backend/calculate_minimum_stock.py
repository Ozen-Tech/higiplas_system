#!/usr/bin/env python3
"""
Script para calcular estoque mínimo baseado nos dados de vendas dos PDFs.
"""

import json
from datetime import datetime
from collections import defaultdict

def load_sales_data():
    """Carrega os dados de vendas processados dos PDFs"""
    try:
        with open('/Users/ozen/higiplas_system/backend/dados_vendas_processados.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Arquivo de dados de vendas não encontrado!")
        return None

def calculate_minimum_stock(sales_data):
    """Calcula o estoque mínimo baseado no histórico de vendas"""
    product_sales = defaultdict(list)
    
    for sale in sales_data:
        product_key = f"{sale['produto_id']}_{sale['produto_nome']}"
        product_sales[product_key].append({
            'quantidade': sale['quantidade'],
            'cliente': sale['cliente_id'],
            'valor': sale['valor_vendido']
        })
    
    minimum_stock_suggestions = []
    
    for product_key, sales in product_sales.items():
        codigo, produto = product_key.split('_', 1)
        
        total_quantity = sum(sale['quantidade'] for sale in sales)
        num_transactions = len(sales)
        avg_per_transaction = total_quantity / num_transactions if num_transactions > 0 else 0
        max_transaction = max(sale['quantidade'] for sale in sales) if sales else 0
        
        period_months = 3
        monthly_avg = total_quantity / period_months
        
        safety_stock = max_transaction * 0.5
        lead_time_demand = monthly_avg
        minimum_stock = int(lead_time_demand + safety_stock)
        
        minimum_stock = max(minimum_stock, int(max_transaction))
        
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
        })
    
    minimum_stock_suggestions.sort(key=lambda x: x['total_vendido_periodo'], reverse=True)
    
    return minimum_stock_suggestions

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
    
    with open('/Users/ozen/higiplas_system/backend/estoque_minimo_sugerido.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"Relatório de estoque mínimo salvo em: estoque_minimo_sugerido.json")

def main():
    print("=== Calculadora de Estoque Mínimo ===")
    print("Carregando dados de vendas...")
    
    sales_data = load_sales_data()
    if not sales_data:
        return
    
    print(f"Dados carregados: {len(sales_data)} registros de vendas")
    
    print("\nCalculando estoque mínimo...")
    minimum_stock_data = calculate_minimum_stock(sales_data)
    
    save_minimum_stock_report(minimum_stock_data)
    
    print("\n=== TOP 10 PRODUTOS COM MAIOR NECESSIDADE DE ESTOQUE ===")
    for i, product in enumerate(minimum_stock_data[:10], 1):
        print(f"{i:2d}. {product['produto']} (Cód: {product['codigo']})")
        print(f"    Vendido no período: {product['total_vendido_periodo']} unidades")
        print(f"    Estoque mínimo sugerido: {product['estoque_minimo_sugerido']} unidades")
        print(f"    Valor do estoque mínimo: R$ {product['valor_estoque_minimo']:.2f}")
        print(f"    Número de clientes: {len(product['clientes_compradores'])}")
        print()
    
    total_minimum_stock_value = sum(product['valor_estoque_minimo'] for product in minimum_stock_data)
    print(f"\n=== RESUMO GERAL ===")
    print(f"Total de produtos analisados: {len(minimum_stock_data)}")
    print(f"Valor total do estoque mínimo sugerido: R$ {total_minimum_stock_value:.2f}")

if __name__ == "__main__":
    main()