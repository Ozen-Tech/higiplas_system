from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routers import (
    auth, empresas, produtos, movimentacoes, upload_excel,
    insights, dashboard_kpis, invoice_processing,
    fornecedores, ordens_compra, clientes_v2, ai_pdf, minimum_stock, vendas, orcamentos, produtos_mais_vendidos, reports, compras,
    fichas_tecnicas, concorrentes, propostas_detalhadas, visitas, clientes_compras
)

from app.create_superuser import create_initial_superuser
from app.core.error_handler import register_exception_handlers
from app.core.logger import app_logger
from contextlib import asynccontextmanager
import logging
import os

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = app_logger

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

# Configuração de CORS - lista específica de origens permitidas
allowed_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "https://higiplas-system.vercel.app",
    "https://higiplas-system.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
app.include_router(ordens_compra.router)
app.include_router(orcamentos.router)
app.include_router(ai_pdf.router, prefix="/ai-pdf", tags=["ai-pdf"])
app.include_router(minimum_stock.router, tags=["Estoque Mínimo"])
app.include_router(produtos_mais_vendidos.router, tags=["Produtos Mais Vendidos"])
app.include_router(reports.router, prefix="/api/v1", tags=["Relatórios"])
app.include_router(compras.router, tags=["Compras"])
app.include_router(clientes_compras.router, tags=["Clientes - Análise de Compras"])
app.include_router(fichas_tecnicas.router, tags=["Fichas Técnicas"])
app.include_router(concorrentes.router, tags=["Concorrentes"])
app.include_router(propostas_detalhadas.router, tags=["Propostas Detalhadas"])
app.include_router(visitas.router, tags=["Visitas de Vendedores"])

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

    # Verificar se a origem está na lista permitida
    allow_origin = origin if origin and origin in allowed_origins else allowed_origins[0] if allowed_origins else "https://higiplas-system.vercel.app"

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

# Exception handlers são registrados via register_exception_handlers()
# Isso substitui os handlers antigos por versões mais robustas
register_exception_handlers(app)

# Middleware para logar requisições e adicionar headers CORS manualmente
@app.middleware("http")
async def add_cors_and_log(request: Request, call_next):
    logger.info(f"Requisição: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Capturar body para logging apenas em POST/PUT/PATCH
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        if body:
            try:
                import json
                body_json = json.loads(body)
                logger.info(f"Body: {body_json}")
            except:
                logger.info(f"Body (raw): {body[:500]}")  # Primeiros 500 chars
        
        # Recriar request com body para que possa ser lido novamente
        async def receive():
            return {"type": "http.request", "body": body}
        
        request._receive = receive

    # Processar a requisição
    try:
        response = await call_next(request)

        # Adicionar headers CORS manualmente baseado na origem da requisição
        origin = request.headers.get("origin")
        if origin and origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        else:
            # Se não houver origem ou não estiver na lista, usar a primeira origem permitida como fallback
            response.headers["Access-Control-Allow-Origin"] = allowed_origins[0] if allowed_origins else "*"
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
