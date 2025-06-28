from app.schemas.empresa import EmpresaCreate
from app.database import get_db_cursor

def create_empresa(empresa: EmpresaCreate):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO empresas (nome, cnpj) VALUES (%s, %s) RETURNING id, nome, cnpj, created_at",
            (empresa.nome, empresa.cnpj)
        )
        new_empresa = cursor.fetchone()
        return new_empresa

def get_empresas():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id, nome, cnpj, created_at FROM empresas")
        empresas = cursor.fetchall()
        return empresas