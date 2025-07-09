from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Nossos routers
from app.routers import auth, empresas, produtos, movimentacoes, upload_excel, insights # Adicionei 'insights'

# Criação da instância principal do FastAPI
app = FastAPI(
    title="API Higiplas",
    description="Sistema de Gestão de Estoque para a Higiplas.",
    version="1.0.0"
)

# Configuração do CORS (já estava correta)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://higiplas-system.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluindo todas as nossas rotas de forma limpa
# Note que no seu código, a rota de insights ainda não estava sendo incluída
app.include_router(auth.router, prefix="/users", tags=["Usuários e Autenticação"])
app.include_router(empresas.router, prefix="/empresas", tags=["Empresas"])
app.include_router(produtos.router, prefix="/produtos", tags=["Produtos"])
app.include_router(movimentacoes.router, prefix="/movimentacoes", tags=["Movimentações de Estoque"])
app.include_router(upload_excel.router, tags=["Upload Excel"])
app.include_router(insights.router, tags=["Insights"]) # Incluindo o router da IA

@app.get("/", tags=["Root"], summary="Verifica a saúde da API")
async def read_root():
    """
    Endpoint principal para verificar se a API está online.
    """
    return {"status": "ok", "message": "Bem-vindo à API da Higiplas!"}