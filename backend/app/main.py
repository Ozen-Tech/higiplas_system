from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.routers import (
    auth, empresas, produtos, movimentacoes, 
    upload_excel, insights, orcamentos, dashboard_kpis, 
    invoice_processing, fornecedores, ordens_compra, clientes
)
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Higiplas System API", version="1.0.0")

# Configuração de CORS mais robusta
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://127.0.0.1:3000",
    "https://higiplas-system.vercel.app",
    "https://higiplas-system.onrender.com",
    "*"  # Permitir todas as origens para resolver o problema
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # Mudado para False quando usando *
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Middleware de hosts confiáveis
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]
)

# Incluindo todas as nossas rotas de forma limpa
# Note que no seu código, a rota de insights ainda não estava sendo incluída
app.include_router(auth.router, prefix="/users", tags=["Usuários e Autenticação"])
app.include_router(empresas.router, prefix="/empresas", tags=["Empresas"])
app.include_router(produtos.router, tags=["Produtos"])
app.include_router(movimentacoes.router, prefix="/movimentacoes", tags=["Movimentações de Estoque"])
app.include_router(upload_excel.router, tags=["Upload Excel"])
app.include_router(insights.router, tags=["Insights"])
app.include_router(orcamentos.router)
app.include_router(clientes.router)
app.include_router(dashboard_kpis.router, tags=["Dashboard"])
app.include_router(invoice_processing.router) 
app.include_router(fornecedores.router)
app.include_router(ordens_compra.router)

@app.get("/", tags=["Root"], summary="Verifica a saúde da API")
async def read_root():
    """
    Endpoint principal para verificar se a API está online.
    """
    return {"status": "ok", "message": "Bem-vindo à API da Higiplas!"}

@app.get("/cors-test")
async def cors_test():
    return {
        "status": "CORS funcionando!",
        "environment": "production" if os.getenv("RENDER") else "development"
    }

# Handler para requisições OPTIONS (preflight CORS)
@app.options("/{path:path}")
async def options_handler(request: Request):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "false"
        }
    )