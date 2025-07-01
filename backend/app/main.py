from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import empresas, produtos, auth, movimentacoes
from app.db.connection import init_connection_pool, close_connection_pool

# Gerenciador de ciclo de vida para a aplicação FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código a ser executado ANTES da aplicação começar a receber requisições
    init_connection_pool()
    yield
    # Código a ser executado DEPOIS que a aplicação parar
    close_connection_pool()

app = FastAPI(
    title="Higiplas API",
    description="API para o sistema de gestão da Higiplas e Higitech.",
    version="1.0.0",
    lifespan=lifespan  # Adiciona o gerenciador de ciclo de vida
)

# ... (resto do seu main.py com os app.include_router)
app.include_router(auth.router) 
app.include_router(empresas.router)
app.include_router(produtos.router)
app.include_router(movimentacoes.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint raiz para verificar se a API está no ar.
    """
    return {"message": "Bem-vindo à API do Sistema Higiplas! Ambiente OK."}