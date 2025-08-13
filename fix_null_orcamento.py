#!/usr/bin/env python3
"""
Script para corrigir orçamento com campos nulos no banco de dados.
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "https://higiplas-system.onrender.com"
LOGIN_ENDPOINT = f"{BASE_URL}/users/token"
ORCAMENTO_ENDPOINT = f"{BASE_URL}/orcamentos"

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

def update_orcamento(token, orcamento_id, update_data):
    """Atualiza um orçamento específico."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.put(
        f"{ORCAMENTO_ENDPOINT}/{orcamento_id}",
        headers=headers,
        json=update_data
    )
    
    return response

def main():
    print("=== CORREÇÃO DE ORÇAMENTO COM CAMPOS NULOS ===")
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
    
    # 2. Atualizar orçamento ID 1
    print("2. Atualizando orçamento ID 1...")
    
    # Dados para corrigir o orçamento
    update_data = {
        "condicao_pagamento": "À vista",  # Valor padrão
        "observacoes": "Orçamento corrigido - campos nulos preenchidos automaticamente"
    }
    
    response = update_orcamento(token, 1, update_data)
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Orçamento atualizado com sucesso!")
        orcamento_data = response.json()
        print(f"   Condição de pagamento: {orcamento_data.get('condicao_pagamento')}")
        print(f"   Cliente ID: {orcamento_data.get('cliente_id')}")
    else:
        print(f"   ❌ Erro ao atualizar orçamento: {response.text}")
    
    print()
    print("=== CORREÇÃO CONCLUÍDA ===")

if __name__ == "__main__":
    main()