from contextlib import asynccontextmanager

# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, empresas, produtos, movimentacoes, upload_excel
from app.db import models, connection
from app.create_superuser import create_initial_superuser


app = FastAPI()



# Configuração do CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://higiplas-system.vercel.app", # Endereço do seu frontend Next.js
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluindo as rotas
app.include_router(auth.router, prefix="/users", tags=["Usuários e Autenticação"])
app.include_router(empresas.router, prefix="/empresas", tags=["Empresas"])
app.include_router(produtos.router, prefix="/produtos", tags=["Produtos"])
app.include_router(movimentacoes.router, prefix="/movimentacoes", tags=["Movimentações de Estoque"])
app.include_router(upload_excel.router, tags=["Upload Excel"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo à API da Higiplas!"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando a aplicação...")
    create_initial_superuser() # A chamada está aqui
    yield
    print("Finalizando a aplicação...")