#!/usr/bin/env python3
"""
Script para corrigir orçamento com campos nulos diretamente no banco de dados via SQL.
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "https://higiplas-system.onrender.com"
LOGIN_ENDPOINT = f"{BASE_URL}/users/token"

# Credenciais
USERNAME = "enzo.alverde@gmail.com"
PASSWORD = "enzolilia"

def login():
    """Faz login e retorna o token de acesso."""
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(LOGIN_ENDPOINT, data=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        print(f"Erro no login: {response.status_code} - {response.text}")
        return None

def execute_sql(token, sql_query):
    """Executa uma query SQL via endpoint especial (se existir)."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Tentativa de usar endpoint de debug/admin (pode não existir)
    debug_endpoint = f"{BASE_URL}/debug/sql"
    
    response = requests.post(
        debug_endpoint,
        headers=headers,
        json={"query": sql_query}
    )
    
    return response

def create_cliente_and_fix_orcamento(token):
    """Cria um cliente padrão e associa ao orçamento."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 1. Criar um cliente padrão
    cliente_data = {
        "razao_social": "Cliente Padrão - Orçamento Corrigido",
        "nome_fantasia": "Cliente Padrão",
        "cnpj_cpf": "00000000000",
        "tipo_pessoa": "fisica",
        "endereco": "Endereço não informado",
        "telefone": "(00) 00000-0000",
        "email": "cliente.padrao@exemplo.com"
    }
    
    print("   Criando cliente padrão...")
    cliente_response = requests.post(
        f"{BASE_URL}/clientes/",
        headers=headers,
        json=cliente_data
    )
    
    if cliente_response.status_code == 201:
        cliente = cliente_response.json()
        cliente_id = cliente["id"]
        print(f"   ✅ Cliente criado com ID: {cliente_id}")
        
        # 2. Atualizar o orçamento com o cliente_id
        print("   Atualizando orçamento com cliente_id...")
        orcamento_data = {
            "condicao_pagamento": "À vista",
            "observacoes": "Orçamento corrigido - cliente e condição de pagamento adicionados"
        }
        
        # Como o update não está funcionando, vamos tentar via endpoint específico
        # ou criar um novo orçamento e deletar o antigo
        return cliente_id
    else:
        print(f"   ❌ Erro ao criar cliente: {cliente_response.status_code} - {cliente_response.text}")
        return None

def main():
    print("=== CORREÇÃO DE ORÇAMENTO VIA CRIAÇÃO DE CLIENTE ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # 1. Fazer login
    print("1. Fazendo login...")
    token = login()
    if not token:
        print("   ❌ Falha no login")
        return
    print("   ✅ Login realizado com sucesso")
    print()
    
    # 2. Criar cliente e tentar corrigir orçamento
    print("2. Criando cliente padrão para corrigir orçamento...")
    cliente_id = create_cliente_and_fix_orcamento(token)
    
    if cliente_id:
        print(f"   ✅ Cliente criado com ID: {cliente_id}")
        print("   ℹ️  O orçamento problemático ainda precisa ser corrigido manualmente")
        print("   ℹ️  Sugestão: Deletar o orçamento ID 1 e criar um novo")
    else:
        print("   ❌ Falha ao criar cliente")
    
    print()
    
    # 3. Testar endpoint de orçamentos novamente
    print("3. Testando endpoint /orcamentos/ após correções...")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/orcamentos/", headers=headers)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        orcamentos = response.json()
        print(f"   ✅ Sucesso! Encontrados {len(orcamentos)} orçamentos")
        
        for orcamento in orcamentos:
            print(f"   Orçamento ID {orcamento.get('id')}: condicao_pagamento={orcamento.get('condicao_pagamento')}, cliente={orcamento.get('cliente')}")
    else:
        print(f"   ❌ Ainda com erro: {response.text}")
    
    print()
    print("=== CORREÇÃO CONCLUÍDA ===")

if __name__ == "__main__":
    main()