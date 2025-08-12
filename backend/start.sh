#!/usr/bin/env bash
set -e

# Define que estamos rodando no Render
export RENDER=true

echo "==> [START] Verificando e criando superusuário..."
# Python agora encontrará 'app' por causa do PYTHONPATH no Dockerfile
python app/create_superuser.py
echo "==> [START] Verificação do superusuário concluída."

echo "==> [START] Iniciando servidor Uvicorn..."
echo "==> [START] Configuração CORS para produção ativada"
exec uvicorn --host 0.0.0.0 --port 10000 --proxy-headers --forwarded-allow-ips='*' app.main:app