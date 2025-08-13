#!/usr/bin/env python3
"""
Script para testar a conectividade com o banco de dados de produção.
"""

import requests
import json

# Configurações
BASE_URL = "https://higiplas-system.onrender.com"
EMAIL = "enzo.alverde@gmail.com"
PASSWORD = "enzolilia"

def test_production_db():
    print("🔍 Testando conectividade com banco de produção...")
    print(f"🌐 Backend: {BASE_URL}")
    print()
    
    try:
        # 1. Testar endpoint básico
        print("1️⃣ Testando endpoint básico...")
        health_response = requests.get(f"{BASE_URL}/", timeout=15)
        print(f"   Status: {health_response.status_code}")
        print(f"   Resposta: {health_response.text}")
        
        if health_response.status_code != 200:
            print("❌ Backend não está respondendo")
            return
        
        # 2. Fazer login
        print("\n2️⃣ Testando login...")
        login_data = {
            "username": EMAIL,
            "password": PASSWORD
        }
        
        login_response = requests.post(f"{BASE_URL}/users/token", data=login_data, timeout=15)
        print(f"   Status do login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        print(f"✅ Login realizado com sucesso!")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # 3. Testar endpoints simples que não fazem JOIN complexo
        print("\n3️⃣ Testando endpoints simples...")
        
        # Testar usuários
        print("   📋 Testando /users/me...")
        users_response = requests.get(f"{BASE_URL}/users/me", headers=headers, timeout=15)
        print(f"      Status: {users_response.status_code}")
        if users_response.status_code != 200:
            print(f"      Erro: {users_response.text}")
        else:
            print(f"      ✅ Usuário logado: {users_response.json().get('email', 'N/A')}")
        
        # Testar produtos (geralmente funciona)
        print("   📦 Testando /produtos...")
        produtos_response = requests.get(f"{BASE_URL}/produtos", headers=headers, timeout=15)
        print(f"      Status: {produtos_response.status_code}")
        if produtos_response.status_code != 200:
            print(f"      Erro: {produtos_response.text}")
        else:
            produtos = produtos_response.json()
            print(f"      ✅ {len(produtos)} produtos encontrados")
        
        # Testar clientes (onde está o problema)
        print("   👥 Testando /clientes...")
        clientes_response = requests.get(f"{BASE_URL}/clientes", headers=headers, timeout=15)
        print(f"      Status: {clientes_response.status_code}")
        if clientes_response.status_code != 200:
            print(f"      ❌ Erro: {clientes_response.text}")
        else:
            clientes = clientes_response.json()
            print(f"      ✅ {len(clientes)} clientes encontrados")
            
            if clientes:
                cliente = clientes[0]
                print(f"      Primeiro cliente: ID {cliente.get('id')} - {cliente.get('nome', 'N/A')}")
        
        # Testar orçamentos (onde também está dando erro)
        print("   💰 Testando /orcamentos...")
        orcamentos_response = requests.get(f"{BASE_URL}/orcamentos", headers=headers, timeout=15)
        print(f"      Status: {orcamentos_response.status_code}")
        if orcamentos_response.status_code != 200:
            print(f"      ❌ Erro: {orcamentos_response.text}")
        else:
            orcamentos = orcamentos_response.json()
            print(f"      ✅ {len(orcamentos)} orçamentos encontrados")
        
        # 4. Análise dos resultados
        print("\n4️⃣ Análise dos resultados:")
        
        if (clientes_response.status_code == 200 and 
            orcamentos_response.status_code == 500):
            print("   🔍 Clientes funcionam, mas orçamentos não")
            print("   💡 Problema pode estar na query de orçamentos ou JOINs")
        elif (clientes_response.status_code == 200 and 
              orcamentos_response.status_code == 200):
            print("   🔍 Ambos funcionam - problema específico no DELETE")
            print("   💡 Pode ser problema de transação ou constraint")
        elif (clientes_response.status_code == 500 and 
              orcamentos_response.status_code == 500):
            print("   🔍 Ambos falham - problema geral no banco")
            print("   💡 Possível problema de conexão ou configuração")
        else:
            print("   🔍 Padrão misto de erros")
            print("   💡 Investigar logs específicos do Render")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_production_db()
    print("\n=== TESTE DE CONECTIVIDADE CONCLUÍDO ===")