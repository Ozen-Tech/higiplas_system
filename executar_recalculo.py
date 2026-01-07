#!/usr/bin/env python3
"""
Script para executar o endpoint de recálculo de preços via API
"""
import requests
import sys

# Configurações
BASE_URL = "https://higiplas-system.onrender.com"
EMAIL = "enzo.alverde@gmail.com"
SENHA = "senha123"

def fazer_login():
    """Faz login e retorna o token"""
    url = f"{BASE_URL}/users/token"
    data = {
        "username": EMAIL,
        "password": SENHA
    }
    
    print("🔐 Fazendo login...")
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print(f"❌ Erro no login: {response.status_code}")
        print(response.text)
        return None

def recalcular_precos(token):
    """Executa o endpoint de recálculo de preços"""
    url = f"{BASE_URL}/orcamentos/admin/recalcular-precos"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n🔄 Executando recálculo de ranges de preços...")
    response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        resultado = response.json()
        print("\n✅ Recálculo concluído com sucesso!")
        print(f"   - Orçamentos processados: {resultado.get('orcamentos_processados', 0)}")
        print(f"   - Clientes processados: {resultado.get('clientes_processados', 0)}")
        print(f"   - Registros atualizados: {resultado.get('registros_precos_atualizados', 0)}")
        return True
    else:
        print(f"\n❌ Erro no recálculo: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    # Fazer login
    token = fazer_login()
    
    if not token:
        print("\n❌ Não foi possível fazer login. Verifique email e senha.")
        sys.exit(1)
    
    # Executar recálculo
    sucesso = recalcular_precos(token)
    
    if sucesso:
        print("\n🎉 Processo concluído! Os ranges de preços agora devem aparecer no frontend.")
    else:
        sys.exit(1)

