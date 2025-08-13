#!/usr/bin/env python3
"""
Script para testar o endpoint /clientes/1 com autenticação após a correção.
"""

import requests
import os

# --- DADOS DE LOGIN ---
# Use variáveis de ambiente ou substitua diretamente
email = os.getenv("TEST_USER_EMAIL", "enzo.alverde@gmail.com")
password = os.getenv("TEST_USER_PASSWORD", "enzolilia")
# --------------------

base_url = "https://higiplas-system.onrender.com"

def get_access_token():
    """Obtém o token de acesso da API."""
    
    login_url = f"{base_url}/login/token"
    login_data = {
        "username": email,
        "password": password
    }
    
    print(f"1️⃣  Tentando obter token de acesso para: {email}...")
    
    try:
        response = requests.post(login_url, data=login_data, timeout=15)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print("✅ Token de acesso obtido com sucesso!")
            return access_token
        else:
            print(f"❌ Erro ao obter token. Status: {response.status_code}")
            try:
                print(f"   Detalhes: {response.json()}")
            except:
                print(f"   Resposta: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Falha na requisição de login: {e}")
        return None

def test_authenticated_endpoint(token):
    """Testa o endpoint /clientes/1 com o token de acesso."""
    
    if not token:
        print("\n⚠️  Não foi possível continuar sem um token de acesso.")
        return

    test_url = f"{base_url}/clientes/1"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"\n2️⃣  Testando endpoint protegido: GET {test_url}")
    
    try:
        response = requests.get(test_url, headers=headers, timeout=15)
        
        print(f"   Status da Resposta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Endpoint respondeu com sucesso (200 OK)!")
            try:
                client_data = response.json()
                print("   Dados do cliente recebidos:")
                # Imprime alguns dados para verificação
                print(f"   - ID: {client_data.get('id')}")
                print(f"   - Nome: {client_data.get('nome')}")
                print(f"   - E-mail: {client_data.get('email')}")
                
                if 'historico_pagamentos' in client_data:
                    print("   - Histórico de pagamentos: Encontrado")
                else:
                    print("   - Histórico de pagamentos: Não encontrado na resposta")

            except Exception as e:
                print(f"   ⚠️  Não foi possível processar o JSON da resposta: {e}")
                print(f"   Resposta (texto): {response.text[:250]}...")

        elif response.status_code == 404:
            print("⚠️  Cliente com ID 1 não encontrado (404 Not Found).")
            print("   Isso pode ser normal se o banco de dados de produção estiver vazio.")
        else:
            print("❌ Teste falhou com um status inesperado.")
            try:
                print(f"   Detalhes: {response.json()}")
            except:
                print(f"   Resposta: {response.text[:250]}...")

    except requests.exceptions.RequestException as e:
        print(f"❌ Falha na requisição ao endpoint: {e}")


if __name__ == "__main__":
    print("=== TESTE DE ENDPOINT AUTENTICADO PÓS-CORREÇÃO ===")
    access_token = get_access_token()
    test_authenticated_endpoint(access_token)
    print("\n=== TESTE CONCLUÍDO ===")