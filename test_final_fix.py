#!/usr/bin/env python3
"""
Script para testar se a correção final do erro 500 em clientes foi aplicada.
Testa GET e DELETE de clientes após a correção dos relacionamentos problemáticos.
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "https://higiplas-system.onrender.com"

def get_auth_token():
    """Obtém token de autenticação."""
    login_data = {
        "username": "enzo.alverde@gmail.com",
        "password": "enzolilia"
    }
    
    response = requests.post(f"{BASE_URL}/users/token", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Erro no login: {response.status_code} - {response.text}")
        return None

def test_get_cliente(token, cliente_id):
    """Testa GET de um cliente específico."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 Testando GET /clientes/{cliente_id}...")
    response = requests.get(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        cliente_data = response.json()
        print(f"✅ Cliente encontrado: {cliente_data.get('razao_social', 'N/A')}")
        print(f"   - ID: {cliente_data.get('id')}")
        print(f"   - CNPJ: {cliente_data.get('cnpj', 'N/A')}")
        print(f"   - Orçamentos: {len(cliente_data.get('orcamentos', []))} (deve ser 0 após correção)")
        print(f"   - Histórico pagamentos: {len(cliente_data.get('historico_pagamentos', []))}")
        return True
    else:
        print(f"❌ Erro: {response.text}")
        return False

def test_delete_cliente(token, cliente_id):
    """Testa DELETE de um cliente."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🗑️ Testando DELETE /clientes/{cliente_id}...")
    response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Cliente excluído com sucesso")
        print(f"   Mensagem: {result.get('message', 'N/A')}")
        return True
    else:
        print(f"❌ Erro: {response.text}")
        return False

def create_test_cliente(token):
    """Cria um cliente de teste."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Gera um CNPJ único baseado no timestamp
    timestamp = int(datetime.now().timestamp())
    cnpj_unico = f"{timestamp:011d}0001{(timestamp % 100):02d}"
    
    cliente_data = {
        "nome": f"Cliente Teste Final {timestamp}",
        "email": f"teste.final{timestamp}@exemplo.com",
        "telefone": "(11) 99999-9999",
        "cpf_cnpj": cnpj_unico,
        "tipo_pessoa": "juridica",
        "observacoes": "Cliente criado para teste final",
        "empresa_vinculada": "HIGIPLAS"
    }
    
    print("\n➕ Criando cliente de teste...")
    response = requests.post(f"{BASE_URL}/clientes/", json=cliente_data, headers=headers)
    
    if response.status_code == 200:
        cliente = response.json()
        print(f"✅ Cliente criado: ID {cliente['id']}")
        return cliente['id']
    else:
        print(f"❌ Erro ao criar cliente: {response.status_code} - {response.text}")
        return None

def main():
    print("🚀 Testando correção final do erro 500 em clientes...")
    print("⏳ Aguardando deploy do Render (120 segundos)...")
    time.sleep(120)
    
    # 1. Fazer login
    print("\n🔐 Fazendo login...")
    token = get_auth_token()
    if not token:
        print("❌ Falha no login. Abortando teste.")
        return
    
    print("✅ Login realizado com sucesso")
    
    # 2. Criar cliente de teste
    cliente_id = create_test_cliente(token)
    if not cliente_id:
        print("❌ Falha ao criar cliente de teste. Abortando.")
        return
    
    # 3. Testar GET do cliente (que estava falhando)
    get_success = test_get_cliente(token, cliente_id)
    
    # 4. Testar DELETE do cliente (que também estava falhando)
    if get_success:
        delete_success = test_delete_cliente(token, cliente_id)
        
        if delete_success:
            print("\n🎉 SUCESSO! Ambos GET e DELETE funcionaram corretamente!")
            print("✅ A correção foi aplicada com sucesso no ambiente de produção.")
        else:
            print("\n⚠️ GET funcionou, mas DELETE ainda tem problemas.")
    else:
        print("\n❌ GET ainda não está funcionando. A correção pode não ter sido aplicada.")
    
    # 5. Teste adicional: verificar se ainda conseguimos listar clientes
    print("\n📋 Testando listagem de clientes...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/clientes/", headers=headers)
    
    if response.status_code == 200:
        clientes = response.json()
        print(f"✅ Listagem funcionando: {len(clientes)} clientes encontrados")
    else:
        print(f"❌ Erro na listagem: {response.status_code}")

if __name__ == "__main__":
    main()