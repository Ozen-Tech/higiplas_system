#!/usr/bin/env python3

import requests
import json
import time

# Configurações
BASE_URL = "http://localhost:8000"
EMAIL = "test@higiplas.com"
PASSWORD = "test123"

def create_and_delete_cliente():
    # 1. Fazer login
    login_data = {
        "username": EMAIL,
        "password": PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/users/token", data=login_data)
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"Erro no login: {login_response.text}")
        return
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 2. Criar um cliente de teste com CNPJ único
    timestamp = str(int(time.time()))
    cnpj_unico = f"123456789{timestamp[-5:]}"  # Usa os últimos 5 dígitos do timestamp
    
    cliente_data = {
        "nome": "Cliente Teste DELETE",
        "cpf_cnpj": cnpj_unico,
        "email": "cliente.delete@teste.com",
        "telefone": "(11) 99999-9999",
        "tipo_pessoa": "JURIDICA",
        "endereco": {
            "logradouro": "Rua Teste DELETE",
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
    print(f"\nCriar cliente Status: {create_response.status_code}")
    
    if create_response.status_code == 200:
        cliente_criado = create_response.json()
        cliente_id = cliente_criado["id"]
        print(f"Cliente criado com ID: {cliente_id}")
        print(f"CNPJ: {cliente_criado.get('cnpj', 'N/A')}")
        print(f"Endereço: {cliente_criado.get('endereco', 'N/A')}")
        
        # 3. Tentar deletar o cliente
        delete_response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
        print(f"\nDelete Status: {delete_response.status_code}")
        print(f"Delete Response: {delete_response.text}")
        
        # 4. Verificar se foi realmente deletado
        get_response = requests.get(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
        print(f"\nVerificar exclusão Status: {get_response.status_code}")
        if get_response.status_code == 404:
            print("✅ Cliente foi excluído com sucesso!")
            print("✅ Endpoint DELETE está funcionando corretamente!")
        else:
            print(f"❌ Cliente ainda existe: {get_response.text}")
    else:
        print(f"Erro ao criar cliente: {create_response.text}")

if __name__ == "__main__":
    create_and_delete_cliente()