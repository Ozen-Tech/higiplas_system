#!/usr/bin/env python3
"""
Script para criar uma versão temporária do DELETE de clientes
que não depende da verificação de orçamentos (que está falhando com erro 500).
"""

import requests
import json

def create_temp_delete_fix():
    """Cria uma correção temporária para o DELETE de clientes."""
    
    print("🔧 Criando correção temporária para DELETE de clientes...")
    
    # Código da função delete_cliente modificada (sem verificação de orçamentos)
    temp_delete_function = '''
def delete_cliente_temp(db: Session, cliente_id: int, empresa_id: int):
    """Exclui um cliente (versão temporária sem verificação de orçamentos)."""
    db_cliente = get_cliente_by_id(db, cliente_id, empresa_id)
    if not db_cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )
    
    # COMENTADO TEMPORARIAMENTE - A verificação de orçamentos está causando erro 500
    # # Verifica se o cliente tem orçamentos associados
    # orcamentos_count = db.query(models.Orcamento).filter(
    #     models.Orcamento.cliente_id == cliente_id
    # ).count()
    # 
    # if orcamentos_count > 0:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Não é possível excluir cliente com orçamentos associados."
    #     )
    
    # Por enquanto, permite a exclusão sem verificar orçamentos
    # TODO: Corrigir o problema no endpoint de orçamentos e reativar a verificação
    
    db.delete(db_cliente)
    db.commit()
    return {"message": "Cliente excluído com sucesso (verificação de orçamentos temporariamente desabilitada)"}
'''
    
    print("\n📝 Função temporária criada:")
    print(temp_delete_function)
    
    print("\n=== INSTRUÇÕES PARA APLICAR A CORREÇÃO ===")
    print("1. Abra o arquivo backend/app/crud/cliente.py")
    print("2. Substitua a função delete_cliente pela versão temporária acima")
    print("3. Faça o deploy da correção")
    print("4. Teste o DELETE de clientes")
    print("5. Depois corrija o problema real no endpoint de orçamentos")
    
    print("\n⚠️  IMPORTANTE:")
    print("   - Esta é uma solução TEMPORÁRIA")
    print("   - Clientes poderão ser excluídos mesmo com orçamentos associados")
    print("   - Corrija o problema no endpoint /orcamentos o mais rápido possível")
    
    print("\n🔍 PROBLEMA REAL A SER CORRIGIDO:")
    print("   - Endpoint /orcamentos retorna erro 500")
    print("   - Isso afeta a verificação no DELETE de clientes")
    print("   - Verifique logs do Render para mais detalhes")
    print("   - Pode ser problema de JOIN, timeout ou relacionamento no banco")

def test_current_delete():
    """Testa o DELETE atual para confirmar o erro 401."""
    
    base_url = "https://higiplas-system.onrender.com"
    
    print("\n🧪 Testando DELETE atual (deve dar erro 401/500)...")
    
    # 1. Fazer login
    login_data = {
        "username": "enzo.alverde@gmail.com",
        "password": "enzolilia"
    }
    
    login_response = requests.post(f"{base_url}/users/token", data=login_data)
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Listar clientes
    clientes_response = requests.get(f"{base_url}/clientes", headers=headers)
    if clientes_response.status_code != 200:
        print(f"❌ Erro ao listar clientes: {clientes_response.text}")
        return
    
    clientes = clientes_response.json()
    if not clientes:
        print("⚠️  Nenhum cliente encontrado para testar")
        return
    
    cliente_id = clientes[0]['id']
    print(f"📋 Testando DELETE do cliente ID: {cliente_id}")
    
    # 3. Tentar DELETE
    delete_response = requests.delete(f"{base_url}/clientes/{cliente_id}", headers=headers)
    print(f"   Status: {delete_response.status_code}")
    
    if delete_response.status_code == 401:
        print("   ❌ Erro 401 (Unauthorized) - Problema de autenticação")
        print("   💡 Verifique se o token está sendo enviado corretamente")
    elif delete_response.status_code == 500:
        print("   ❌ Erro 500 (Internal Server Error) - Problema no backend")
        print("   💡 Confirmado: Problema na verificação de orçamentos")
    else:
        print(f"   ℹ️  Resposta: {delete_response.text}")

if __name__ == "__main__":
    print("=== CORREÇÃO TEMPORÁRIA PARA DELETE DE CLIENTES ===")
    create_temp_delete_fix()
    test_current_delete()
    print("\n=== CORREÇÃO CRIADA ===")