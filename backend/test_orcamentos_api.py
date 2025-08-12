#!/usr/bin/env python3

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/users/token"
ORCAMENTOS_URL = f"{BASE_URL}/orcamentos/"

# Credenciais de teste
USERNAME = "test@higiplas.com"
PASSWORD = "test123"

def test_orcamentos_api():
    print("🔍 Testando API de Orçamentos...")
    
    # 1. Fazer login
    print("\n1. Fazendo login...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        login_response = requests.post(LOGIN_URL, data=login_data)
        print(f"Status do login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        print(f"✅ Login realizado com sucesso!")
        
        # 2. Testar endpoint de orçamentos
        print("\n2. Testando endpoint /orcamentos/...")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        orcamentos_response = requests.get(ORCAMENTOS_URL, headers=headers)
        print(f"Status dos orçamentos: {orcamentos_response.status_code}")
        
        if orcamentos_response.status_code == 200:
            orcamentos_data = orcamentos_response.json()
            print(f"✅ Orçamentos obtidos com sucesso!")
            print(f"📊 Total de orçamentos: {len(orcamentos_data)}")
            
            if orcamentos_data:
                print(f"\n📋 Primeiro orçamento:")
                primeiro_orcamento = orcamentos_data[0]
                print(f"   ID: {primeiro_orcamento.get('id')}")
                print(f"   Cliente: {primeiro_orcamento.get('nome_cliente')}")
                print(f"   Status: {primeiro_orcamento.get('status')}")
                print(f"   Data: {primeiro_orcamento.get('data_criacao')}")
            else:
                print("📝 Nenhum orçamento encontrado no banco de dados.")
        else:
            print(f"❌ Erro ao buscar orçamentos: {orcamentos_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_orcamentos_api()