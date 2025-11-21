# 🏭 Higiplas System

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/next.js-15+-black.svg)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/postgresql-13+-blue.svg)](https://postgresql.org)

## 📋 Descrição

O **Higiplas System** é um sistema completo de gestão de estoque e movimentações desenvolvido especificamente para empresas do setor industrial. O sistema oferece funcionalidades avançadas para:

- 📊 **Gestão de Estoque**: Controle completo de produtos, quantidades e valores
- 📄 **Processamento de PDFs**: Extração automática de dados de notas fiscais
- 🔄 **Movimentações**: Registro de entradas e saídas de produtos
- 👥 **Gestão de Clientes**: Cadastro e controle de clientes e fornecedores
- 💰 **Orçamentos**: Criação e gestão de orçamentos
- 📈 **Relatórios**: Análises detalhadas de vendas e estoque
- 🤖 **Automação**: Processamento inteligente de documentos fiscais

### 🎯 Principais Funcionalidades

- **Dashboard Interativo**: Interface moderna e responsiva
- **Processamento de PDFs**: Extração automática de dados de notas fiscais
- **Gestão de Produtos Similares**: Sistema inteligente de associação de produtos
- **Controle de Estoque Mínimo**: Alertas automáticos para reposição
- **API RESTful**: Backend robusto com FastAPI
- **Autenticação JWT**: Sistema seguro de autenticação
- **Banco de Dados PostgreSQL**: Armazenamento confiável e escalável

## 🔧 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

### Sistema Operacional
- **macOS**, **Linux** ou **Windows** (com WSL2 recomendado)

### Software Necessário
- **Python 3.11+** (recomendado 3.11 ou superior) - [Download](https://python.org/downloads/)
- **Node.js 18+** (recomendado 20+) - [Download](https://nodejs.org/)
- **PostgreSQL 13+** (recomendado 15+) - [Download](https://postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/downloads/)

### Ferramentas Opcionais
- **Docker** - Para containerização
- **Docker Compose** - Para orquestração de containers

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/higiplas_system.git
cd higiplas_system
```

### 2. Configuração do Backend

```bash
# Navegue para o diretório do backend
cd backend

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No macOS/Linux:
source venv/bin/activate
# No Windows:
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração do Frontend

```bash
# Navegue para o diretório do frontend
cd ../higiplas_frontend

# Instale as dependências
npm install
```

### 4. Configuração do Banco de Dados

```bash
# Crie o banco de dados PostgreSQL
psql -U postgres -c "CREATE DATABASE higiplas_db;"

# Execute as migrações
cd ../backend
alembic upgrade head
```

### 5. Configuração com Docker (Alternativa)

```bash
# Na raiz do projeto
docker-compose up -d
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie os arquivos de configuração:

#### Backend (.env)

```bash
# Copie o arquivo de exemplo
cp backend/.env.example backend/.env
```

```env
# Configurações do Banco de Dados
DATABASE_URL=postgresql://usuario:senha@localhost:5432/higiplas_db

# Configurações JWT
SECRET_KEY=sua_chave_secreta_muito_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configurações da API
API_V1_STR=/api/v1
PROJECT_NAME="Higiplas System"

# Configurações CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Configurações de Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB
```

#### Frontend (.env.local)

```bash
# Crie o arquivo de configuração
touch higiplas_frontend/.env.local
```

```env
# URL da API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Configurações de Desenvolvimento
NEXT_PUBLIC_ENV=development
```

## 🏃‍♂️ Uso

### Desenvolvimento

#### 1. Inicie o Backend

```bash
cd backend
source venv/bin/activate  # Ative o ambiente virtual
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O backend estará disponível em: `http://localhost:8000`

#### 2. Inicie o Frontend

```bash
cd higiplas_frontend
npm run dev
```

O frontend estará disponível em: `http://localhost:3000`

### Produção

#### Com Docker

```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### Manual

```bash
# Backend
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
cd higiplas_frontend
npm run build
npm start
```

### Primeiros Passos

1. **Acesse o sistema**: `http://localhost:3000`
2. **Faça login** com as credenciais padrão:
   - Email: `admin@higiplas.com`
   - Senha: `admin123`
3. **Configure produtos**: Vá para "Produtos" e cadastre seus itens
4. **Processe PDFs**: Use "Movimentações" para importar notas fiscais
5. **Visualize relatórios**: Acesse o dashboard para análises

## 📁 Estrutura de Arquivos

```
higiplas_system/
├── 📁 backend/                    # API Backend (FastAPI)
│   ├── 📁 app/
│   │   ├── 📁 core/               # Configurações centrais
│   │   ├── 📁 crud/               # Operações CRUD
│   │   ├── 📁 db/                 # Configuração do banco
│   │   ├── 📁 routers/            # Endpoints da API
│   │   ├── 📁 schemas/            # Modelos Pydantic
│   │   ├── 📁 services/           # Lógica de negócio
│   │   └── 📄 main.py             # Aplicação principal
│   ├── 📁 alembic/                # Migrações do banco
│   ├── 📄 requirements.txt       # Dependências Python
│   └── 📄 .env                    # Variáveis de ambiente
├── 📁 higiplas_frontend/          # Frontend (Next.js)
│   ├── 📁 src/
│   │   ├── 📁 app/                # App Router (Next.js 13+)
│   │   ├── 📁 components/         # Componentes React
│   │   ├── 📁 contexts/           # Context API
│   │   ├── 📁 hooks/              # Custom Hooks
│   │   ├── 📁 services/           # Serviços de API
│   │   └── 📁 types/              # Tipos TypeScript
│   ├── 📄 package.json           # Dependências Node.js
│   ├── 📄 tailwind.config.js     # Configuração Tailwind
│   └── 📄 .env.local              # Variáveis de ambiente
├── 📁 dados de baixa e entrada no estoque/  # PDFs de exemplo
├── 📄 docker-compose.yml         # Configuração Docker
├── 📄 README.md                  # Este arquivo
└── 📄 .gitignore                 # Arquivos ignorados pelo Git
```

### Principais Diretórios

- **`backend/app/routers/`**: Contém todos os endpoints da API
- **`backend/app/services/`**: Lógica de processamento de PDFs e negócio
- **`higiplas_frontend/src/app/`**: Páginas e layouts do sistema
- **`higiplas_frontend/src/components/`**: Componentes reutilizáveis

## 🧪 Testes

### Backend

```bash
cd backend

# Instale dependências de teste
pip install pytest pytest-asyncio httpx

# Execute todos os testes
pytest

# Execute com cobertura
pytest --cov=app tests/

# Execute testes específicos
pytest tests/test_movimentacoes.py -v
```

### Frontend

```bash
cd higiplas_frontend

# Execute testes unitários
npm test

# Execute testes com cobertura
npm run test:coverage

# Execute testes E2E
npm run test:e2e
```

### Testes de Integração

```bash
# Teste a API diretamente
curl -X GET http://localhost:8000/api/v1/health

# Teste upload de PDF
curl -X POST http://localhost:8000/api/v1/movimentacoes/preview-pdf \
  -H "Authorization: Bearer seu_token" \
  -F "arquivo=@exemplo.pdf" \
  -F "tipo_movimentacao=ENTRADA"
```

## 🤝 Contribuição

Contribuições são sempre bem-vindas! Siga estas diretrizes:

### Como Contribuir

1. **Fork** o projeto
2. **Clone** seu fork: `git clone https://github.com/seu-usuario/higiplas_system.git`
3. **Crie uma branch** para sua feature: `git checkout -b feature/nova-funcionalidade`
4. **Commit** suas mudanças: `git commit -m 'Adiciona nova funcionalidade'`
5. **Push** para a branch: `git push origin feature/nova-funcionalidade`
6. **Abra um Pull Request**

### Padrões de Código

#### Backend (Python)
- Use **Black** para formatação: `black app/`
- Use **isort** para imports: `isort app/`
- Use **flake8** para linting: `flake8 app/`
- Siga **PEP 8**

#### Frontend (TypeScript/React)
- Use **Prettier** para formatação: `npm run format`
- Use **ESLint** para linting: `npm run lint`
- Siga as **convenções do React**

### Estrutura de Commits

```
feat: adiciona nova funcionalidade
fix: corrige bug específico
docs: atualiza documentação
style: mudanças de formatação
refactor: refatoração de código
test: adiciona ou modifica testes
chore: tarefas de manutenção
```

### Reportando Bugs

Ao reportar bugs, inclua:
- **Descrição clara** do problema
- **Passos para reproduzir**
- **Comportamento esperado vs atual**
- **Screenshots** (se aplicável)
- **Informações do ambiente** (OS, versões, etc.)

## 📄 Licença

Este projeto está licenciado sob a **Licença MIT** - veja o arquivo [LICENSE](LICENSE) para detalhes.

```
MIT License

Copyright (c) 2024 Higiplas System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📞 Contato

### Mantenedores

- **Equipe de Desenvolvimento**: [comercial@ozentech.com](mailto:comercial@ozentech.com)
- **Suporte Técnico**: [comercial@ozentech.com](mailto:comercial@ozentech.com)

### Links Úteis

- 🌐 **Website**: [https://higiplas.ozentech.com](https://higiplas.ozentech.com)
- 📚 **Documentação**: [https://docs.higiplas.com](https://docs.higiplas.com)

### Redes Sociais

- 💼 **LinkedIn**: [Ozen Tech]([https://linkedin.com/company/higiplas](https://www.linkedin.com/company/ozen-tech/?viewAsMember=true))

---

<div align="center">
  <p><strong>Desenvolvido com ❤️ pela equipe OzenTech</strong></p>
  <p>Se este projeto foi útil para você, considere dar uma ⭐!</p>
</div>

## 🔄 Changelog

### v1.0.0 (2024-01-15)
- ✨ Lançamento inicial do sistema
- 🎯 Processamento de PDFs GIRASSOL
- 📊 Dashboard completo
- 🔐 Sistema de autenticação JWT
- 📱 Interface responsiva

### Próximas Versões

- 🔮 **v1.1.0**: Relatórios avançados e exportação
- 🚀 **v1.2.0**: API mobile e aplicativo
- 🤖 **v2.0.0**: IA para previsão de estoque

---

> **Nota**: Este README é um documento vivo e será atualizado conforme o projeto evolui. Para a versão mais recente, sempre consulte o repositório oficial.