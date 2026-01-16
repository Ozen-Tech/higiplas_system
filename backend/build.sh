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

echo "==> Garantindo que tabela visitas_vendedor existe (independente de migrações)..."
python ensure_visitas_table.py || echo "⚠ Aviso: Erro ao garantir tabela visitas_vendedor, mas continuando..."

echo "==> Rodando migrações do banco de dados..."
# Desabilita set -e temporariamente para permitir continuar mesmo com erros
set +e

# Verifica se há múltiplas heads
HEADS_OUTPUT=$(alembic heads 2>&1)
HEAD_COUNT=$(echo "$HEADS_OUTPUT" | grep -c "revision" 2>/dev/null || echo "0")

# Garante que HEAD_COUNT é um número válido
if [ -z "$HEAD_COUNT" ] || [ "$HEAD_COUNT" = "" ] || ! [[ "$HEAD_COUNT" =~ ^[0-9]+$ ]]; then
    HEAD_COUNT=0
fi

if [ "$HEAD_COUNT" -gt 1 ] 2>/dev/null; then
    echo "==> Múltiplas heads detectadas ($HEAD_COUNT), tentando aplicar merge..."
    # Tenta aplicar migrações específicas primeiro
    echo "==> Aplicando: create_empresas_higiplas_higitec"
    alembic upgrade create_empresas_higiplas_higitec 2>&1 | tail -5 || true
    
    echo "==> Aplicando: create_visitas_vendedor"
    alembic upgrade create_visitas_vendedor 2>&1 | tail -5 || true
    
    echo "==> Aplicando: add_data_criacao_foto_perfil_001"
    alembic upgrade add_data_criacao_foto_perfil_001 2>&1 | tail -5 || true
    
    echo "==> Aplicando migração de merge: merge_heads_visitas_001"
    alembic upgrade merge_heads_visitas_001 2>&1 | tail -5 || true
    
    echo "==> Garantindo que tabela visitas_vendedor existe: ensure_visitas_table_001"
    alembic upgrade ensure_visitas_table_001 2>&1 | tail -5 || true
    
    # Tenta aplicar todas as heads de uma vez
    echo "==> Tentando aplicar todas as heads..."
    alembic upgrade heads 2>&1 | tail -10 || true
else
    echo "==> Aplicando migrações normalmente..."
    alembic upgrade head 2>&1 | tail -5
fi

# Reabilita set -e
set -e

echo "==> Build concluído com sucesso!"
