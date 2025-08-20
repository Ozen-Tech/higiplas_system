#!/usr/bin/env python3
"""
Script para atualizar o estoque mínimo no banco de dados e importar novos clientes.
"""

import sys
import json
from sqlalchemy.orm import Session

# Adicionar o diretório do backend ao path
sys.path.append('/Users/ozen/higiplas_system/backend')

from sqlalchemy import create_engine
from app.db.models import Produto, Cliente
from app.crud.cliente import create_cliente
from app.schemas.cliente import ClienteCreate, EmpresaVinculada, StatusPagamento
from app.core.config import settings

# --- Configuração de Conexão para Execução Local ---
# Usar exatamente a mesma URL que o SQLAlchemy usa
print(f"Usando DATABASE_URL: {settings.DATABASE_URL}")
engine = create_engine(settings.DATABASE_URL)
# ----------------------------------------------------

def load_minimum_stock_data():
    """Carrega os dados de estoque mínimo do arquivo JSON."""
    try:
        with open('/Users/ozen/higiplas_system/backend/estoque_minimo_sugerido.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Arquivo de estoque mínimo sugerido não encontrado!")
        return None

def update_minimum_stock_in_db(minimum_stock_data):
    """Atualiza o estoque mínimo dos produtos no banco de dados."""
    db = Session(engine)
    updated_count = 0
    not_found_count = 0
    
    try:
        for item in minimum_stock_data['minimum_stock_suggestions']:
            produto = db.query(Produto).filter(Produto.codigo == item['codigo']).first()
            if produto:
                produto.estoque_minimo = item['estoque_minimo_sugerido']
                updated_count += 1
            else:
                not_found_count += 1
        db.commit()
    except Exception as e:
        print(f"Erro ao atualizar o estoque mínimo: {e}")
        db.rollback()
    finally:
        db.close()
        
    print(f"\nResumo da atualização de estoque mínimo:")
    print(f"  - Atualizados: {updated_count}")
    print(f"  - Não encontrados: {not_found_count}")

def extract_unique_clients_from_sales():
    """Extrai clientes únicos dos dados de vendas processados."""
    try:
        with open('/Users/ozen/higiplas_system/backend/dados_vendas_processados.json', 'r', encoding='utf-8') as f:
            sales_data = json.load(f)
    except FileNotFoundError:
        print("Arquivo de dados de vendas não encontrado!")
        return []
        
    clients = set()
    for sale in sales_data:
        clients.add(sale['cliente_id'])
    
    return sorted(list(clients))

def import_clients_to_database(clients):
    """Importa clientes para o banco de dados."""
    db = Session(engine)
    imported_count = 0
    skipped_count = 0
    
    try:
        for client_id in clients:
            existing_client = db.query(Cliente).filter(Cliente.id == client_id).first()
            if existing_client:
                skipped_count += 1
                continue
            
            # Para este exemplo, estamos criando um cliente com informações básicas
            # Em um cenário real, você pode querer buscar mais detalhes do cliente
            client_data = ClienteCreate(
                razao_social=f"Cliente {client_id}",
                cnpj=None,
                email=None,
                telefone=None,
                endereco=None,
                empresa_vinculada=EmpresaVinculada.HIGIPLAS,
                status_pagamento=StatusPagamento.BOM_PAGADOR
            )
            create_cliente(db, client_data, empresa_id=1)
            imported_count += 1
            
    except Exception as e:
        print(f"Erro ao importar clientes: {e}")
        db.rollback()
    finally:
        db.close()
        
    print(f"\nResumo da importação de clientes:")
    print(f"  - Importados: {imported_count}")
    print(f"  - Já existiam: {skipped_count}")

def main():
    print("=== Atualizador de Estoque Mínimo e Importador de Clientes ===")
    
    minimum_stock_data = load_minimum_stock_data()
    if not minimum_stock_data:
        return
        
    print("\nAtualizando estoque mínimo no banco de dados...")
    update_minimum_stock_in_db(minimum_stock_data)
    
    print("\nExtraindo clientes únicos dos dados de vendas...")
    clients = extract_unique_clients_from_sales()
    print(f"Encontrados {len(clients)} clientes únicos.")
    
    print("\nImportando novos clientes para o banco de dados...")
    import_clients_to_database(clients)

if __name__ == "__main__":
    main()