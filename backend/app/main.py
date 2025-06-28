from fastapi import FastAPI
from app.routers import empresas, produtos

app = FastAPI(
    title="Higiplas API",
    description="API para o sistema de gestão da Higiplas e Higitech.",
    version="1.0.0"
)

# Inclui os routers na aplicação principal
app.include_router(empresas.router)
app.include_router(produtos.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint raiz para verificar se a API está no ar.
    """
    return {"message": "Bem-vindo à API do Sistema Higiplas! Ambiente OK."}