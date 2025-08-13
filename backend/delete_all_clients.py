import requests
import os

# --- Configurações ---
BASE_URL = "https://higiplas-backend.onrender.com"
AUTH_URL = f"{BASE_URL}/auth/token"
CLIENTES_URL = f"{BASE_URL}/clientes"
USERNAME = "enzo.alverde@gmail.com"
PASSWORD = "enzolilia"

def get_auth_token():
    """Autentica e obtém o token de acesso."""
    try:
        response = requests.post(AUTH_URL, data={"username": USERNAME, "password": PASSWORD})
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Erro ao autenticar: {e}")
        if e.response:
            print(f"Detalhes do erro: {e.response.text}")
        return None

def get_all_clients(token):
    """Obtém a lista de todos os clientes."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(CLIENTES_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao listar clientes: {e}")
        return []

def delete_client(token, client_id):
    """Exclui um cliente específico."""
    headers = {"Authorization": f"Bearer {token}"}
    delete_url = f"{CLIENTES_URL}/{client_id}"
    try:
        response = requests.delete(delete_url, headers=headers)
        response.raise_for_status()
        print(f"Cliente com ID {client_id} excluído com sucesso.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao excluir cliente com ID {client_id}: {e}")
        if e.response:
            print(f"Detalhes do erro: {e.response.text}")
        return False

def main():
    """Função principal para excluir todos os clientes."""
    token = get_auth_token()
    if not token:
        return

    clients = get_all_clients(token)
    if not clients:
        print("Nenhum cliente encontrado para excluir.")
        return

    print(f"Encontrados {len(clients)} clientes. Iniciando exclusão...")

    for client in clients:
        delete_client(token, client["id"])

    print("\nExclusão de todos os clientes concluída.")

if __name__ == "__main__":
    main()