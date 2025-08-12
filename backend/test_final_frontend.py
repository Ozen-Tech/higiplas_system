#!/usr/bin/env python3

import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import os

# Configurações
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"
EMAIL = "test@higiplas.com"
PASSWORD = "test123"

def test_frontend_delete_with_string_address():
    print("🔍 Testando DELETE no frontend com endereço string...")
    
    # Configurar Chrome em modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = None
    cliente_id = None
    
    try:
        # 1. Primeiro, criar um cliente via API com endereço string
        print("📝 Criando cliente via API...")
        
        login_data = {"username": EMAIL, "password": PASSWORD}
        login_response = requests.post(f"{BACKEND_URL}/users/token", data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        
        # Criar cliente com endereço objeto primeiro
        timestamp = str(int(time.time()))
        cnpj_unico = f"123456789{timestamp[-5:]}"
        
        cliente_data = {
            "nome": "Cliente Teste Frontend Delete",
            "cpf_cnpj": cnpj_unico,
            "email": "cliente.frontend.delete@teste.com",
            "telefone": "(11) 99999-9999",
            "tipo_pessoa": "JURIDICA",
            "endereco": {
                "logradouro": "Rua Teste Frontend",
                "numero": "456",
                "complemento": "Sala 1",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01000-000"
            },
            "empresa_vinculada": "HIGIPLAS"
        }
        
        create_response = requests.post(f"{BACKEND_URL}/clientes/", headers=headers, json=cliente_data)
        
        if create_response.status_code != 200:
            print(f"❌ Erro ao criar cliente: {create_response.text}")
            return
        
        cliente_criado = create_response.json()
        cliente_id = cliente_criado["id"]
        print(f"✅ Cliente criado com ID: {cliente_id}")
        
        # Modificar endereço para string no banco (simulando o problema)
        from sqlalchemy import create_engine, text
        from dotenv import load_dotenv
        
        load_dotenv('.env.local')
        DATABASE_URL = os.getenv('DATABASE_URL')
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            endereco_string = "Rua Problema, 789, Recanto dos vinhais, São Luís, MA, 65070011"
            conn.execute(
                text("UPDATE clientes SET endereco = :endereco WHERE id = :id"),
                {"endereco": endereco_string, "id": cliente_id}
            )
            conn.commit()
            print(f"✅ Endereço modificado para string: {endereco_string}")
        
        # 2. Agora testar o frontend
        print("\n🌐 Iniciando teste no frontend...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"{FRONTEND_URL}/login")
        
        # Login no frontend
        print("🔐 Fazendo login no frontend...")
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_input = driver.find_element(By.NAME, "password")
        
        email_input.send_keys(EMAIL)
        password_input.send_keys(PASSWORD)
        
        login_button = driver.find_element(By.TYPE, "submit")
        login_button.click()
        
        # Aguardar redirecionamento
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard")
        )
        print("✅ Login realizado com sucesso")
        
        # Navegar para página de clientes
        print("📋 Navegando para página de clientes...")
        driver.get(f"{FRONTEND_URL}/dashboard/clientes")
        
        # Aguardar carregamento da página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        # Verificar se há erros no console
        logs = driver.get_log('browser')
        parsing_errors = [log for log in logs if 'Falha ao analisar o JSON do endereço' in log.get('message', '')]
        
        if parsing_errors:
            print(f"❌ Ainda há erros de parsing: {len(parsing_errors)} erros encontrados")
            for error in parsing_errors[:3]:  # Mostrar apenas os primeiros 3
                print(f"   - {error['message']}")
        else:
            print("✅ Nenhum erro de parsing de endereço encontrado!")
        
        # Procurar o botão de delete do cliente criado
        print(f"🔍 Procurando cliente ID {cliente_id} na tabela...")
        
        # Aguardar um pouco para garantir que a tabela carregou
        time.sleep(2)
        
        # Procurar por botões de delete (ícones de lixeira)
        delete_buttons = driver.find_elements(By.CSS_SELECTOR, "button[title*='Excluir'], button[aria-label*='delete'], .trash-icon, [data-testid*='delete']")
        
        if not delete_buttons:
            # Tentar encontrar por outros seletores
            delete_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'delete') or contains(text(), 'Excluir')]")
        
        print(f"🗑️ Encontrados {len(delete_buttons)} botões de delete")
        
        if delete_buttons:
            # Clicar no primeiro botão de delete (assumindo que é nosso cliente de teste)
            print("🖱️ Clicando no botão de delete...")
            delete_buttons[0].click()
            
            # Aguardar possível modal de confirmação
            try:
                confirm_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirmar') or contains(text(), 'Sim') or contains(text(), 'Delete')]"))
                )
                confirm_button.click()
                print("✅ Confirmação de delete clicada")
            except TimeoutException:
                print("ℹ️ Nenhum modal de confirmação encontrado")
            
            # Aguardar um pouco para a operação completar
            time.sleep(3)
            
            # Verificar logs novamente após a operação
            logs_after = driver.get_log('browser')
            new_errors = [log for log in logs_after if log not in logs and 'error' in log.get('level', '').lower()]
            
            if new_errors:
                print(f"❌ Novos erros após delete: {len(new_errors)}")
                for error in new_errors[:3]:
                    print(f"   - {error['message']}")
            else:
                print("✅ Nenhum erro durante operação de delete!")
            
            print("✅ Teste de delete no frontend concluído")
        else:
            print("❌ Nenhum botão de delete encontrado")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
    
    finally:
        if driver:
            driver.quit()
        
        # Limpar cliente de teste se ainda existir
        if cliente_id:
            try:
                delete_response = requests.delete(f"{BACKEND_URL}/clientes/{cliente_id}", headers=headers)
                if delete_response.status_code == 200:
                    print(f"🧹 Cliente de teste {cliente_id} removido")
            except Exception as cleanup_error:
                print(f"⚠️ Erro ao limpar cliente de teste: {cleanup_error}")

if __name__ == "__main__":
    test_frontend_delete_with_string_address()