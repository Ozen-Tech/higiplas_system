#!/usr/bin/env python3
"""
Script para investigar mais profundamente o erro 500 no DELETE de clientes.
Vamos testar diferentes cenários para identificar a causa real.
"""

import requests
import json

# Configurações
BASE_URL = "https://higiplas-system.onrender.com"
EMAIL = "enzo.alverde@gmail.com"
PASSWORD = "enzolilia"

def get_auth_token():
    """Obtém token de autenticação."""
    login_data = {
        "username": EMAIL,
        "password": PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/users/token", data=login_data, timeout=15)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Erro no login: {response.text}")
        return None

def test_basic_endpoints(token):
    """Testa endpoints básicos para verificar se o problema é geral."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔍 Testando endpoints básicos...")
    
    # Teste 1: Listar clientes
    try:
        response = requests.get(f"{BASE_URL}/clientes", headers=headers, timeout=15)
        print(f"   GET /clientes: {response.status_code}")
        if response.status_code == 200:
            clientes = response.json()
            print(f"   ✅ {len(clientes)} clientes encontrados")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    # Teste 2: Endpoint de usuário
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers, timeout=15)
        print(f"   GET /users/me: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"   ✅ Usuário: {user.get('email', 'N/A')}")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    # Teste 3: Endpoint de produtos (para comparar)
    try:
        response = requests.get(f"{BASE_URL}/produtos", headers=headers, timeout=15)
        print(f"   GET /produtos: {response.status_code}")
        if response.status_code != 500:
            print(f"   ✅ Produtos OK")
        else:
            print(f"   ❌ Produtos também com erro 500")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")

def test_client_operations(token):
    """Testa operações CRUD de clientes para identificar onde está o problema."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n🧪 Testando operações de clientes...")
    
    # Teste 1: Criar cliente
    cliente_data = {
        "nome": "Cliente Debug",
        "cnpj": "11111111000111",
        "telefone": "11777777777",
        "email": "debug@test.com",
        "tipo_pessoa": "juridica",
        "endereco": {
            "logradouro": "Rua Debug",
            "numero": "123",
            "complemento": "",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01000-000"
        },
        "empresa_vinculada": "HIGIPLAS"
    }
    
    try:
        print("   Criando cliente...")
        create_response = requests.post(f"{BASE_URL}/clientes/", headers=headers, json=cliente_data, timeout=15)
        print(f"   POST /clientes: {create_response.status_code}")
        
        if create_response.status_code == 200:
            cliente = create_response.json()
            cliente_id = cliente["id"]
            print(f"   ✅ Cliente criado com ID: {cliente_id}")
            
            # Teste 2: Buscar cliente específico
            try:
                print(f"   Buscando cliente {cliente_id}...")
                get_response = requests.get(f"{BASE_URL}/clientes/{cliente_id}", headers=headers, timeout=15)
                print(f"   GET /clientes/{cliente_id}: {get_response.status_code}")
                
                if get_response.status_code == 200:
                    print(f"   ✅ Cliente encontrado")
                else:
                    print(f"   ❌ Erro ao buscar: {get_response.text}")
            except Exception as e:
                print(f"   ❌ Exceção ao buscar: {e}")
            
            # Teste 3: Atualizar cliente
            try:
                print(f"   Atualizando cliente {cliente_id}...")
                update_data = {"telefone": "11888888888"}
                put_response = requests.put(f"{BASE_URL}/clientes/{cliente_id}", headers=headers, json=update_data, timeout=15)
                print(f"   PUT /clientes/{cliente_id}: {put_response.status_code}")
                
                if put_response.status_code == 200:
                    print(f"   ✅ Cliente atualizado")
                else:
                    print(f"   ❌ Erro ao atualizar: {put_response.text}")
            except Exception as e:
                print(f"   ❌ Exceção ao atualizar: {e}")
            
            # Teste 4: DELETE (o problema)
            try:
                print(f"   Deletando cliente {cliente_id}...")
                delete_response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}", headers=headers, timeout=15)
                print(f"   DELETE /clientes/{cliente_id}: {delete_response.status_code}")
                
                if delete_response.status_code == 200:
                    print(f"   ✅ Cliente deletado com sucesso!")
                    response_data = delete_response.json()
                    print(f"   Mensagem: {response_data.get('message', 'N/A')}")
                elif delete_response.status_code == 500:
                    print(f"   ❌ Erro 500 confirmado")
                    print(f"   Resposta: {delete_response.text}")
                    
                    # Tentar obter mais detalhes do erro
                    print(f"   Headers da resposta: {dict(delete_response.headers)}")
                    
                else:
                    print(f"   ❌ Erro {delete_response.status_code}: {delete_response.text}")
                    
            except Exception as e:
                print(f"   ❌ Exceção no DELETE: {e}")
                
        else:
            print(f"   ❌ Erro ao criar cliente: {create_response.text}")
            
    except Exception as e:
        print(f"   ❌ Exceção geral: {e}")

def test_database_connection():
    """Testa se o problema pode ser de conexão com banco de dados."""
    print("\n🔗 Testando conectividade geral...")
    
    try:
        # Teste de health check
        response = requests.get(f"{BASE_URL}/", timeout=15)
        print(f"   Health check: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Serviço está online")
        else:
            print(f"   ❌ Serviço com problemas: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro de conectividade: {e}")

def main():
    print("=== INVESTIGAÇÃO PROFUNDA DO ERRO 500 NO DELETE ===")
    print("\n🎯 Objetivo: Identificar a causa real do erro 500")
    print("\n📋 Cenários a testar:")
    print("   1. Endpoints básicos (verificar se é problema geral)")
    print("   2. Operações CRUD de clientes (isolar o DELETE)")
    print("   3. Conectividade geral")
    
    # Obter token
    print("\n🔑 Obtendo token de autenticação...")
    token = get_auth_token()
    if not token:
        print("❌ Não foi possível obter token. Abortando.")
        return
    
    print("✅ Token obtido com sucesso")
    
    # Executar testes
    test_database_connection()
    test_basic_endpoints(token)
    test_client_operations(token)
    
    print("\n=== ANÁLISE DOS RESULTADOS ===")
    print("\n🔍 Com base nos testes acima, podemos identificar:")
    print("   - Se o problema é específico do DELETE ou geral")
    print("   - Se outros endpoints também têm erro 500")
    print("   - Se a correção foi aplicada corretamente")
    print("   - Se há problemas de conectividade ou banco de dados")
    
    print("\n💡 Próximos passos baseados nos resultados:")
    print("   - Se apenas DELETE falha: problema específico na função")
    print("   - Se múltiplos endpoints falham: problema de infraestrutura")
    print("   - Se nenhum endpoint funciona: problema de deploy/conectividade")

if __name__ == "__main__":
    main()