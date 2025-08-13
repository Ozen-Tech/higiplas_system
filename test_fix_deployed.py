#!/usr/bin/env python3
"""
Script para testar se a correção temporária do DELETE de clientes foi aplicada com sucesso no Render.
"""

import requests
import json
import time

# Configurações
BASE_URL = "https://higiplas-system.onrender.com"
EMAIL = "enzo.alverde@gmail.com"
PASSWORD = "enzolilia"

def wait_for_deploy():
    """Aguarda o deploy ser concluído no Render."""
    print("⏳ Aguardando deploy ser concluído no Render...")
    print("   (O Render pode levar alguns minutos para aplicar as mudanças)")
    
    for i in range(12):  # 12 tentativas = 6 minutos
        print(f"   Tentativa {i+1}/12 - Aguardando 30 segundos...")
        time.sleep(30)
        
        try:
            # Testa se o serviço está respondendo
            response = requests.get(f"{BASE_URL}/", timeout=10)
            if response.status_code == 200:
                print("✅ Serviço está respondendo!")
                return True
        except:
            continue
    
    print("⚠️  Timeout aguardando deploy. Continuando teste...")
    return False

def test_delete_after_fix():
    """Testa o DELETE de clientes após a correção."""
    print("\n🧪 Testando DELETE de clientes após correção...")
    print(f"🌐 Backend: {BASE_URL}")
    print(f"👤 Usuário: {EMAIL}")
    
    try:
        # 1. Fazer login
        print("\n1️⃣ Fazendo login...")
        login_data = {
            "username": EMAIL,
            "password": PASSWORD
        }
        
        login_response = requests.post(f"{BASE_URL}/users/token", data=login_data, timeout=15)
        print(f"   Status do login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.text}")
            return False
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        print(f"✅ Login realizado com sucesso!")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # 2. Criar um cliente de teste
        print("\n2️⃣ Criando cliente de teste...")
        cliente_data = {
            "nome": "Cliente Teste Correção",
            "cnpj": "98765432000188",
            "telefone": "11888888888",
            "email": "teste.correcao@delete.com",
            "tipo_pessoa": "juridica",
            "endereco": {
                "logradouro": "Rua da Correção",
                "numero": "456",
                "complemento": "",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01000-000"
            },
            "empresa_vinculada": "HIGIPLAS"
        }
        
        create_response = requests.post(f"{BASE_URL}/clientes/", headers=headers, json=cliente_data, timeout=15)
        print(f"   Status da criação: {create_response.status_code}")
        
        if create_response.status_code != 200:
            print(f"❌ Erro ao criar cliente: {create_response.text}")
            return False
        
        cliente_criado = create_response.json()
        cliente_id = cliente_criado["id"]
        print(f"✅ Cliente criado com ID: {cliente_id}")
        
        # 3. Testar DELETE (deve funcionar agora)
        print(f"\n3️⃣ Testando DELETE no cliente ID {cliente_id}...")
        delete_response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}", headers=headers, timeout=15)
        print(f"   Status do DELETE: {delete_response.status_code}")
        
        if delete_response.status_code == 200:
            response_data = delete_response.json()
            print("✅ DELETE realizado com sucesso!")
            print(f"   Resposta: {response_data.get('message', 'N/A')}")
            
            # Verificar se contém a mensagem da correção temporária
            if "temporariamente desabilitada" in response_data.get('message', ''):
                print("✅ Correção temporária aplicada com sucesso!")
                print("   A verificação de orçamentos foi desabilitada conforme esperado.")
            
            # 4. Verificar se foi realmente deletado
            print(f"\n4️⃣ Verificando se o cliente foi deletado...")
            get_response = requests.get(f"{BASE_URL}/clientes/{cliente_id}", headers=headers, timeout=15)
            
            if get_response.status_code == 404:
                print("✅ Cliente foi deletado com sucesso!")
                print("✅ CORREÇÃO FUNCIONOU! O DELETE agora está operacional.")
                return True
            else:
                print(f"❌ Cliente ainda existe: {get_response.text}")
                return False
                
        elif delete_response.status_code == 500:
            print("❌ Ainda retornando erro 500")
            print(f"   Resposta: {delete_response.text}")
            print("   A correção pode não ter sido aplicada ainda.")
            return False
            
        else:
            print(f"❌ Erro inesperado: {delete_response.status_code}")
            print(f"   Resposta: {delete_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    print("=== TESTE DA CORREÇÃO TEMPORÁRIA DO DELETE ===")
    print("\n📋 Resumo da correção aplicada:")
    print("   - Comentada a verificação de orçamentos em delete_cliente()")
    print("   - Isso resolve o erro 500 causado pela query de orçamentos")
    print("   - DELETE agora deve funcionar sem verificar orçamentos")
    
    # Aguardar deploy
    wait_for_deploy()
    
    # Testar correção
    success = test_delete_after_fix()
    
    print("\n=== RESULTADO DO TESTE ===")
    if success:
        print("✅ SUCESSO! A correção temporária foi aplicada com sucesso.")
        print("\n📋 Próximos passos:")
        print("   1. ✅ DELETE de clientes está funcionando")
        print("   2. 🔧 Corrigir o problema real no endpoint /orcamentos")
        print("   3. 🔄 Reativar a verificação de orçamentos no DELETE")
        print("\n⚠️  LEMBRETE: Esta é uma correção TEMPORÁRIA")
        print("   Clientes podem ser excluídos mesmo com orçamentos associados.")
    else:
        print("❌ FALHA! A correção não funcionou como esperado.")
        print("\n🔍 Possíveis causas:")
        print("   - Deploy ainda não foi aplicado")
        print("   - Erro na aplicação da correção")
        print("   - Problema diferente do identificado")
        print("\n💡 Sugestões:")
        print("   - Aguarde mais alguns minutos e teste novamente")
        print("   - Verifique os logs do Render")
        print("   - Confirme se o commit foi aplicado")

if __name__ == "__main__":
    main()