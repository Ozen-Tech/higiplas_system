#!/usr/bin/env python3
"""
Script para verificar se o cliente tem orçamentos associados, causando erro no DELETE.
"""

import requests
import json

# Configurações
BASE_URL = "https://higiplas-system.onrender.com"
EMAIL = "@gmail.com"
PASSWORD = ""

def check_client_orcamentos():
    print("🔍 Verificando orçamentos associados ao cliente...")
    print(f"🌐 Backend: {BASE_URL}")
    print(f"👤 Usuário: {EMAIL}")
    print()
    
    # 1. Fazer login
    print("1️⃣ Fazendo login...")
    login_data = {
        "username": EMAIL,
        "password": PASSWORD
    }
    
    try:
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
        
        # 2. Listar clientes
        print("\n2️⃣ Listando clientes...")
        clientes_response = requests.get(f"{BASE_URL}/clientes", headers=headers, timeout=15)
        print(f"   Status da listagem: {clientes_response.status_code}")
        
        if clientes_response.status_code == 200:
            clientes = clientes_response.json()
            print(f"✅ {len(clientes)} clientes encontrados")
            
            for cliente in clientes:
                cliente_id = cliente["id"]
                cliente_nome = cliente.get("nome", "N/A")
                print(f"\n📋 Cliente ID {cliente_id} - {cliente_nome}")
                
                # 3. Verificar orçamentos do cliente
                print(f"   🔍 Verificando orçamentos...")
                orcamentos_response = requests.get(f"{BASE_URL}/orcamentos?cliente_id={cliente_id}", headers=headers, timeout=15)
                
                if orcamentos_response.status_code == 200:
                    orcamentos = orcamentos_response.json()
                    print(f"   📊 {len(orcamentos)} orçamentos encontrados")
                    
                    if len(orcamentos) > 0:
                        print(f"   ⚠️ Cliente tem orçamentos associados - DELETE deve falhar com erro 400")
                        for i, orcamento in enumerate(orcamentos[:3]):  # Mostrar apenas os primeiros 3
                            print(f"      - Orçamento {i+1}: ID {orcamento.get('id', 'N/A')} - Status: {orcamento.get('status', 'N/A')}")
                        if len(orcamentos) > 3:
                            print(f"      ... e mais {len(orcamentos) - 3} orçamentos")
                    else:
                        print(f"   ✅ Cliente sem orçamentos - DELETE deve funcionar")
                        
                        # Testar DELETE neste cliente
                        print(f"   🗑️ Testando DELETE...")
                        delete_response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}", headers=headers, timeout=15)
                        print(f"   Status do DELETE: {delete_response.status_code}")
                        
                        if delete_response.status_code == 200:
                            print(f"   ✅ DELETE realizado com sucesso!")
                            print(f"   Resposta: {delete_response.text}")
                        else:
                            print(f"   ❌ Erro no DELETE: {delete_response.status_code}")
                            print(f"   Resposta: {delete_response.text}")
                        
                        break  # Testar apenas o primeiro cliente sem orçamentos
                        
                elif orcamentos_response.status_code == 404:
                    print(f"   ✅ Endpoint de orçamentos não encontrado ou cliente sem orçamentos")
                else:
                    print(f"   ❌ Erro ao verificar orçamentos: {orcamentos_response.status_code}")
                    print(f"   Resposta: {orcamentos_response.text}")
        else:
            print(f"❌ Erro ao listar clientes: {clientes_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    check_client_orcamentos()
    print("\n=== VERIFICAÇÃO CONCLUÍDA ===")