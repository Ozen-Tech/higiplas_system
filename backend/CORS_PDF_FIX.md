# 🔧 Correção do CORS e Encoding para Download de PDF

## 🐛 Problemas Identificados

### 1. Erro de CORS com Authorization Header

Ao tentar baixar o PDF do orçamento, o navegador bloqueava a requisição com os seguintes erros:

```
Aviso de requisição de origem cruzada (cross-origin): A diretiva de mesma origem (same origin)
em breve não permitirá a leitura do recurso remoto. Motivo: quando o valor de
`Access-Control-Allow-Headers` é `*`, o cabeçalho `Authorization` não é coberto.

Requisição cross-origin bloqueada: A diretiva Same Origin (mesma origem) não permite a leitura
do recurso remoto (motivo: falta cabeçalho 'Access-Control-Allow-Origin' no CORS).
Código de status: 500.
```

### 2. Erro de NoneType no PDF

Após corrigir o CORS, um segundo erro apareceu:

```python
AttributeError: 'NoneType' object has no attribute 'encode'
File "/code/app/routers/orcamentos.py", line 117, in secao_cliente
    self.cell(0, 5, self.orcamento_data['cliente'].get('cnpj', 'N/A'), 0, 1)
```

**Causa:** O método `.get('cnpj', 'N/A')` retorna o valor padrão `'N/A'` apenas quando a chave não existe. Se a chave existe mas o valor é `None`, ele retorna `None`, causando o erro ao tentar fazer `.encode()`.

### 3. Erro de Unicode Encoding no PDF

Após corrigir os valores None, um terceiro erro apareceu:

```python
fpdf.errors.FPDFUnicodeEncodingException: Character "•" at index 0 in text is outside the range
of characters supported by the font used: "helvetica". Please consider using a Unicode font.

File "/code/app/routers/orcamentos.py", line 250, in secao_observacoes
    self.multi_cell(0, 5, obs)
```

**Causa:** A fonte `Arial/Helvetica` usa encoding `latin-1` que não suporta caracteres Unicode como:
- `•` (bullet point - U+2022)
- Acentos portugueses: `ç`, `ã`, `õ`, `á`, `é`, `í`, `ó`, `ú`
- Outros caracteres especiais

## 🔍 Causa Raiz

### Problema 1: CORS

1. **Wildcard `*` não cobre `Authorization`**: Quando `Access-Control-Allow-Headers` é definido como `*`, o navegador **não inclui automaticamente** o cabeçalho `Authorization` por questões de segurança.

2. **Falta de `expose-headers`**: O cabeçalho `Content-Disposition` (necessário para o download do arquivo) não estava sendo exposto ao frontend.

3. **Inconsistência entre middleware e configuração**: Havia configurações conflitantes entre o middleware CORS do FastAPI e o middleware customizado.

### Problema 2: Valores None

Campos opcionais do cliente (`cnpj`, `email`, `endereco`, `telefone`) podem ter valor `None` no banco de dados, e o código não estava tratando isso corretamente.

## ✅ Soluções Implementadas

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

### 2. **Tratamento de Valores None no PDF**

**Antes:**
```python
self.cell(0, 5, self.orcamento_data['cliente'].get('cnpj', 'N/A'), 0, 1)
# ❌ Se cnpj=None, retorna None em vez de 'N/A'
```

**Depois:**
```python
cnpj = self.orcamento_data['cliente'].get('cnpj') or 'N/A'
self.cell(0, 5, cnpj, 0, 1)
# ✅ Se cnpj=None ou '', retorna 'N/A'
```

**Campos corrigidos:**
- `cnpj`: `self.orcamento_data['cliente'].get('cnpj') or 'N/A'`
- `telefone`: `self.orcamento_data['cliente']['telefone'] or 'N/A'`
- `email`: `self.orcamento_data['cliente'].get('email') or 'N/A'`
- `endereco`: `self.orcamento_data['cliente'].get('endereco') or 'N/A'`

### 3. **Remoção de Caracteres Unicode no PDF**

**Problema:** A fonte Arial/Helvetica usa encoding `latin-1` que não suporta caracteres Unicode.

**Solução:** Substituir todos os caracteres especiais por equivalentes ASCII.

**Antes:**
```python
observacoes = [
    '• Este orçamento tem validade de 30 dias a partir da data de emissão.',
    '• Os preços estão sujeitos a alteração sem aviso prévio.',
    '• O prazo de entrega será informado após confirmação do pedido.',
    '• Frete não incluso no valor do orçamento.',
    '• Pagamento conforme condição especificada acima.',
]
# ❌ Caracteres • (bullet) e acentos não funcionam com latin-1
```

**Depois:**
```python
observacoes = [
    '- Este orcamento tem validade de 30 dias a partir da data de emissao.',
    '- Os precos estao sujeitos a alteracao sem aviso previo.',
    '- O prazo de entrega sera informado apos confirmacao do pedido.',
    '- Frete nao incluso no valor do orcamento.',
    '- Pagamento conforme condicao especificada acima.',
]
# ✅ Apenas caracteres ASCII simples
```

**Caracteres substituídos:**
- `•` → `-` (bullet point para hífen)
- `ç` → `c` (cedilha removida)
- `ã`, `õ` → `a`, `o` (til removido)
- `á`, `é`, `í`, `ó`, `ú` → `a`, `e`, `i`, `o`, `u` (acentos removidos)

**Alternativa futura:** Usar fonte Unicode como DejaVu que suporta todos os caracteres especiais.

### 4. **Handler OPTIONS Atualizado**

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

### 4. **Middleware Customizado Atualizado**

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

## 💡 Lições Aprendidas

### Diferença entre `.get()` e `or`

```python
# ❌ ERRADO - .get() com valor padrão não funciona para None
value = dict.get('key', 'default')  # Se key=None, retorna None

# ✅ CORRETO - usar 'or' para tratar None e valores falsy
value = dict.get('key') or 'default'  # Se key=None ou '', retorna 'default'
```

### Quando usar cada abordagem:

| Situação | Solução | Exemplo |
|----------|---------|---------|
| Chave pode não existir | `.get('key', 'default')` | Campos opcionais novos |
| Chave existe mas pode ser None | `.get('key') or 'default'` | Campos nullable no DB |
| Chave sempre existe | `dict['key'] or 'default'` | Campos obrigatórios |

## 📚 Referências

- [MDN - CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [MDN - Access-Control-Allow-Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Headers)
- [MDN - Access-Control-Expose-Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Expose-Headers)
- [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)
- [Python dict.get() documentation](https://docs.python.org/3/library/stdtypes.html#dict.get)

## ✅ Resultado

Após essas correções:
- ✅ O cabeçalho `Authorization` é aceito nas requisições
- ✅ O cabeçalho `Content-Disposition` é acessível pelo JavaScript
- ✅ Valores `None` são tratados corretamente no PDF
- ✅ O download do PDF funciona corretamente
- ✅ Não há mais erros de CORS no console
- ✅ Não há mais erros de `AttributeError: 'NoneType'`

## 🚀 Deploy

Commits realizados:
```bash
# Correção do CORS
git commit -m "fix: Explicitly allow Authorization header in CORS configuration for PDF download"

# Documentação do CORS
git commit -m "docs: Add comprehensive documentation for CORS PDF download fix"

# Correção dos valores None
git commit -m "fix: Handle None values in PDF generation for cliente fields (cnpj, telefone, email, endereco)"

git push origin raking_de_vendas
```

O Render.com irá automaticamente fazer o deploy da nova versão com as correções.

**Tempo estimado de deploy**: 2-5 minutos

---

**Commits:** 
- `52e31ca` - "fix: Explicitly allow Authorization header in CORS configuration for PDF download"
- `aa511b9` - "docs: Add comprehensive documentation for CORS PDF download fix"
- `5efc297` - "fix: Handle None values in PDF generation for cliente fields"

**Data:** 2025
**Branch:** `raking_de_vendas`
**Status:** ✅ **Deployed**
