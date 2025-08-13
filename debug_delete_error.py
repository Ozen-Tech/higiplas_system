#!/usr/bin/env python3
"""
Script para debugar o erro 500 no DELETE de clientes em produção.
"""

import requests
import json
import traceback

# Configurações
BASE_URL = "https://higiplas-system.onrender.com"
EMAIL = "enzo.alverde@gmail.com"
PASSWORD = "enzolilia"

def debug_delete_error():
    print("🔍 Debugando erro 500 no DELETE de clientes...")
    print(f"🌐 Backend: {BASE_URL}")
    print(f"👤 Usuário: {EMAIL}")
    print()
    
    try:
        # 1. Fazer login
        print("1️⃣ Fazendo login...")
        login_data = {
            "username": EMAIL,
            "password": PASSWORD
        }
        
        login_response = requests.post(f"{BASE_URL}/users/token", data=login_data, timeout=15)
        print(f"   Status do login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        print(f"✅ Login realizado com sucesso!")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # 2. Listar clientes existentes
        print("\n2️⃣ Listando clientes existentes...")
        list_response = requests.get(f"{BASE_URL}/clientes", headers=headers, timeout=15)
        print(f"   Status da listagem: {list_response.status_code}")
        
        if list_response.status_code == 200:
            clientes = list_response.json()
            print(f"✅ {len(clientes)} clientes encontrados")
            
            if clientes:
                # Pegar o primeiro cliente para testar
                cliente_teste = clientes[0]
                cliente_id = cliente_teste["id"]
                print(f"   Cliente para teste: ID {cliente_id} - {cliente_teste.get('nome', 'N/A')}")
                
                # 3. Verificar se o cliente tem orçamentos
                print(f"\n3️⃣ Verificando orçamentos do cliente {cliente_id}...")
                orcamentos_response = requests.get(f"{BASE_URL}/orcamentos", headers=headers, timeout=15)
                print(f"   Status da consulta de orçamentos: {orcamentos_response.status_code}")
                
                if orcamentos_response.status_code == 200:
                    orcamentos = orcamentos_response.json()
                    orcamentos_cliente = [o for o in orcamentos if o.get('cliente_id') == cliente_id]
                    print(f"   Orçamentos do cliente: {len(orcamentos_cliente)}")
                    
                    if orcamentos_cliente:
                        print("⚠️ Cliente tem orçamentos associados - DELETE deve retornar 400, não 500")
                        for orc in orcamentos_cliente:
                            print(f"     - Orçamento ID: {orc.get('id')} - Status: {orc.get('status', 'N/A')}")
                    else:
                        print("✅ Cliente não tem orçamentos - DELETE deve funcionar")
                else:
                    print(f"❌ Erro ao consultar orçamentos: {orcamentos_response.text}")
                
                # 4. Tentar DELETE com mais detalhes
                print(f"\n4️⃣ Testando DELETE no cliente ID {cliente_id}...")
                print(f"   URL: {BASE_URL}/clientes/{cliente_id}")
                print(f"   Headers: {headers}")
                
                try:
                    delete_response = requests.delete(
                        f"{BASE_URL}/clientes/{cliente_id}", 
                        headers=headers, 
                        timeout=30  # Timeout maior para capturar erro
                    )
                    
                    print(f"   Status do DELETE: {delete_response.status_code}")
                    print(f"   Headers da resposta: {dict(delete_response.headers)}")
                    print(f"   Conteúdo da resposta: {delete_response.text}")
                    print(f"   Encoding da resposta: {delete_response.encoding}")
                    
                    # Tentar capturar mais detalhes do erro
                    if delete_response.status_code == 500:
                        print("\n🔍 Análise do erro 500:")
                        print(f"   - Content-Type: {delete_response.headers.get('Content-Type', 'N/A')}")
                        print(f"   - Server: {delete_response.headers.get('Server', 'N/A')}")
                        print(f"   - X-Render-Origin-Server: {delete_response.headers.get('x-render-origin-server', 'N/A')}")
                        
                        # Verificar se é um erro de timeout ou conexão
                        if 'timeout' in delete_response.text.lower():
                            print("   ⚠️ Possível timeout no banco de dados")
                        elif 'connection' in delete_response.text.lower():
                            print("   ⚠️ Possível problema de conexão com o banco")
                        elif 'internal server error' in delete_response.text.lower():
                            print("   ⚠️ Erro interno genérico - verificar logs do Render")
                        
                except requests.exceptions.Timeout:
                    print("❌ Timeout na requisição DELETE - possível problema no backend")
                except requests.exceptions.ConnectionError:
                    print("❌ Erro de conexão na requisição DELETE")
                except Exception as e:
                    print(f"❌ Erro inesperado na requisição DELETE: {e}")
                    traceback.print_exc()
                
            else:
                print("⚠️ Nenhum cliente encontrado para testar")
        else:
            print(f"❌ Erro ao listar clientes: {list_response.text}")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_delete_error()
    print("\n=== DEBUG CONCLUÍDO ===")