#!/usr/bin/env python3
"""
Script para testar os novos endpoints de cliente v2
"""

import requests
import json
from datetime import datetime

# URL base da API (ajustar conforme necessário)
API_URL = "https://higiplas-system.onrender.com"
# API_URL = "http://localhost:8000"  # Para testes locais

# Token de autenticação (você precisa fazer login primeiro)
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlbnpvLmFsdmVyZGVAZ21haWwuY29tIiwiZXhwIjoxNzU5NjA5MDQ2fQ.sGHMUmiuJWxO0wnoUpUkNcdPc2tCYNtzl5B-I9y-wv8"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_quick_create():
    """Testar criação rápida de cliente"""
    print("\n🚀 Testando criação rápida (POST /v2/clientes/quick)")
    
    data = {
        "nome": "João da Silva",
        "telefone": "98999887766"
    }
    
    response = requests.post(f"{API_URL}/v2/clientes/quick", json=data, headers=headers)
    
    if response.status_code == 200:
        print("✅ Criação rápida funcionando!")
        print(f"   Cliente criado: {response.json()}")
    else:
        print(f"❌ Erro: {response.status_code} - {response.text}")
    
    return response.status_code == 200

def test_full_create():
    """Testar criação completa de cliente"""
    print("\n📝 Testando criação completa (POST /v2/clientes/)")
    
    data = {
        "nome": "Maria Oliveira",
        "telefone": "98888776655",
        "tipo_pessoa": "FISICA",
        "cpf_cnpj": "12345678900",
        "bairro": "Centro",
        "cidade": "São Luís",
        "observacoes": "Cliente preferencial, paga à vista",
        "referencia_localizacao": "Próximo ao mercado central"
    }
    
    response = requests.post(f"{API_URL}/v2/clientes/", json=data, headers=headers)
    
    if response.status_code == 200:
        print("✅ Criação completa funcionando!")
        print(f"   Cliente criado: {response.json()['nome']}")
    else:
        print(f"❌ Erro: {response.status_code} - {response.text}")
    
    return response.status_code == 200

def test_list_clients():
    """Testar listagem de clientes"""
    print("\n📋 Testando listagem (GET /v2/clientes/)")
    
    params = {
        "limit": 5,
        "skip": 0
    }
    
    response = requests.get(f"{API_URL}/v2/clientes/", params=params, headers=headers)
    
    if response.status_code == 200:
        clientes = response.json()
        print(f"✅ Listagem funcionando! {len(clientes)} clientes encontrados")
        for cliente in clientes[:3]:  # Mostrar apenas os 3 primeiros
            print(f"   - {cliente.get('nome', 'Sem nome')} ({cliente.get('telefone', 'Sem telefone')})")
        return clientes
    else:
        print(f"❌ Erro: {response.status_code} - {response.text}")
        return []

def test_search():
    """Testar busca de clientes"""
    print("\n🔍 Testando busca (GET /v2/clientes/?search=)")
    
    params = {
        "search": "João",
        "limit": 5
    }
    
    response = requests.get(f"{API_URL}/v2/clientes/", params=params, headers=headers)
    
    if response.status_code == 200:
        clientes = response.json()
        print(f"✅ Busca funcionando! {len(clientes)} clientes com 'João'")
    else:
        print(f"❌ Erro: {response.status_code} - {response.text}")

def test_filter_by_location():
    """Testar filtro por localização"""
    print("\n📍 Testando filtro por bairro (GET /v2/clientes/?bairro=)")
    
    params = {
        "bairro": "Centro",
        "limit": 5
    }
    
    response = requests.get(f"{API_URL}/v2/clientes/", params=params, headers=headers)
    
    if response.status_code == 200:
        clientes = response.json()
        print(f"✅ Filtro por bairro funcionando! {len(clientes)} clientes no Centro")
    else:
        print(f"❌ Erro: {response.status_code} - {response.text}")

def test_my_clients():
    """Testar filtro de meus clientes"""
    print("\n👤 Testando meus clientes (GET /v2/clientes/?meus_clientes=true)")
    
    params = {
        "meus_clientes": True,
        "limit": 5
    }
    
    response = requests.get(f"{API_URL}/v2/clientes/", params=params, headers=headers)
    
    if response.status_code == 200:
        clientes = response.json()
        print(f"✅ Filtro 'meus clientes' funcionando! {len(clientes)} clientes seus")
    else:
        print(f"❌ Erro: {response.status_code} - {response.text}")

def test_get_client(client_id):
    """Testar buscar cliente específico"""
    print(f"\n🔎 Testando buscar cliente ID {client_id} (GET /v2/clientes/{client_id})")
    
    response = requests.get(f"{API_URL}/v2/clientes/{client_id}", headers=headers)
    
    if response.status_code == 200:
        cliente = response.json()
        print(f"✅ Busca por ID funcionando!")
        print(f"   Cliente: {cliente['nome']}")
        print(f"   Telefone: {cliente['telefone']}")
        print(f"   Bairro: {cliente.get('bairro', 'Não informado')}")
    else:
        print(f"❌ Erro: {response.status_code} - {response.text}")

def test_update_client(client_id):
    """Testar atualização de cliente"""
    print(f"\n✏️ Testando atualização ID {client_id} (PUT /v2/clientes/{client_id})")
    
    data = {
        "observacoes": f"Atualizado em {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "bairro": "Cohama"
    }
    
    response = requests.put(f"{API_URL}/v2/clientes/{client_id}", json=data, headers=headers)
    
    if response.status_code == 200:
        print("✅ Atualização funcionando!")
        print(f"   Observações atualizadas")
    else:
        print(f"❌ Erro: {response.status_code} - {response.text}")

def test_client_stats(client_id):
    """Testar estatísticas do cliente"""
    print(f"\n📊 Testando estatísticas ID {client_id} (GET /v2/clientes/{client_id}/stats)")
    
    response = requests.get(f"{API_URL}/v2/clientes/{client_id}/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Estatísticas funcionando!")
        print(f"   Total de orçamentos: {stats.get('total_orcamentos', 0)}")
        print(f"   Total vendido: R$ {stats.get('total_vendido', 0):.2f}")
        print(f"   Ticket médio: R$ {stats.get('ticket_medio', 0):.2f}")
    else:
        print(f"❌ Erro: {response.status_code} - {response.text}")

def test_nearby_search():
    """Testar busca por proximidade"""
    print("\n🗺️ Testando busca por proximidade (GET /v2/clientes/search/nearby)")
    
    params = {
        "bairro": "Centro",
        "limit": 10
    }
    
    response = requests.get(f"{API_URL}/v2/clientes/search/nearby", params=params, headers=headers)
    
    if response.status_code == 200:
        clientes = response.json()
        print(f"✅ Busca por proximidade funcionando! {len(clientes)} clientes no Centro")
    else:
        print(f"❌ Erro: {response.status_code} - {response.text}")

def main():
    print("=" * 60)
    print("🧪 TESTE DO SISTEMA DE CLIENTES V2")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Token: {TOKEN[:20]}...")
    
    # Executar testes
    test_quick_create()
    test_full_create()
    clientes = test_list_clients()
    test_search()
    test_filter_by_location()
    test_my_clients()
    
    # Se encontrou clientes, testar operações específicas
    if clientes and len(clientes) > 0:
        client_id = clientes[0]['id']
        test_get_client(client_id)
        test_update_client(client_id)
        test_client_stats(client_id)
    
    test_nearby_search()
    
    print("\n" + "=" * 60)
    print("✅ TESTES CONCLUÍDOS!")
    print("=" * 60)

if __name__ == "__main__":
    main()
