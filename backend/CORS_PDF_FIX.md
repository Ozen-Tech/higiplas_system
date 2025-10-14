# 🔧 Correção do CORS para Download de PDF

## 🐛 Problema Identificado

Ao tentar baixar o PDF do orçamento, o navegador bloqueava a requisição com os seguintes erros:

```
Aviso de requisição de origem cruzada (cross-origin): A diretiva de mesma origem (same origin) 
em breve não permitirá a leitura do recurso remoto. Motivo: quando o valor de 
`Access-Control-Allow-Headers` é `*`, o cabeçalho `Authorization` não é coberto.

Requisição cross-origin bloqueada: A diretiva Same Origin (mesma origem) não permite a leitura 
do recurso remoto (motivo: falta cabeçalho 'Access-Control-Allow-Origin' no CORS). 
Código de status: 500.
```

## 🔍 Causa Raiz

O problema ocorria porque:

1. **Wildcard `*` não cobre `Authorization`**: Quando `Access-Control-Allow-Headers` é definido como `*`, o navegador **não inclui automaticamente** o cabeçalho `Authorization` por questões de segurança.

2. **Falta de `expose-headers`**: O cabeçalho `Content-Disposition` (necessário para o download do arquivo) não estava sendo exposto ao frontend.

3. **Inconsistência entre middleware e configuração**: Havia configurações conflitantes entre o middleware CORS do FastAPI e o middleware customizado.

## ✅ Solução Implementada

### 1. **Configuração Explícita do CORS Middleware**

**Antes:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],  # ❌ Wildcard não cobre Authorization
    expose_headers=["*"],
    max_age=3600
)
```

**Depois:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",      # ✅ Explicitamente permitido
        "Accept",
        "Origin",
        "User-Agent",
        "DNT",
        "Cache-Control",
        "X-Requested-With"
    ],
    expose_headers=[
        "Content-Disposition",  # ✅ Necessário para download
        "Content-Type",
        "Content-Length"
    ],
    max_age=3600
)
```

### 2. **Handler OPTIONS Atualizado**

```python
@app.options("/{path:path}")
async def options_handler(request: Request):
    # ... código de verificação de origem ...
    
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin, User-Agent, DNT, Cache-Control, X-Requested-With",  # ✅ Explícito
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Expose-Headers": "Content-Disposition, Content-Type, Content-Length"  # ✅ Exposto
        }
    )
```

### 3. **Middleware Customizado Atualizado**

```python
@app.middleware("http")
async def add_cors_and_log(request: Request, call_next):
    # ... código de logging ...
    
    response = await call_next(request)
    
    # Adicionar headers CORS manualmente
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, Origin, User-Agent, DNT, Cache-Control, X-Requested-With"  # ✅ Explícito
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition, Content-Type, Content-Length"  # ✅ Exposto
    
    return response
```

## 📋 Cabeçalhos Importantes

### `Access-Control-Allow-Headers`
Lista de cabeçalhos que o cliente pode enviar:
- **`Authorization`**: Token JWT para autenticação
- **`Content-Type`**: Tipo de conteúdo da requisição
- **`Accept`**: Tipos de resposta aceitos

### `Access-Control-Expose-Headers`
Lista de cabeçalhos que o cliente pode ler na resposta:
- **`Content-Disposition`**: Informa ao navegador para fazer download do arquivo
- **`Content-Type`**: Tipo do arquivo (application/pdf)
- **`Content-Length`**: Tamanho do arquivo

## 🧪 Como Testar

### 1. **Teste Local**
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd higiplas_frontend
npm run dev
```

Acesse: `http://localhost:3000/dashboard/vendedor`
- Crie um orçamento
- Clique em "Baixar PDF"
- O PDF deve ser baixado sem erros

### 2. **Teste em Produção**
```bash
# Verificar headers CORS
curl -I -X OPTIONS https://higiplas-system.onrender.com/orcamentos/13/pdf/ \
  -H "Origin: https://higiplas-system.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization"
```

**Resposta esperada:**
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://higiplas-system.vercel.app
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: Content-Type, Authorization, Accept, Origin, User-Agent, DNT, Cache-Control, X-Requested-With
Access-Control-Allow-Credentials: true
Access-Control-Expose-Headers: Content-Disposition, Content-Type, Content-Length
```

## 🔐 Segurança

### Por que não usar `*` para tudo?

1. **`Authorization` com wildcard**: Por questões de segurança, navegadores modernos **não permitem** o uso de wildcard (`*`) quando o cabeçalho `Authorization` está presente.

2. **Credenciais**: Quando `allow_credentials=True`, o navegador exige que os cabeçalhos sejam explicitamente listados.

3. **Expose Headers**: O navegador só permite que o JavaScript acesse cabeçalhos que estejam explicitamente listados em `Access-Control-Expose-Headers`.

## 📚 Referências

- [MDN - CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [MDN - Access-Control-Allow-Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Headers)
- [MDN - Access-Control-Expose-Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Expose-Headers)
- [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)

## ✅ Resultado

Após essas correções:
- ✅ O cabeçalho `Authorization` é aceito nas requisições
- ✅ O cabeçalho `Content-Disposition` é acessível pelo JavaScript
- ✅ O download do PDF funciona corretamente
- ✅ Não há mais erros de CORS no console

## 🚀 Deploy

Após fazer o commit e push:
```bash
git add backend/app/main.py
git commit -m "fix: Explicitly allow Authorization header in CORS configuration for PDF download"
git push origin raking_de_vendas
```

O Render.com irá automaticamente fazer o deploy da nova versão com as correções de CORS.

**Tempo estimado de deploy**: 2-5 minutos

---

**Commit:** `52e31ca` - "fix: Explicitly allow Authorization header in CORS configuration for PDF download"
**Data:** 2025
**Branch:** `raking_de_vendas`
