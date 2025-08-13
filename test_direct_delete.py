#!/usr/bin/env python3
"""
Script para testar diretamente o DELETE de clientes, identificando a causa do erro 500.
"""

import requests
import json

# Configurações
BASE_URL = "https://higiplas-system.onrender.com"
EMAIL = "enzo.alverde@gmail.com"
PASSWORD = "enzolilia"

def test_direct_delete():
    print("🔍 Testando DELETE direto de clientes...")
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
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # 2. Criar um cliente de teste para deletar
        print("\n2️⃣ Criando cliente de teste...")
        cliente_data = {
            "nome": "Cliente Teste DELETE",
            "cnpj": "12345678000199",
            "telefone": "11999999999",
            "email": "teste@delete.com",
            "tipo_pessoa": "juridica",
            "endereco": {
                "logradouro": "Rua Teste",
                "numero": "123",
                "complemento": "",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01000-000"
            },
            "empresa_vinculada": "HIGIPLAS"
        }
        
        create_response = requests.post(f"{BASE_URL}/clientes/", headers=headers, json=cliente_data, timeout=15)
        print(f"   Status da criação: {create_response.status_code}")
        
        if create_response.status_code == 200:
            cliente_criado = create_response.json()
            cliente_id = cliente_criado["id"]
            print(f"✅ Cliente criado com ID: {cliente_id}")
            print(f"   Nome: {cliente_criado.get('nome', 'N/A')}")
            print(f"   CNPJ: {cliente_criado.get('cnpj', 'N/A')}")
            
            # 3. Tentar deletar o cliente recém-criado
            print(f"\n3️⃣ Testando DELETE no cliente ID {cliente_id}...")
            delete_response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}", headers=headers, timeout=15)
            print(f"   Status do DELETE: {delete_response.status_code}")
            print(f"   Headers da resposta: {dict(delete_response.headers)}")
            
            if delete_response.status_code == 200:
                print("✅ DELETE realizado com sucesso!")
                print(f"   Resposta: {delete_response.text}")
                
                # Verificar se foi realmente deletado
                print(f"\n4️⃣ Verificando se o cliente foi deletado...")
                get_response = requests.get(f"{BASE_URL}/clientes/{cliente_id}", headers=headers, timeout=15)
                print(f"   Status da verificação: {get_response.status_code}")
                
                if get_response.status_code == 404:
                    print("✅ Cliente foi deletado com sucesso!")
                else:
                    print(f"❌ Cliente ainda existe: {get_response.text}")
                    
            elif delete_response.status_code == 400:
                print("⚠️ Erro 400 - Cliente pode ter orçamentos associados")
                print(f"   Resposta: {delete_response.text}")
                
            elif delete_response.status_code == 401:
                print("❌ Erro 401 - Não autorizado")
                print(f"   Resposta: {delete_response.text}")
                print(f"   Token usado: {headers['Authorization'][:50]}...")
                
            elif delete_response.status_code == 500:
                print("❌ Erro 500 - Erro interno do servidor")
                print(f"   Resposta: {delete_response.text}")
                print("\n🔍 Isso indica um problema no backend de produção.")
                print("   Possíveis causas:")
                print("   - Problema de conexão com o banco de dados")
                print("   - Erro na query SQL")
                print("   - Problema com as dependências do SQLAlchemy")
                print("   - Configuração incorreta do ambiente de produção")
                
            else:
                print(f"❌ Erro inesperado: {delete_response.status_code}")
                print(f"   Resposta: {delete_response.text}")
                
        else:
            print(f"❌ Erro ao criar cliente: {create_response.text}")
            print("   Não foi possível criar cliente de teste para o DELETE")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_direct_delete()
    print("\n=== TESTE CONCLUÍDO ===")