#!/usr/bin/env python3
"""
Script para analisar produtos no banco de produção
"""

import psycopg2
import json
from collections import Counter
import re

# Configurações do banco de produção
PROD_DB_CONFIG = {
    'host': 'dpg-d1kpjbfdiees73ern72g-a.oregon-postgres.render.com',
    'database': 'higiplas_postgres_prod',
    'user': 'higiplas_postgres_prod_user',
    'password': 'T4UPwBadMURnW5EPOcAsogYUARNgWWXj',
    'port': 5432
}

def connect_to_prod_db():
    """Conecta ao banco de produção"""
    try:
        conn = psycopg2.connect(**PROD_DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def analyze_products():
    """Analisa os produtos no banco de produção"""
    conn = connect_to_prod_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Buscar todos os produtos
        cursor.execute("""
            SELECT id, nome, codigo, categoria, descricao, preco_venda, unidade_medida
            FROM produtos 
            ORDER BY nome
        """)
        
        produtos = cursor.fetchall()
        
        print(f"\n=== ANÁLISE DE PRODUTOS NO BANCO DE PRODUÇÃO ===")
        print(f"Total de produtos: {len(produtos)}")
        print("\n=== PRIMEIROS 20 PRODUTOS ===")
        
        produtos_data = []
        categorias = []
        unidades = []
        
        for i, produto in enumerate(produtos[:20]):
            id_prod, nome, codigo, categoria, descricao, preco, unidade = produto
            print(f"{i+1:2d}. {nome} (Código: {codigo}) - {categoria} - {unidade}")
            
            produtos_data.append({
                'id': id_prod,
                'nome': nome,
                'codigo': codigo,
                'categoria': categoria,
                'descricao': descricao,
                'preco_venda': float(preco) if preco else 0,
                'unidade_medida': unidade
            })
            
            if categoria:
                categorias.append(categoria)
            if unidade:
                unidades.append(unidade)
        
        # Análise de categorias
        print("\n=== CATEGORIAS MAIS COMUNS ===")
        categoria_counts = Counter(cat for _, _, _, cat, _, _, _ in produtos if cat)
        for categoria, count in categoria_counts.most_common(10):
            print(f"{categoria}: {count} produtos")
        
        # Análise de unidades de medida
        print("\n=== UNIDADES DE MEDIDA MAIS COMUNS ===")
        unidade_counts = Counter(un for _, _, _, _, _, _, un in produtos if un)
        for unidade, count in unidade_counts.most_common(10):
            print(f"{unidade}: {count} produtos")
        
        # Análise de padrões de nomes
        print("\n=== ANÁLISE DE PADRÕES DE NOMES ===")
        nomes = [nome for _, nome, _, _, _, _, _ in produtos if nome]
        
        # Palavras mais comuns nos nomes
        todas_palavras = []
        for nome in nomes:
            # Remove caracteres especiais e divide em palavras
            palavras = re.findall(r'\b\w+\b', nome.upper())
            todas_palavras.extend(palavras)
        
        palavra_counts = Counter(todas_palavras)
        print("\nPalavras mais comuns nos nomes dos produtos:")
        for palavra, count in palavra_counts.most_common(15):
            if len(palavra) > 2:  # Ignora palavras muito pequenas
                print(f"{palavra}: {count} ocorrências")
        
        # Salvar dados para análise posterior
        with open('/Users/ozen/higiplas_system/backend/produtos_producao.json', 'w', encoding='utf-8') as f:
            json.dump({
                'total_produtos': len(produtos),
                'produtos_amostra': produtos_data,
                'categorias': dict(categoria_counts.most_common()),
                'unidades_medida': dict(unidade_counts.most_common()),
                'palavras_comuns': dict(palavra_counts.most_common(50))
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nDados salvos em produtos_producao.json")
        
    except Exception as e:
        print(f"Erro ao analisar produtos: {e}")
    finally:
        conn.close()

def search_similar_products(search_term, limit=10):
    """Busca produtos similares por nome"""
    conn = connect_to_prod_db()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        # Busca usando ILIKE para similaridade básica
        cursor.execute("""
            SELECT id, nome, codigo, categoria, unidade_medida, preco_venda
            FROM produtos 
            WHERE UPPER(nome) LIKE UPPER(%s)
            ORDER BY 
                CASE 
                    WHEN UPPER(nome) = UPPER(%s) THEN 1
                    WHEN UPPER(nome) LIKE UPPER(%s) THEN 2
                    ELSE 3
                END,
                nome
            LIMIT %s
        """, (f'%{search_term}%', search_term, f'{search_term}%', limit))
        
        produtos = cursor.fetchall()
        
        result = []
        for produto in produtos:
            id_prod, nome, codigo, categoria, unidade, preco = produto
            result.append({
                'id': id_prod,
                'nome': nome,
                'codigo': codigo,
                'categoria': categoria,
                'unidade_medida': unidade,
                'preco_venda': float(preco) if preco else 0
            })
        
        return result
        
    except Exception as e:
        print(f"Erro ao buscar produtos similares: {e}")
        return []
    finally:
        conn.close()

if __name__ == "__main__":
    print("Conectando ao banco de produção...")
    analyze_products()
    
    # Teste de busca por similaridade
    print("\n=== TESTE DE BUSCA POR SIMILARIDADE ===")
    test_terms = ["LUVA", "NITRILICA", "PRETA", "ALCOOL", "GEL"]
    
    for term in test_terms:
        print(f"\nBuscando por '{term}':")
        similares = search_similar_products(term, 5)
        for produto in similares:
            print(f"  - {produto['nome']} (ID: {produto['id']})")