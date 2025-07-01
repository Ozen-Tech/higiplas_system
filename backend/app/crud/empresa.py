from psycopg2.extensions import connection
from app.schemas.empresa import EmpresaCreate
from app.db.connection import get_db # Importe a dependência
from fastapi import HTTPException, status
from psycopg2 import errors

def create_empresa(conn: connection, empresa: EmpresaCreate):
    with conn.cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO empresas (nome, cnpj) VALUES (%s, %s) RETURNING id, nome, cnpj, created_at;",
                (empresa.nome, empresa.cnpj)
            )
            new_empresa = cur.fetchone()
            conn.commit()
            column_names = [desc[0] for desc in cur.description]
            return dict(zip(column_names, new_empresa))
        except errors.UniqueViolation:
            conn.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Empresa com este CNPJ já existe.")
        except Exception as e:
            conn.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Erro ao criar empresa: {e}")

def get_empresas(conn: connection, skip: int = 0, limit: int = 100):
    """
    Busca uma lista paginada de empresas no banco de dados.
    """
    empresas = []
    with conn.cursor() as cur:
        # Selecionamos as colunas que o nosso schema 'Empresa' espera
        cur.execute(
            "SELECT id, nome, cnpj, created_at FROM empresas ORDER BY nome LIMIT %s OFFSET %s;",
            (limit, skip)
        )
        
        # Pega os nomes das colunas para montar os dicionários de forma segura
        column_names = [desc[0] for desc in cur.description]
        
        for row in cur.fetchall():
            empresas.append(dict(zip(column_names, row)))
            
    return empresas