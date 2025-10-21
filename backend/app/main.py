from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.routers import (
    auth, empresas, produtos, movimentacoes, upload_excel,
    insights, dashboard_kpis, invoice_processing,
    fornecedores, ordens_compra, clientes_v2, ai_pdf, minimum_stock, vendas, orcamentos, produtos_mais_vendidos, propostas
)
from app.create_superuser import create_initial_superuser
from contextlib import asynccontextmanager
import logging
import os
# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando aplicação...")
    create_initial_superuser()
    logger.info("Superusuário criado/verificado com sucesso")
    yield
    # Shutdown
    logger.info("Encerrando aplicação...")

app = FastAPI(
    title="Higiplas System API",
    version="1.0.0",
    redirect_slashes=True,  # Permite URLs com e sem barra final
    lifespan=lifespan
)

# Configuração de CORS para desenvolvimento: permitir todas as origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens temporariamente para debug
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "User-Agent",
        "DNT",
        "Cache-Control",
        "X-Requested-With"
    ],
    expose_headers=[
        "Content-Disposition",
        "Content-Type",
        "Content-Length"
    ],
    max_age=3600  # Cache preflight por 1 hora
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
app.include_router(vendas.router)
app.include_router(upload_excel.router, tags=["Upload Excel"])
app.include_router(insights.router, tags=["Insights"])
app.include_router(clientes_v2.router)  # Sistema principal de clientes
app.include_router(dashboard_kpis.router, tags=["Dashboard"])
app.include_router(invoice_processing.router)
app.include_router(fornecedores.router)
app.include_router(orcamentos.router)
app.include_router(ordens_compra.router)
app.include_router(ai_pdf.router, prefix="/ai-pdf", tags=["ai-pdf"])
app.include_router(minimum_stock.router, tags=["Estoque Mínimo"])
app.include_router(produtos_mais_vendidos.router, tags=["Produtos Mais Vendidos"])
app.include_router(propostas.router, tags=["Propostas"])

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
    origin = request.headers.get("origin")
    allowed_origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "https://higiplas-system.vercel.app",
        "https://higiplas-system.onrender.com"
    ]

    # Verificar se a origem está na lista permitida
    allow_origin = origin if origin in allowed_origins else "https://higiplas-system.vercel.app"

    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin, User-Agent, DNT, Cache-Control, X-Requested-With",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Expose-Headers": "Content-Disposition, Content-Type, Content-Length"
        }
    )

# Middleware para logar requisições e adicionar headers CORS manualmente
@app.middleware("http")
async def add_cors_and_log(request: Request, call_next):
    logger.info(f"Requisição: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")

    # Processar a requisição
    try:
        response = await call_next(request)

        # Adicionar headers CORS manualmente
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, Origin, User-Agent, DNT, Cache-Control, X-Requested-With"
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition, Content-Type, Content-Length"

        logger.info(f"Resposta: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Erro ao processar requisição: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise
