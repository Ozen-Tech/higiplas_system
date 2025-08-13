#!/usr/bin/env python3
"""
Script para testar se a correção do banco de produção funcionou.
"""

import requests
import time
import json

def test_production_api():
    """Testa se a API de produção está funcionando corretamente."""
    
    base_url = "https://higiplas-system.onrender.com"
    
    print("🧪 TESTANDO CORREÇÃO DA API DE PRODUÇÃO")
    print(f"🌐 URL base: {base_url}")
    print()
    
    # Teste 1: Health check
    print("1️⃣ Testando health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check OK")
        else:
            print(f"⚠️  Health check retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False
    
    # Teste 2: Endpoint que causava erro (GET /clientes/1)
    print("\n2️⃣ Testando endpoint que causava erro (GET /clientes/1)...")
    try:
        # Primeiro, vamos tentar sem autenticação para ver se o erro mudou
        response = requests.get(f"{base_url}/clientes/1", timeout=10)
        
        if response.status_code == 401:
            print("✅ Endpoint responde corretamente (401 Unauthorized - esperado sem token)")
            print("   O erro de 'data_vencimento does not exist' foi corrigido!")
        elif response.status_code == 500:
            print("❌ Ainda retorna erro 500 - a correção pode não ter sido aplicada")
            try:
                error_detail = response.json()
                print(f"   Detalhes do erro: {error_detail}")
            except:
                print(f"   Resposta: {response.text[:200]}...")
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return False
    
    # Teste 3: Verificar se o serviço está rodando
    print("\n3️⃣ Testando se o serviço está ativo...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ Documentação da API acessível")
        else:
            print(f"⚠️  Documentação retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar documentação: {e}")
    
    return True

def monitor_render_deploy():
    """Monitora o status do deploy no Render."""
    
    print("🔍 MONITORANDO DEPLOY NO RENDER")
    print("Aguardando o deploy ser concluído...")
    print("(Isso pode levar alguns minutos)")
    print()
    
    max_attempts = 20  # 10 minutos
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"⏳ Tentativa {attempt}/{max_attempts} - Testando API...")
        
        try:
            response = requests.get("https://higiplas-system.onrender.com/health", timeout=10)
            
            if response.status_code == 200:
                print("✅ API está respondendo!")
                print("🎉 Deploy parece ter sido concluído")
                return True
            else:
                print(f"⚠️  API retornou status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"⏳ API ainda não está disponível: {type(e).__name__}")
        
        if attempt < max_attempts:
            print("   Aguardando 30 segundos...")
            time.sleep(30)
        
    print("⏰ Timeout atingido. O deploy pode ainda estar em andamento.")
    return False

def main():
    """Função principal."""
    
    print("=== TESTE DA CORREÇÃO DO BANCO DE PRODUÇÃO ===")
    print()
    
    # Opção 1: Monitorar deploy
    print("Escolha uma opção:")
    print("1. Monitorar deploy e testar quando estiver pronto")
    print("2. Testar agora (se o deploy já foi concluído)")
    print("3. Apenas mostrar instruções")
    
    choice = input("\nEscolha (1/2/3): ").strip()
    
    if choice == "1":
        print("\n🔄 Iniciando monitoramento...")
        if monitor_render_deploy():
            print("\n🧪 Executando testes...")
            test_production_api()
        else:
            print("\n⚠️  Não foi possível confirmar que o deploy terminou.")
            print("Você pode testar manualmente mais tarde.")
            
    elif choice == "2":
        print("\n🧪 Executando testes...")
        test_production_api()
        
    elif choice == "3":
        print("\n📋 INSTRUÇÕES MANUAIS:")
        print("1. Acesse https://dashboard.render.com")
        print("2. Vá para o serviço 'higiplas-system'")
        print("3. Verifique se o deploy foi concluído")
        print("4. Acesse os logs para ver se a migração foi aplicada")
        print("5. Teste a API acessando: https://higiplas-system.onrender.com/clientes/1")
        print("   (Deve retornar 401 em vez de 500)")
        
    else:
        print("Opção inválida.")
    
    print("\n🔗 Links úteis:")
    print("- Render Dashboard: https://dashboard.render.com")
    print("- API de Produção: https://higiplas-system.onrender.com")
    print("- Documentação: https://higiplas-system.onrender.com/docs")
    print("- Frontend: https://higiplas-frontend.vercel.app")

if __name__ == "__main__":
    main()