# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, empresas, produtos, movimentacoes, upload_excel
from app.db import models, connection

app = FastAPI(
    title="API Higiplas OzenTech",
    description="API para o sistema de gestão de estoque e CRM da Higiplas.",
    version="1.0.0"
)




# Configuração do CORS
origins = [
    "http://localhost",
    "http://localhost:3000", # Endereço do seu frontend Next.js
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