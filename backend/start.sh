#!/bin/bash

# Este script executa tarefas que DEVEM acontecer toda vez que o container inicia,
# ANTES do servidor web principal.

# 1. Garante que as tabelas existem (create_all é seguro de rodar múltiplas vezes)
echo "==> Executando prestart.py para garantir que as tabelas existem..."
python /code/app/prestart.py
echo "==> prestart.py concluído."

# 2. Garante que o superusuário existe (a lógica interna já previne recriação)
echo "==> Executando create_superuser.py..."
python /code/app/create_superuser.py
echo "==> create_superuser.py concluído."

# 3. Inicia o servidor Uvicorn (este deve ser o ÚLTIMO comando)
echo "==> Iniciando o servidor Uvicorn..."
exec uvicorn --host 0.0.0.0 --port 10000 --proxy-headers --forwarded-allow-ips='*' app.main:app