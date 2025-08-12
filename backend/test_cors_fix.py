#!/usr/bin/env python3

import requests
import json
import time

# Configurações
BACKEND_URL = "http://localhost:8000"
PRODUCTION_URL = "https://higiplas-system.onrender.com"
FRONTEND_ORIGIN = "https://higiplas-system.vercel.app"

def test_cors_local():
    """Testa CORS no ambiente local"""
    print("🔍 Testando CORS no ambiente local...")
    
    try:
        # Teste básico de saúde
        response = requests.get(f"{BACKEND_URL}/")
        print(f"✅ Health check local: {response.status_code}")
        
        # Teste do endpoint de CORS
        response = requests.get(f"{BACKEND_URL}/cors-test")
        print(f"✅ CORS test local: {response.status_code}")
        print(f"📋 Response: {response.json()}")
        
        # Teste com headers de origem
        headers = {
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type"
        }
        
        # Teste OPTIONS (preflight)
        response = requests.options(f"{BACKEND_URL}/clientes/1", headers=headers)
        print(f"✅ OPTIONS preflight local: {response.status_code}")
        print(f"📋 CORS Headers: {dict(response.headers)}")
        
    except Exception as e:
        print(f"❌ Erro no teste local: {e}")

def test_cors_production():
    """Testa CORS no ambiente de produção"""
    print("\n🔍 Testando CORS no ambiente de produção...")
    
    try:
        # Teste básico de saúde
        response = requests.get(f"{PRODUCTION_URL}/")
        print(f"✅ Health check produção: {response.status_code}")
        
        # Teste do endpoint de CORS
        response = requests.get(f"{PRODUCTION_URL}/cors-test")
        print(f"✅ CORS test produção: {response.status_code}")
        print(f"📋 Response: {response.json()}")
        
        # Teste com headers de origem
        headers = {
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type"
        }
        
        # Teste OPTIONS (preflight)
        response = requests.options(f"{PRODUCTION_URL}/clientes/1", headers=headers)
        print(f"✅ OPTIONS preflight produção: {response.status_code}")
        print(f"📋 CORS Headers: {dict(response.headers)}")
        
        # Teste específico do endpoint que estava falhando
        response = requests.get(f"{PRODUCTION_URL}/clientes/1", headers={"Origin": FRONTEND_ORIGIN})
        print(f"✅ GET /clientes/1 produção: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Erro no teste de produção: {e}")

def main():
    print("🚀 Iniciando testes de CORS...")
    
    # Testa local primeiro
    test_cors_local()
    
    # Aguarda um pouco
    time.sleep(2)
    
    # Testa produção
    test_cors_production()
    
    print("\n✅ Testes de CORS concluídos!")
    print("\n📝 Próximos passos:")
    print("1. Se os testes locais passaram, faça o deploy das mudanças")
    print("2. Aguarde alguns minutos para o Render atualizar")
    print("3. Teste novamente o frontend no Vercel")
    print("4. Verifique os logs do Render para mensagens de debug")

if __name__ == "__main__":
    main()