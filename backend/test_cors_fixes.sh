#!/bin/bash

echo "=== Testando correções de CORS no Render ==="
echo

BASE_URL="https://higiplas-system.onrender.com"
ORIGIN="https://higiplas-system.vercel.app"

echo "1. Testando requisição OPTIONS (preflight) para /clientes/2:"
curl -s -X OPTIONS \
  -H "Origin: $ORIGIN" \
  -H "Access-Control-Request-Method: DELETE" \
  -H "Access-Control-Request-Headers: Authorization,Content-Type" \
  -w "Status: %{http_code}\n" \
  "$BASE_URL/clientes/2" | grep -E "(access-control|Status)"
echo

echo "2. Testando requisição OPTIONS (preflight) para /orcamentos/:"
curl -s -X OPTIONS \
  -H "Origin: $ORIGIN" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization,Content-Type" \
  -w "Status: %{http_code}\n" \
  "$BASE_URL/orcamentos/" | grep -E "(access-control|Status)"
echo

echo "3. Testando DELETE /clientes/2 (deve retornar 401 com CORS):"
curl -s -X DELETE \
  -H "Origin: $ORIGIN" \
  -H "Authorization: Bearer fake-token" \
  -w "Status: %{http_code}\n" \
  -D - \
  "$BASE_URL/clientes/2" | grep -E "(access-control|Status|HTTP)"
echo

echo "4. Testando GET /orcamentos/ (deve retornar 401 com CORS):"
curl -s -X GET \
  -H "Origin: $ORIGIN" \
  -H "Authorization: Bearer fake-token" \
  -w "Status: %{http_code}\n" \
  -D - \
  "$BASE_URL/orcamentos/" | grep -E "(access-control|Status|HTTP)"
echo

echo "=== Teste concluído ==="
echo "Todos os testes devem mostrar:"
echo "- Status 200 para OPTIONS (preflight)"
echo "- Status 401 para requisições autenticadas com token inválido"
echo "- Cabeçalhos access-control-allow-origin presentes"
echo "- Cabeçalhos access-control-allow-credentials: true"