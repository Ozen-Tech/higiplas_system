# Sistema Higiplas

Sistema de gestão completo para Higiplas e Higitec, incluindo controle de estoque, produtos, clientes, orçamentos e análise de vendas com IA.

## 🚀 Funcionalidades

### Backend (FastAPI + PostgreSQL)
- **Gestão de Produtos**: CRUD completo com controle de estoque
- **Gestão de Clientes**: Cadastro e gerenciamento de clientes
- **Sistema de Orçamentos**: Criação e acompanhamento de orçamentos
- **Análise de Vendas com IA**: Processamento de PDFs e análise inteligente
- **Produtos Mais Vendidos**: Dashboard com insights de vendas
- **Autenticação JWT**: Sistema seguro de login
- **API RESTful**: Endpoints documentados com Swagger

### Frontend (Next.js + TypeScript)
- **Dashboard Interativo**: Visualização de dados em tempo real
- **Interface Responsiva**: Design moderno com Tailwind CSS
- **Gestão de Estado**: Context API para gerenciamento global
- **Componentes Reutilizáveis**: Arquitetura modular
- **Integração com IA**: Interface para análise de produtos

## 🛠️ Tecnologias

### Backend
- **FastAPI**: Framework web moderno e rápido
- **PostgreSQL**: Banco de dados relacional
- **SQLAlchemy**: ORM para Python
- **Alembic**: Migrações de banco de dados
- **PyPDF2**: Processamento de arquivos PDF
- **Pydantic**: Validação de dados
- **JWT**: Autenticação segura

### Frontend
- **Next.js 14**: Framework React com App Router
- **TypeScript**: Tipagem estática
- **Tailwind CSS**: Framework CSS utilitário
- **React Hook Form**: Gerenciamento de formulários
- **Axios**: Cliente HTTP
- **Lucide React**: Ícones modernos

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- Node.js 18+
- PostgreSQL 12+

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Configurar banco de dados
cp .env.example .env
# Editar .env com suas configurações

# Executar migrações
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

### Frontend
```bash
cd higiplas_frontend
npm install
npm run dev
```

## 🔧 Configuração

### Variáveis de Ambiente (Backend)
```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/higiplas_db
SECRET_KEY=sua_chave_secreta_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Variáveis de Ambiente (Frontend)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Funcionalidades Especiais

### Processamento de PDFs
O sistema processa automaticamente relatórios de vendas em PDF, extraindo:
- Produtos vendidos
- Quantidades
- Valores
- Clientes
- Análise de performance

### IA para Análise de Vendas
- Identificação de produtos mais vendidos
- Sugestões de estoque mínimo
- Análise de tendências
- Relatórios inteligentes

## 🚀 Deploy

### Usando Docker
```bash
docker-compose up -d
```

### Deploy Manual
1. Configure o banco PostgreSQL
2. Execute as migrações
3. Build do frontend: `npm run build`
4. Inicie os serviços

## 📝 API Documentation

Após iniciar o backend, acesse:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 👥 Equipe

Desenvolvido para Higiplas e Higitec.

---

**Sistema Higiplas** - Gestão inteligente para o seu negócio 🚀