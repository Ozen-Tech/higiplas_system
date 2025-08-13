#!/usr/bin/env python3
"""
Script para testar se o problema de CORS está no frontend ou backend.
Simula as requisições que o frontend faz para identificar a causa.
"""

import requests
import json

# Configurações
BASE_URL = "https://higiplas-system.onrender.com"
ORIGIN = "https://higiplas-system.vercel.app"
FAKE_TOKEN = "fake-token-for-testing"

def test_preflight_request(method, endpoint):
    """Testa requisição OPTIONS (preflight)"""
    print(f"\n=== Testando preflight {method} {endpoint} ===")
    
    headers = {
        "Origin": ORIGIN,
        "Access-Control-Request-Method": method,
        "Access-Control-Request-Headers": "Authorization,Content-Type"
    }
    
    try:
        response = requests.options(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"CORS Headers:")
        for header, value in response.headers.items():
            if "access-control" in header.lower():
                print(f"  {header}: {value}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_actual_request(method, endpoint, data=None):
    """Testa requisição real"""
    print(f"\n=== Testando {method} {endpoint} ===")
    
    headers = {
        "Origin": ORIGIN,
        "Authorization": f"Bearer {FAKE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method == "DELETE":
            response = requests.delete(f"{BASE_URL}{endpoint}", headers=headers)
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", headers=headers, json=data or {})
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data or {})
        
        print(f"Status: {response.status_code}")
        print(f"CORS Headers:")
        for header, value in response.headers.items():
            if "access-control" in header.lower():
                print(f"  {header}: {value}")
        
        if response.status_code != 401:  # 401 é esperado com token fake
            print(f"Response body: {response.text[:200]}...")
        
        return response.status_code in [200, 401]  # 401 é OK para token inválido
    except Exception as e:
        print(f"Erro: {e}")
        return False

def main():
    print("🔍 Testando problemas de CORS reportados pelo frontend")
    print(f"Backend: {BASE_URL}")
    print(f"Origin: {ORIGIN}")
    
    tests = [
        # Testes de preflight
        ("preflight", "GET", "/clientes/1"),
        ("preflight", "DELETE", "/clientes/1"),
        ("preflight", "PUT", "/clientes/1"),
        
        # Testes de requisições reais
        ("actual", "GET", "/clientes/1"),
        ("actual", "DELETE", "/clientes/1"),
        ("actual", "PUT", "/clientes/1", {"nome": "Test"}),
    ]
    
    results = []
    
    for test_type, method, endpoint, *args in tests:
        if test_type == "preflight":
            success = test_preflight_request(method, endpoint)
        else:
            data = args[0] if args else None
            success = test_actual_request(method, endpoint, data)
        
        results.append((test_type, method, endpoint, success))
    
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    all_passed = True
    for test_type, method, endpoint, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {test_type.upper()} {method} {endpoint}")
        if not success:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("O problema NÃO está no backend. Possíveis causas:")
        print("1. Cache do browser no frontend")
        print("2. Configuração incorreta no deploy do Vercel")
        print("3. Token de autenticação inválido/expirado")
        print("4. Problema de rede/DNS")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM!")
        print("O problema pode estar no backend.")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Limpar cache do browser")
    print("2. Verificar se o frontend está usando a URL correta")
    print("3. Verificar logs do Vercel")
    print("4. Testar com token de autenticação válido")

if __name__ == "__main__":
    main()