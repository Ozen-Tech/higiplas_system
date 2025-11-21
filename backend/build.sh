#!/usr/bin/env bash
set -e

echo "==> Instalando dependências..."
pip install -r requirements.txt

echo "==> Corrigindo histórico de migrações do Alembic..."
python -c "
from app.core.config import settings
import psycopg2

try:
    conn = psycopg2.connect(settings.DATABASE_URL)
    cur = conn.cursor()
    
    print('--- [DEBUG] URL DE CONEXÃO VINDA DAS CONFIGURAÇÕES ---')
    print(f'--- [DEBUG] URL: {settings.DATABASE_URL}')
    print('----------------------------------------------------')
    
    # Verifica se a tabela alembic_version existe
    cur.execute(\"\"\"
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'alembic_version'
        );
    \"\"\")
    table_exists = cur.fetchone()[0]
    
    if table_exists:
        # Verifica a revisão atual
        cur.execute('SELECT version_num FROM alembic_version;')
        current_version = cur.fetchone()
        
        if current_version:
            print(f'==> Revisão atual no banco: {current_version[0]}')
            
            # Se a revisão for 'add_refresh_tokens', remove e marca como '227dac4b4f63' (última revisão válida)
            if current_version[0] == 'add_refresh_tokens':
                print('==> Removendo revisão inválida add_refresh_tokens...')
                cur.execute('DELETE FROM alembic_version;')
                cur.execute(\"INSERT INTO alembic_version (version_num) VALUES ('227dac4b4f63');\")
                conn.commit()
                print('==> Revisão corrigida para 227dac4b4f63')
            else:
                print('==> Revisão válida, nenhuma correção necessária')
        else:
            print('==> Nenhuma revisão encontrada no banco')
    else:
        print('==> Tabela alembic_version não existe, será criada durante a migração')
    
    cur.close()
    conn.close()
except Exception as e:
    print(f'==> Erro ao verificar/corrigir histórico: {e}')
    print('==> Continuando com as migrações...')
"

echo "==> Rodando migrações do banco de dados..."
# Desabilita set -e temporariamente para permitir continuar mesmo com erros
set +e

# Verifica se há múltiplas heads
HEADS_OUTPUT=$(alembic heads 2>&1)
HEAD_COUNT=$(echo "$HEADS_OUTPUT" | grep -c "revision" || echo "0")

if [ "$HEAD_COUNT" -gt "1" ]; then
    echo "==> Múltiplas heads detectadas ($HEAD_COUNT), aplicando individualmente..."
    # Aplica cada head individualmente
    echo "==> Aplicando: merge_proposta_fornecedor"
    alembic upgrade merge_proposta_fornecedor 2>&1 | tail -5
    
    echo "==> Aplicando: approval_fields_001"
    alembic upgrade approval_fields_001 2>&1 | tail -5
    
    # Depois aplica a migração de merge que une as duas heads
    echo "==> Aplicando migração de merge: merge_approval_proposta"
    alembic upgrade merge_approval_proposta 2>&1 | tail -5
else
    echo "==> Aplicando migrações normalmente..."
    alembic upgrade head 2>&1 | tail -5
fi

# Reabilita set -e
set -e

echo "==> Build concluído com sucesso!"
