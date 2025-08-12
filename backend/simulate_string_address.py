#!/usr/bin/env python3

import requests
import json
import time
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('.env.local')

# Configurações
BASE_URL = "http://localhost:8000"
EMAIL = "test@higiplas.com"
PASSWORD = "test123"

# Configuração do banco
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def simulate_string_address_problem():
    print("🔍 Simulando problema de endereço como string...")
    
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
    
    # 2. Criar um cliente com endereço como objeto primeiro
    timestamp = str(int(time.time()))
    cnpj_unico = f"123456789{timestamp[-5:]}"
    
    cliente_data = {
        "nome": "Cliente Teste String Address",
        "cpf_cnpj": cnpj_unico,
        "email": "cliente.string.address@teste.com",
        "telefone": "(11) 99999-9999",
        "tipo_pessoa": "JURIDICA",
        "endereco": {
            "logradouro": "Rua Teste",
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
        
        # 3. Modificar o endereço no banco para ser uma string simples (simulando o problema)
        try:
            with engine.connect() as conn:
                # Atualizar o endereço para ser uma string simples como no erro relatado
                endereco_string = "Rua, 2, Recanto dos vinhais, São Luís, MA, 65070011"
                conn.execute(
                    text("UPDATE clientes SET endereco = :endereco WHERE id = :id"),
                    {"endereco": endereco_string, "id": cliente_id}
                )
                conn.commit()
                print(f"✅ Endereço atualizado para string simples: {endereco_string}")
        except Exception as e:
            print(f"❌ Erro ao atualizar endereço: {e}")
            return
        
        # 4. Listar clientes para ver como o frontend vai processar
        list_response = requests.get(f"{BASE_URL}/clientes/", headers=headers)
        print(f"\n📋 Listar clientes Status: {list_response.status_code}")
        
        if list_response.status_code == 200:
            clientes = list_response.json()
            cliente_teste = None
            for cliente in clientes:
                if cliente['id'] == cliente_id:
                    cliente_teste = cliente
                    break
            
            if cliente_teste:
                print(f"✅ Cliente encontrado na lista")
                print(f"Endereço retornado pela API: {cliente_teste.get('endereco', 'N/A')}")
                print(f"Tipo do endereço: {type(cliente_teste.get('endereco', 'N/A'))}")
                
                # 5. Tentar deletar o cliente
                delete_response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
                print(f"\n🗑️ Delete Status: {delete_response.status_code}")
                print(f"Delete Response: {delete_response.text}")
                
                # 6. Verificar se foi realmente deletado
                get_response = requests.get(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
                print(f"\n🔍 Verificar exclusão Status: {get_response.status_code}")
                if get_response.status_code == 404:
                    print("✅ Cliente foi excluído com sucesso!")
                    print("✅ Backend DELETE funcionando mesmo com endereço string!")
                else:
                    print(f"❌ Cliente ainda existe: {get_response.text}")
            else:
                print("❌ Cliente não encontrado na lista")
        else:
            print(f"❌ Erro ao listar clientes: {list_response.text}")
    else:
        print(f"❌ Erro ao criar cliente: {create_response.text}")

if __name__ == "__main__":
    simulate_string_address_problem()