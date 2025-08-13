#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def check_null_orcamentos():
    """Verifica se há orçamentos com campos nulos que causam erro 500."""
    
    print("=== VERIFICAÇÃO DE ORÇAMENTOS COM CAMPOS NULOS ===")
    print(f"Timestamp: {datetime.now()}")
    
    base_url = "https://higiplas-system.onrender.com"
    
    # Dados de login
    login_data = {
        "username": "enzo.alverde@gmail.com",
        "password": "enzolilia"
    }
    
    try:
        # 1. Fazer login
        print("\n1. Fazendo login...")
        login_response = requests.post(
            f"{base_url}/users/token",
            data=login_data,
            timeout=30
        )
        
        if login_response.status_code != 200:
            print(f"   ❌ Erro no login: {login_response.status_code} - {login_response.text}")
            return
            
        token = login_response.json().get("access_token")
        if not token:
            print("   ❌ Token não encontrado na resposta")
            return
            
        print("   ✅ Login realizado com sucesso")
        
        # Headers com token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 2. Tentar acessar orçamentos com mais detalhes de erro
        print("\n2. Testando endpoint /orcamentos/...")
        orcamentos_response = requests.get(
            f"{base_url}/orcamentos/",
            headers=headers,
            timeout=30
        )
        
        print(f"   Status Code: {orcamentos_response.status_code}")
        print(f"   Headers: {dict(orcamentos_response.headers)}")
        
        if orcamentos_response.status_code == 200:
            orcamentos = orcamentos_response.json()
            print(f"   ✅ Sucesso! Encontrados {len(orcamentos)} orçamentos")
            
            # Verificar campos nulos
            problemas_encontrados = []
            for i, orcamento in enumerate(orcamentos):
                problemas = []
                
                if orcamento.get('condicao_pagamento') is None:
                    problemas.append('condicao_pagamento é None')
                    
                if orcamento.get('cliente') is None:
                    problemas.append('cliente é None')
                    
                if problemas:
                    problemas_encontrados.append({
                        'id': orcamento.get('id'),
                        'problemas': problemas
                    })
                    
            if problemas_encontrados:
                print(f"\n   ⚠️  Encontrados {len(problemas_encontrados)} orçamentos com problemas:")
                for problema in problemas_encontrados:
                    print(f"      Orçamento ID {problema['id']}: {', '.join(problema['problemas'])}")
            else:
                print("   ✅ Nenhum problema encontrado nos orçamentos")
                
        elif orcamentos_response.status_code == 500:
            print(f"   ❌ Erro 500: {orcamentos_response.text}")
            
            # Tentar extrair detalhes do erro de validação
            try:
                error_data = orcamentos_response.json()
                if 'detail' in error_data:
                    print(f"   🔍 Detalhes do erro: {error_data['detail']}")
                    
                    # Se for erro de validação, mostrar campos específicos
                    if isinstance(error_data['detail'], list):
                        for error in error_data['detail']:
                            if isinstance(error, dict) and 'loc' in error:
                                print(f"      Campo problemático: {error.get('loc')} - {error.get('msg')}")
                                
            except Exception as parse_error:
                print(f"   🔍 Erro ao parsear JSON: {parse_error}")
                print(f"   🔍 Resposta bruta: {orcamentos_response.text[:500]}")
                
        else:
            print(f"   ❌ Erro: {orcamentos_response.status_code} - {orcamentos_response.text}")
            
    except requests.exceptions.Timeout:
        print("   ⏰ Timeout na requisição")
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        import traceback
        print(f"   🔍 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    check_null_orcamentos()
    print("\n=== VERIFICAÇÃO CONCLUÍDA ===")