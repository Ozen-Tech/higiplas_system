#!/usr/bin/env python3

import requests
import json

def test_orcamento_validation():
    """Testa se há orçamentos com campos None que causam erro de validação."""
    
    base_url = "https://higiplas-system.onrender.com"
    
    print("🔍 Testando validação de orçamentos...")
    print(f"🌐 Backend: {base_url}")
    
    # 1. Fazer login
    login_data = {
        "username": "enzo.alverde@gmail.com",
        "password": "enzolilia"
    }
    
    print("\n1️⃣ Fazendo login...")
    login_response = requests.post(f"{base_url}/users/token", data=login_data)
    print(f"   Status do login: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login realizado com sucesso!")
    
    # 2. Testar endpoint de orçamentos com detalhes do erro
    print("\n2️⃣ Testando endpoint /orcamentos...")
    try:
        orcamentos_response = requests.get(f"{base_url}/orcamentos", headers=headers, timeout=30)
        print(f"   Status: {orcamentos_response.status_code}")
        
        if orcamentos_response.status_code == 200:
            orcamentos = orcamentos_response.json()
            print(f"   ✅ {len(orcamentos)} orçamentos encontrados")
            
            # Verificar se há orçamentos com campos problemáticos
            for i, orcamento in enumerate(orcamentos[:3]):
                print(f"\n   📋 Orçamento {i+1}:")
                print(f"      ID: {orcamento.get('id')}")
                print(f"      condicao_pagamento: {repr(orcamento.get('condicao_pagamento'))}")
                print(f"      cliente: {type(orcamento.get('cliente'))} - {orcamento.get('cliente')}")
                print(f"      status: {orcamento.get('status')}")
                
        elif orcamentos_response.status_code == 500:
            print(f"   ❌ Erro 500: {orcamentos_response.text}")
            
            # Tentar extrair detalhes do erro de validação
            try:
                error_data = orcamentos_response.json()
                if 'detail' in error_data:
                    print(f"   🔍 Detalhes do erro: {error_data['detail']}")
            except:
                print("   🔍 Não foi possível extrair detalhes do erro JSON")
                
        else:
            print(f"   ❌ Erro: {orcamentos_response.text}")
            
    except requests.exceptions.Timeout:
        print("   ⏰ Timeout na requisição")
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_orcamento_validation()
    print("\n=== TESTE DE VALIDAÇÃO CONCLUÍDO ===")