#!/usr/bin/env python3
"""
Script para testar o problema de autenticação 401 no DELETE de clientes em produção.
"""

import requests
import json

# Configurações
BASE_URL = "https://higiplas-system.onrender.com"
EMAIL = "enzo.alverde@gmail.com"
PASSWORD = "enzolilia"

def test_production_auth_issue():
    print("🔍 Testando problema de autenticação 401 no DELETE de clientes...")
    print(f"🌐 Backend: {BASE_URL}")
    print(f"👤 Usuário: {EMAIL}")
    print()
    
    # 1. Fazer login
    print("1️⃣ Fazendo login...")
    login_data = {
        "username": EMAIL,
        "password": PASSWORD
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/users/token", data=login_data, timeout=15)
        print(f"   Status do login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        print(f"✅ Login realizado com sucesso!")
        print(f"   Token: {access_token[:20]}...")
        
        # 2. Testar GET /clientes para verificar se há clientes
        print("\n2️⃣ Listando clientes...")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        clientes_response = requests.get(f"{BASE_URL}/clientes", headers=headers, timeout=15)
        print(f"   Status da listagem: {clientes_response.status_code}")
        
        if clientes_response.status_code == 200:
            clientes = clientes_response.json()
            print(f"✅ {len(clientes)} clientes encontrados")
            
            if clientes:
                cliente_teste = clientes[0]
                cliente_id = cliente_teste["id"]
                print(f"   Primeiro cliente: ID {cliente_id} - {cliente_teste.get('nome', 'N/A')}")
                
                # 3. Testar DELETE no primeiro cliente
                print(f"\n3️⃣ Testando DELETE no cliente ID {cliente_id}...")
                delete_response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}", headers=headers, timeout=15)
                print(f"   Status do DELETE: {delete_response.status_code}")
                
                if delete_response.status_code == 200:
                    print("✅ DELETE realizado com sucesso!")
                    print(f"   Resposta: {delete_response.text}")
                elif delete_response.status_code == 401:
                    print("❌ Erro 401 Unauthorized no DELETE!")
                    print(f"   Resposta: {delete_response.text}")
                    print("\n🔍 Verificando detalhes do token...")
                    print(f"   Authorization header: {headers['Authorization'][:50]}...")
                    
                    # Testar se o token ainda é válido fazendo outro GET
                    print("\n4️⃣ Testando se o token ainda é válido...")
                    test_response = requests.get(f"{BASE_URL}/clientes", headers=headers, timeout=15)
                    print(f"   Status do GET após DELETE: {test_response.status_code}")
                    
                    if test_response.status_code == 200:
                        print("✅ Token ainda é válido - problema específico no DELETE")
                    else:
                        print("❌ Token inválido - problema de autenticação geral")
                        
                elif delete_response.status_code == 400:
                    print("⚠️ Erro 400 - Cliente pode ter orçamentos associados")
                    print(f"   Resposta: {delete_response.text}")
                else:
                    print(f"❌ Erro inesperado: {delete_response.status_code}")
                    print(f"   Resposta: {delete_response.text}")
            else:
                print("⚠️ Nenhum cliente encontrado para testar DELETE")
        else:
            print(f"❌ Erro ao listar clientes: {clientes_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_production_auth_issue()
    print("\n=== TESTE CONCLUÍDO ===")