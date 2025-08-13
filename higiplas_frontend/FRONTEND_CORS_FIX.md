# 🔧 Correção de Problemas de CORS no Frontend

## 🚨 Problema Identificado

O frontend está apresentando erros de CORS e "failed to fetch" ao tentar excluir e editar clientes:

```
Access to fetch at 'https://higiplas-system.onrender.com/clientes/1' from origin 'https://higiplas-system.vercel.app' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
GET https://higiplas-system.onrender.com/clientes/1 net::ERR_FAILED 500 (Internal Server Error)
```

## 🔍 Diagnóstico

✅ **Backend está funcionando corretamente** - Todos os testes de CORS passaram
❌ **Frontend não está usando a URL de produção correta**

### Testes Realizados no Backend

- ✅ Requisições OPTIONS (preflight) para GET, DELETE, PUT
- ✅ Requisições reais com headers CORS corretos
- ✅ Configuração de CORS permite origem `https://higiplas-system.vercel.app`
- ✅ Headers `Access-Control-Allow-Credentials: true` presentes

## 🛠️ Soluções Implementadas

### 1. Arquivo `.env.production` Criado

```bash
NEXT_PUBLIC_API_URL=https://higiplas-system.onrender.com
```

### 2. Arquivo `vercel.json` Criado

Força o Vercel a usar as variáveis de ambiente corretas:

```json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://higiplas-system.onrender.com"
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_API_URL": "https://higiplas-system.onrender.com"
    }
  }
}
```

### 3. Script de Debug Criado

Arquivo `debug-api-url.js` para testar no console do browser.

## 📋 Próximos Passos

### 1. Commit e Push das Alterações

```bash
cd /Users/ozen/higiplas_system/higiplas_frontend
git add .
git commit -m "fix: configure production API URL for Vercel deployment"
git push origin main
```

### 2. Forçar Redeploy no Vercel

**Opção A: Via Dashboard do Vercel**
1. Acesse https://vercel.com/dashboard
2. Encontre o projeto `higiplas-system`
3. Vá em "Deployments"
4. Clique em "Redeploy" no último deployment

**Opção B: Via CLI (se instalado)**
```bash
npx vercel --prod
```

**Opção C: Trigger via Git**
```bash
# Fazer um commit vazio para triggerar redeploy
git commit --allow-empty -m "trigger: force Vercel redeploy with correct env vars"
git push origin main
```

### 3. Verificar Variáveis de Ambiente no Vercel

1. Acesse o projeto no dashboard do Vercel
2. Vá em "Settings" > "Environment Variables"
3. Adicione/verifique:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://higiplas-system.onrender.com`
   - **Environments**: Production, Preview, Development

### 4. Testar Após Redeploy

1. Limpe o cache do browser (Ctrl+Shift+R ou Cmd+Shift+R)
2. Abra o DevTools > Network tab
3. Tente excluir/editar um cliente
4. Verifique se as requisições estão indo para `https://higiplas-system.onrender.com`

### 5. Debug no Browser (se necessário)

1. Abra o console do browser na página do frontend
2. Cole o conteúdo do arquivo `debug-api-url.js`
3. Execute e verifique os logs

## 🔧 Comandos de Troubleshooting

### Verificar Build Local
```bash
cd /Users/ozen/higiplas_system/higiplas_frontend
npm run build
npm run start
```

### Testar Localmente com Produção
```bash
# Definir variável de ambiente temporariamente
NEXT_PUBLIC_API_URL=https://higiplas-system.onrender.com npm run dev
```

### Verificar Logs do Vercel
```bash
npx vercel logs [deployment-url]
```

## 📊 Status Esperado Após Correção

- ✅ Requisições do frontend vão para `https://higiplas-system.onrender.com`
- ✅ Headers CORS corretos nas respostas
- ✅ Exclusão de clientes funciona sem erros
- ✅ Edição de clientes funciona sem loops de erro
- ✅ Todas as operações CRUD funcionam normalmente

## 🚨 Se o Problema Persistir

1. **Verificar cache do browser**: Teste em aba anônima
2. **Verificar DNS**: `nslookup higiplas-system.onrender.com`
3. **Verificar certificado SSL**: Acesse a URL diretamente
4. **Verificar logs do Render**: Procure por erros 500 reais
5. **Testar com token válido**: Use um token de autenticação real

---

**Criado em**: $(date)
**Status**: Aguardando redeploy do Vercel
**Próxima ação**: Commit e push das alterações