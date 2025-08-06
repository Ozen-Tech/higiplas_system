#!/usr/bin/env bash
# Exit on error
set -e

echo "==> Instalando dependências..."
pip install -r requirements.txt

echo "==> Rodando migrações do banco de dados..."
alembic upgrade head

echo "==> Build concluído com sucesso!"