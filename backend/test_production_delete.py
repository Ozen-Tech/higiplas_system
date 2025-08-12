#!/usr/bin/env python3

import requests
import json
import time

# Configurações para produção
BASE_URL = "https://higiplas-system.onrender.com"
EMAIL = "admin@higiplas.com"
PASSWORD = "123456"

def test_production_delete():
    print("🔍 Testando DELETE em produção...")
    print(f"URL Base: {BASE_URL}")
    
    # 1. Fazer login
    login_data = {
        "username": EMAIL,
        "password": PASSWORD
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/users/token", data=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        print("✅ Login realizado com sucesso")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Origin": "https://higiplas-system.vercel.app",  # Simular origem do frontend
            "Referer": "https://higiplas-system.vercel.app/dashboard/clientes"
        }
        
        # 2. Criar um cliente de teste
        timestamp = str(int(time.time()))
        cnpj_unico = f"123456789{timestamp[-5:]}"
        
        cliente_data = {
            "nome": "Cliente Teste PROD DELETE",
            "cpf_cnpj": cnpj_unico,
            "email": "cliente.prod.delete@teste.com",
            "telefone": "(11) 99999-9999",
            "tipo_pessoa": "JURIDICA",
            "endereco": {
                "logradouro": "Rua Teste PROD DELETE",
                "numero": "123",
                "complemento": "Apto 1",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01000-000"
            },
            "empresa_vinculada": "HIGIPLAS"
        }
        
        create_response = requests.post(f"{BASE_URL}/clientes/", headers=headers, json=cliente_data)
        print(f"\n📝 Criar cliente Status: {create_response.status_code}")
        
        if create_response.status_code == 200:
            cliente_criado = create_response.json()
            cliente_id = cliente_criado["id"]
            print(f"✅ Cliente criado com ID: {cliente_id}")
            print(f"CNPJ: {cliente_criado.get('cnpj', 'N/A')}")
            print(f"Endereço: {cliente_criado.get('endereco', 'N/A')}")
            
            # 3. Tentar deletar o cliente (simulando frontend)
            print(f"\n🗑️ Tentando deletar cliente ID {cliente_id}...")
            delete_response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
            print(f"Delete Status: {delete_response.status_code}")
            print(f"Delete Headers: {dict(delete_response.headers)}")
            print(f"Delete Response: {delete_response.text}")
            
            # 4. Verificar se foi realmente deletado
            get_response = requests.get(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
            print(f"\n🔍 Verificar exclusão Status: {get_response.status_code}")
            if get_response.status_code == 404:
                print("✅ Cliente foi excluído com sucesso em produção!")
            else:
                print(f"❌ Cliente ainda existe: {get_response.text}")
        else:
            print(f"❌ Erro ao criar cliente: {create_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_production_delete()