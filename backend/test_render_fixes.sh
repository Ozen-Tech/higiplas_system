#!/bin/bash

echo "🔧 Testando correções no Render..."
echo "======================================"

BASE_URL="https://higiplas-system.onrender.com"
ORIGIN="https://higiplas-system.vercel.app"

echo "\n1. Testando /clientes (sem barra final):"
curl -s -o /dev/null -w "Status: %{http_code}\n" -H "Origin: $ORIGIN" "$BASE_URL/clientes"

echo "\n2. Testando /clientes/ (com barra final):"
curl -s -o /dev/null -w "Status: %{http_code}\n" -H "Origin: $ORIGIN" "$BASE_URL/clientes/"

echo "\n3. Testando /produtos/baixo-estoque (sem barra final):"
curl -s -o /dev/null -w "Status: %{http_code}\n" -H "Origin: $ORIGIN" "$BASE_URL/produtos/baixo-estoque"

echo "\n4. Testando /produtos/baixo-estoque/ (com barra final):"
curl -s -o /dev/null -w "Status: %{http_code}\n" -H "Origin: $ORIGIN" "$BASE_URL/produtos/baixo-estoque/"

echo "\n5. Testando /orcamentos (sem barra final):"
curl -s -o /dev/null -w "Status: %{http_code}\n" -H "Origin: $ORIGIN" "$BASE_URL/orcamentos"

echo "\n6. Testando /orcamentos/ (com barra final):"
curl -s -o /dev/null -w "Status: %{http_code}\n" -H "Origin: $ORIGIN" "$BASE_URL/orcamentos/"

echo "\n7. Testando rota raiz:"
curl -s -o /dev/null -w "Status: %{http_code}\n" -H "Origin: $ORIGIN" "$BASE_URL/"

echo "\n✅ Teste concluído!"
echo "Nota: Status 401 é esperado (não autenticado), 405 indica erro de método, 500 indica erro interno."