#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("DATABASE_URL not found in environment")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Check products data
        result = conn.execute(text("""
            SELECT nome, codigo, quantidade_em_estoque, estoque_minimo, 
                   preco_venda, data_validade 
            FROM produtos 
            LIMIT 5
        """))
        
        products = result.fetchall()
        print(f"Found {len(products)} products:")
        print()
        
        for product in products:
            print(f"Nome: {product[0]}")
            print(f"Código: {product[1]}")
            print(f"Estoque: {product[2]}")
            print(f"Estoque Mínimo: {product[3]}")
            print(f"Preço Venda: {product[4]}")
            print(f"Data Validade: {product[5]}")
            print("-" * 40)
            
except Exception as e:
    print(f"Error: {e}")