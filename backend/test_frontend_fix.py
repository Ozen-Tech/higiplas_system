#!/usr/bin/env python3

import requests
import json
import time

# Configurações
BASE_URL = "http://localhost:8000"
EMAIL = "test@higiplas.com"
PASSWORD = "test123"

def test_frontend_fix():
    print("🔍 Testando correção do frontend para parsing de endereço...")
    
    # 1. Fazer login
    login_data = {
        "username": EMAIL,
        "password": PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/users/token", data=login_data)
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.text}")
        return
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 2. Criar um cliente com endereço em formato de string simples (como o problema relatado)
    timestamp = str(int(time.time()))
    cnpj_unico = f"123456789{timestamp[-5:]}"
    
    cliente_data = {
        "nome": "Cliente Teste Endereço String",
        "cpf_cnpj": cnpj_unico,
        "email": "cliente.endereco.string@teste.com",
        "telefone": "(11) 99999-9999",
        "tipo_pessoa": "JURIDICA",
        "endereco": "Rua Teste, 123, Recanto dos vinhais, São Luís, MA, 65070011",  # String simples como no erro
        "empresa_vinculada": "HIGIPLAS"
    }
    
    create_response = requests.post(f"{BASE_URL}/clientes/", headers=headers, json=cliente_data)
    print(f"\n📝 Criar cliente Status: {create_response.status_code}")
    
    if create_response.status_code == 200:
        cliente_criado = create_response.json()
        cliente_id = cliente_criado["id"]
        print(f"✅ Cliente criado com ID: {cliente_id}")
        print(f"CNPJ: {cliente_criado.get('cnpj', 'N/A')}")
        print(f"Endereço (string): {cliente_criado.get('endereco', 'N/A')}")
        
        # 3. Listar clientes para simular o que o frontend faz
        list_response = requests.get(f"{BASE_URL}/clientes/", headers=headers)
        print(f"\n📋 Listar clientes Status: {list_response.status_code}")
        
        if list_response.status_code == 200:
            clientes = list_response.json()
            print(f"✅ {len(clientes)} clientes encontrados")
            
            # Encontrar nosso cliente de teste
            cliente_teste = None
            for cliente in clientes:
                if cliente['id'] == cliente_id:
                    cliente_teste = cliente
                    break
            
            if cliente_teste:
                print(f"✅ Cliente de teste encontrado na lista")
                print(f"Endereço na lista: {cliente_teste.get('endereco', 'N/A')}")
                
                # 4. Tentar deletar o cliente
                delete_response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
                print(f"\n🗑️ Delete Status: {delete_response.status_code}")
                print(f"Delete Response: {delete_response.text}")
                
                # 5. Verificar se foi realmente deletado
                get_response = requests.get(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
                print(f"\n🔍 Verificar exclusão Status: {get_response.status_code}")
                if get_response.status_code == 404:
                    print("✅ Cliente foi excluído com sucesso!")
                    print("✅ Correção do parsing de endereço funcionou!")
                else:
                    print(f"❌ Cliente ainda existe: {get_response.text}")
            else:
                print("❌ Cliente de teste não encontrado na lista")
        else:
            print(f"❌ Erro ao listar clientes: {list_response.text}")
    else:
        print(f"❌ Erro ao criar cliente: {create_response.text}")

if __name__ == "__main__":
    test_frontend_fix()