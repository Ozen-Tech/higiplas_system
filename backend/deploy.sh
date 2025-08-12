#!/usr/bin/env bash
set -e

echo "🚀 Iniciando deploy para o Render..."

# Verificar se estamos no diretório correto
if [ ! -f "app/main.py" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do backend"
    exit 1
fi

# Verificar se há mudanças não commitadas
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Há mudanças não commitadas. Commitando automaticamente..."
    git add .
    git commit -m "fix: Correção de CORS para produção no Render"
fi

# Push para o repositório
echo "📤 Fazendo push das mudanças..."
git push origin main

echo "✅ Deploy concluído!"
echo "🔗 Acesse: https://higiplas-system.onrender.com"
echo "🧪 Teste CORS: https://higiplas-system.onrender.com/cors-test"
echo ""
echo "📋 Para verificar se o CORS está funcionando:"
echo "curl -X GET https://higiplas-system.onrender.com/cors-test -H 'Origin: https://higiplas-system.vercel.app' -v"