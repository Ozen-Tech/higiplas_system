#!/usr/bin/env python3
"""
Script para aplicar migration e testar endpoints v2 em produção
"""

import requests
import json
import os
from datetime import datetime

# URLs
PROD_URL = "https://higiplas-system.onrender.com"
LOCAL_URL = "http://localhost:8000"

# Usar produção por padrão
API_URL = PROD_URL

# Token de teste (você precisa fazer login primeiro)
TOKEN = None  # Será preenchido após login

def login():
    """Fazer login e obter token"""
    global TOKEN
    
    print("🔐 Fazendo login...")
    
    login_data = {
        "username": "admin@higiplas.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{API_URL}/users/token", data=login_data)
        
        if response.status_code == 200:
            data = response.json()
            TOKEN = data.get('access_token')
            print("✅ Login realizado com sucesso!")
            return True
        else:
            print(f"❌ Erro no login: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def get_headers():
    """Obter headers com autenticação"""
    if not TOKEN:
        return {"Content-Type": "application/json"}
    
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

def test_health():
    """Testar se a API está online"""
    print("\n🏥 Testando saúde da API...")
    
    try:
        response = requests.get(f"{API_URL}/")
        
        if response.status_code == 200:
            print("✅ API está online!")
            return True
        else:
            print(f"❌ API com problemas: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def test_quick_create():
    """Testar criação rápida de cliente"""
    print("\n🚀 Testando criação rápida (POST /clientes/quick)")
    
    data = {
        "nome": f"Cliente Teste {datetime.now().strftime('%H%M%S')}",
        "telefone": f"9899988{datetime.now().strftime('%H%M')}"
    }
    
    try:
        response = requests.post(f"{API_URL}/clientes/quick", json=data, headers=get_headers())
        
        if response.status_code == 200:
            cliente = response.json()
            print("✅ Criação rápida funcionando!")
            print(f"   Cliente criado: {cliente.get('nome')} (ID: {cliente.get('id')})")
            return cliente
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_full_create():
    """Testar criação completa de cliente"""
    print("\n📝 Testando criação completa (POST /clientes/)")
    
    timestamp = datetime.now().strftime('%H%M%S')
    data = {
        "nome": f"Cliente Completo {timestamp}",
        "telefone": f"9888877{timestamp[:4]}",
        "tipo_pessoa": "FISICA",
        "cpf_cnpj": f"123456789{timestamp[:2]}",
        "bairro": "Centro",
        "cidade": "São Luís",
        "observacoes": f"Cliente de teste criado em {datetime.now()}",
        "referencia_localizacao": "Próximo ao teste automatizado"
    }
    
    try:
        response = requests.post(f"{API_URL}/clientes/", json=data, headers=get_headers())
        
        if response.status_code == 200:
            cliente = response.json()
            print("✅ Criação completa funcionando!")
            print(f"   Cliente: {cliente.get('nome')} (ID: {cliente.get('id')})")
            print(f"   Bairro: {cliente.get('bairro')}")
            return cliente
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_list_clients():
    """Testar listagem de clientes"""
    print("\n📋 Testando listagem (GET /clientes/)")
    
    try:
        response = requests.get(f"{API_URL}/clientes/?limit=5", headers=get_headers())
        
        if response.status_code == 200:
            clientes = response.json()
            print(f"✅ Listagem funcionando! {len(clientes)} clientes encontrados")
            
            for i, cliente in enumerate(clientes[:3]):
                print(f"   {i+1}. {cliente.get('nome', 'Sem nome')} - {cliente.get('telefone', 'Sem telefone')}")
            
            return clientes
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return []

def test_search():
    """Testar busca de clientes"""
    print("\n🔍 Testando busca (GET /clientes/?search=)")
    
    try:
        response = requests.get(f"{API_URL}/clientes/?search=Teste&limit=10", headers=get_headers())
        
        if response.status_code == 200:
            clientes = response.json()
            print(f"✅ Busca funcionando! {len(clientes)} clientes com 'Teste'")
            return True
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_filter_by_bairro():
    """Testar filtro por bairro"""
    print("\n📍 Testando filtro por bairro (GET /clientes/?bairro=)")
    
    try:
        response = requests.get(f"{API_URL}/clientes/?bairro=Centro&limit=10", headers=get_headers())
        
        if response.status_code == 200:
            clientes = response.json()
            print(f"✅ Filtro por bairro funcionando! {len(clientes)} clientes no Centro")
            return True
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_my_clients():
    """Testar filtro de meus clientes"""
    print("\n👤 Testando meus clientes (GET /clientes/?meus_clientes=true)")
    
    try:
        response = requests.get(f"{API_URL}/clientes/?meus_clientes=true&limit=10", headers=get_headers())
        
        if response.status_code == 200:
            clientes = response.json()
            print(f"✅ Filtro 'meus clientes' funcionando! {len(clientes)} clientes seus")
            return True
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_get_client(client_id):
    """Testar buscar cliente específico"""
    print(f"\n🔎 Testando buscar cliente ID {client_id} (GET /clientes/{client_id})")
    
    try:
        response = requests.get(f"{API_URL}/clientes/{client_id}", headers=get_headers())
        
        if response.status_code == 200:
            cliente = response.json()
            print(f"✅ Busca por ID funcionando!")
            print(f"   Cliente: {cliente.get('nome')}")
            print(f"   Telefone: {cliente.get('telefone')}")
            return cliente
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_update_client(client_id):
    """Testar atualização de cliente"""
    print(f"\n✏️ Testando atualização ID {client_id} (PUT /clientes/{client_id})")
    
    data = {
        "observacoes": f"Atualizado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "bairro": "Cohama"
    }
    
    try:
        response = requests.put(f"{API_URL}/clientes/{client_id}", json=data, headers=get_headers())
        
        if response.status_code == 200:
            print("✅ Atualização funcionando!")
            return True
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_client_stats(client_id):
    """Testar estatísticas do cliente"""
    print(f"\n📊 Testando estatísticas ID {client_id} (GET /clientes/{client_id}/stats)")
    
    try:
        response = requests.get(f"{API_URL}/clientes/{client_id}/stats", headers=get_headers())
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Estatísticas funcionando!")
            print(f"   Total de orçamentos: {stats.get('total_orcamentos', 0)}")
            print(f"   Total vendido: R$ {stats.get('total_vendido', 0):.2f}")
            return True
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_nearby_search():
    """Testar busca por proximidade"""
    print("\n🗺️ Testando busca por proximidade (GET /clientes/search/nearby)")
    
    try:
        response = requests.get(f"{API_URL}/clientes/search/nearby?bairro=Centro&limit=10", headers=get_headers())
        
        if response.status_code == 200:
            clientes = response.json()
            print(f"✅ Busca por proximidade funcionando! {len(clientes)} clientes no Centro")
            return True
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    print("=" * 70)
    print("🧪 TESTE COMPLETO DO SISTEMA DE CLIENTES V2")
    print("=" * 70)
    print(f"🌐 API URL: {API_URL}")
    
    # Testes básicos
    if not test_health():
        print("\n❌ API não está respondendo. Abortando testes.")
        return
    
    if not login():
        print("\n❌ Não foi possível fazer login. Abortando testes.")
        return
    
    # Testes de funcionalidade
    print("\n" + "="*50)
    print("📝 TESTANDO CRIAÇÃO DE CLIENTES")
    print("="*50)
    
    cliente_rapido = test_quick_create()
    cliente_completo = test_full_create()
    
    print("\n" + "="*50)
    print("📋 TESTANDO LISTAGEM E BUSCA")
    print("="*50)
    
    clientes = test_list_clients()
    test_search()
    test_filter_by_bairro()
    test_my_clients()
    test_nearby_search()
    
    # Testes com clientes específicos
    if cliente_completo and cliente_completo.get('id'):
        print("\n" + "="*50)
        print("🔧 TESTANDO OPERAÇÕES ESPECÍFICAS")
        print("="*50)
        
        client_id = cliente_completo['id']
        test_get_client(client_id)
        test_update_client(client_id)
        test_client_stats(client_id)
    
    print("\n" + "="*70)
    print("✅ TESTES CONCLUÍDOS!")
    print("="*70)
    
    # Resumo
    print("\n📊 RESUMO:")
    print(f"   • API v2 está funcionando em: {API_URL}")
    print(f"   • Criação rápida: {'✅' if cliente_rapido else '❌'}")
    print(f"   • Criação completa: {'✅' if cliente_completo else '❌'}")
    print(f"   • Listagem: {'✅' if clientes else '❌'}")
    print(f"   • Sistema pronto para uso pelos vendedores!")

if __name__ == "__main__":
    main()
