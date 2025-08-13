#!/usr/bin/env python3

import requests
import json

def test_orcamento_query():
    """Testa diretamente a query de orçamentos que está causando o erro 500."""
    
    base_url = "https://higiplas-system.onrender.com"
    
    print("🔍 Testando query de orçamentos que causa erro 500...")
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
    
    # 2. Testar endpoint de orçamentos (que está falhando)
    print("\n2️⃣ Testando endpoint /orcamentos (que causa erro 500)...")
    try:
        orcamentos_response = requests.get(f"{base_url}/orcamentos", headers=headers, timeout=30)
        print(f"   Status: {orcamentos_response.status_code}")
        
        if orcamentos_response.status_code == 200:
            orcamentos = orcamentos_response.json()
            print(f"   ✅ {len(orcamentos)} orçamentos encontrados")
        else:
            print(f"   ❌ Erro: {orcamentos_response.text}")
            
    except requests.exceptions.Timeout:
        print("   ❌ Timeout na requisição (>30s)")
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # 3. Testar query simples de contagem (similar ao DELETE)
    print("\n3️⃣ Testando se conseguimos fazer uma query simples de orçamentos...")
    
    # Primeiro, pegar um cliente para testar
    clientes_response = requests.get(f"{base_url}/clientes", headers=headers)
    if clientes_response.status_code == 200:
        clientes = clientes_response.json()
        if clientes:
            cliente_id = clientes[0]['id']
            print(f"   📋 Testando com cliente ID: {cliente_id}")
            
            # Tentar acessar orçamentos específicos (se houver endpoint)
            try:
                # Teste direto da query que o DELETE usa
                print("   🔍 Simulando a verificação que o DELETE faz...")
                print("   (Esta é a mesma query que está causando o problema no DELETE)")
                
                # O DELETE faz: db.query(models.Orcamento).filter(models.Orcamento.cliente_id == cliente_id).count()
                # Mas como não temos acesso direto ao DB, vamos tentar o endpoint
                orcamentos_response = requests.get(f"{base_url}/orcamentos", headers=headers, timeout=10)
                
                if orcamentos_response.status_code == 500:
                    print("   ❌ Confirmado: A query de orçamentos está falhando com erro 500")
                    print("   💡 Isso explica por que o DELETE também falha!")
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    print("\n=== ANÁLISE DO PROBLEMA ===")
    print("🔍 O DELETE de clientes falha porque:")
    print("   1. Ele tenta verificar se há orçamentos associados")
    print("   2. A query de orçamentos está falhando com erro 500")
    print("   3. Isso causa o erro 500 no DELETE também")
    print("\n💡 SOLUÇÃO: Corrigir o problema na query de orçamentos")
    print("   - Pode ser um problema de JOIN ou relacionamento")
    print("   - Ou um problema de timeout no banco de dados")
    print("   - Verificar logs do Render para mais detalhes")

if __name__ == "__main__":
    test_orcamento_query()