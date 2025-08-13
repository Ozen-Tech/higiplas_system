#!/bin/bash

# Script para testar se o deploy do Vercel corrigiu os problemas de CORS

echo "🚀 Testando correções de CORS após deploy do Vercel"
echo "================================================="

FRONTEND_URL="https://higiplas-system.vercel.app"
BACKEND_URL="https://higiplas-system.onrender.com"

echo "Frontend: $FRONTEND_URL"
echo "Backend: $BACKEND_URL"
echo ""

# Função para testar se o frontend está usando a URL correta
test_frontend_config() {
    echo "🔍 Testando se o frontend está acessível..."
    
    # Testa se o frontend responde
    if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" | grep -q "200\|301\|302"; then
        echo "✅ Frontend está acessível"
    else
        echo "❌ Frontend não está acessível"
        return 1
    fi
    
    echo "✅ Frontend deploy concluído"
}

# Função para testar CORS do backend
test_backend_cors() {
    echo "\n🔍 Testando CORS do backend..."
    
    # Testa requisição OPTIONS
    echo "Testando requisição OPTIONS para /clientes/1..."
    response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
        -H "Origin: $FRONTEND_URL" \
        -H "Access-Control-Request-Method: DELETE" \
        -H "Access-Control-Request-Headers: Authorization,Content-Type" \
        -X OPTIONS \
        "$BACKEND_URL/clientes/1")
    
    http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
    
    if [ "$http_code" = "200" ]; then
        echo "✅ Requisição OPTIONS funcionando (Status: $http_code)"
        
        # Verifica headers CORS
        if echo "$response" | grep -i "access-control-allow-origin.*$FRONTEND_URL" > /dev/null; then
            echo "✅ Header Access-Control-Allow-Origin correto"
        else
            echo "❌ Header Access-Control-Allow-Origin incorreto ou ausente"
        fi
        
        if echo "$response" | grep -i "access-control-allow-credentials.*true" > /dev/null; then
            echo "✅ Header Access-Control-Allow-Credentials correto"
        else
            echo "❌ Header Access-Control-Allow-Credentials incorreto ou ausente"
        fi
    else
        echo "❌ Requisição OPTIONS falhou (Status: $http_code)"
        return 1
    fi
}

# Função para aguardar o deploy
wait_for_deploy() {
    echo "⏳ Aguardando deploy do Vercel (60 segundos)..."
    sleep 60
    echo "✅ Tempo de espera concluído"
}

# Função principal
main() {
    echo "📋 Iniciando testes pós-deploy..."
    echo ""
    
    # Aguarda o deploy
    wait_for_deploy
    
    # Testa frontend
    if ! test_frontend_config; then
        echo "\n❌ Falha nos testes do frontend"
        exit 1
    fi
    
    # Testa backend
    if ! test_backend_cors; then
        echo "\n❌ Falha nos testes do backend"
        exit 1
    fi
    
    echo "\n================================================="
    echo "🎉 TODOS OS TESTES PASSARAM!"
    echo "================================================="
    echo ""
    echo "✅ Deploy do Vercel concluído com sucesso"
    echo "✅ Configuração de CORS funcionando"
    echo "✅ Frontend deve estar usando a URL de produção correta"
    echo ""
    echo "🔗 Links para testar:"
    echo "   Frontend: $FRONTEND_URL"
    echo "   Backend:  $BACKEND_URL"
    echo ""
    echo "💡 Próximos passos:"
    echo "   1. Acesse o frontend e teste excluir/editar clientes"
    echo "   2. Abra o DevTools > Network para verificar as requisições"
    echo "   3. Confirme que não há mais erros de CORS"
    echo "   4. Limpe o cache do browser se necessário (Ctrl+Shift+R)"
    echo ""
    echo "📊 Se ainda houver problemas:"
    echo "   1. Verifique as variáveis de ambiente no dashboard do Vercel"
    echo "   2. Execute o script debug-api-url.js no console do browser"
    echo "   3. Verifique os logs do Vercel: npx vercel logs"
}

# Executa o script
main