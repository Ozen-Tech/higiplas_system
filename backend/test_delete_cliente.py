#!/usr/bin/env python3

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
EMAIL = "test@higiplas.com"
PASSWORD = "test123"

def test_delete_cliente():
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
    
    # 2. Listar clientes para ver se existem
    clientes_response = requests.get(f"{BASE_URL}/clientes/", headers=headers)
    print(f"\nListar clientes Status: {clientes_response.status_code}")
    
    if clientes_response.status_code == 200:
        clientes = clientes_response.json()
        print(f"Número de clientes encontrados: {len(clientes)}")
        
        if clientes:
            cliente_id = clientes[0]["id"]
            print(f"Primeiro cliente ID: {cliente_id}")
            
            # 3. Tentar deletar o primeiro cliente
            delete_response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
            print(f"\nDelete Status: {delete_response.status_code}")
            print(f"Delete Response: {delete_response.text}")
        else:
            print("Nenhum cliente encontrado para deletar")
    else:
        print(f"Erro ao listar clientes: {clientes_response.text}")

if __name__ == "__main__":
    test_delete_cliente()