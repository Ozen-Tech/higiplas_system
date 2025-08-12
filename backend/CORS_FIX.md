# Correção de CORS para Produção no Render

## Problema Identificado
O frontend em `https://higiplas-system.vercel.app` estava sendo bloqueado ao tentar acessar `https://higiplas-system.onrender.com/clientes/1` devido à ausência do cabeçalho 'Access-Control-Allow-Origin'.

## Soluções Implementadas

### 1. Configuração Robusta de CORS
- Configurado `CORSMiddleware` com `allow_origins=["*"]` para permitir todas as origens
- Definido `allow_credentials=False` (obrigatório quando usando `*`)
- Configurado métodos permitidos: `GET, POST, PUT, DELETE, OPTIONS`
- Configurado headers permitidos: `*`
- Adicionado `expose_headers=["*"]`

### 2. Handler para Requisições OPTIONS
- Implementado handler específico para requisições preflight (`OPTIONS`)
- Retorna headers CORS corretos para todas as rotas

### 3. Configuração de Ambiente
- Adicionado `export RENDER=true` no `start.sh`
- Criado `render.yaml` com configurações específicas do Render

### 4. Middleware de Hosts Confiáveis
- Configurado `TrustedHostMiddleware` com `allowed_hosts=["*"]`

## Arquivos Modificados

1. **`app/main.py`**
   - Simplificada configuração de CORS
   - Removido middleware de debug complexo
   - Adicionado handler OPTIONS

2. **`start.sh`**
   - Adicionado `export RENDER=true`
   - Mantido configuração do Uvicorn com proxy headers

3. **`render.yaml`** (novo)
   - Configuração específica para deploy no Render

4. **`deploy.sh`** (novo)
   - Script automatizado para deploy

## Como Testar

### Localmente
```bash
# Testar endpoint de CORS
curl -X GET http://localhost:8000/cors-test -H "Origin: https://higiplas-system.vercel.app" -v

# Testar requisição preflight
curl -X OPTIONS http://localhost:8000/clientes/1 \
  -H "Origin: https://higiplas-system.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" -v
```

### Em Produção
```bash
# Testar endpoint de CORS
curl -X GET https://higiplas-system.onrender.com/cors-test -H "Origin: https://higiplas-system.vercel.app" -v

# Testar requisição preflight
curl -X OPTIONS https://higiplas-system.onrender.com/clientes/1 \
  -H "Origin: https://higiplas-system.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" -v
```

## Deploy

Para fazer o deploy das correções:

```bash
./deploy.sh
```

Ou manualmente:

```bash
git add .
git commit -m "fix: Correção de CORS para produção no Render"
git push origin main
```

## Verificação Pós-Deploy

1. Acesse: https://higiplas-system.onrender.com/cors-test
2. Verifique se retorna: `{"status": "CORS funcionando!", "environment": "production"}`
3. Teste o frontend em https://higiplas-system.vercel.app
4. Verifique se não há mais erros de CORS no console do navegador

## Headers CORS Esperados

As respostas devem incluir:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: *`
- `Access-Control-Expose-Headers: *`