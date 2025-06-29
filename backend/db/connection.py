import psycopg2
from psycopg2.extensions import connection
import os

# Função para obter uma conexão com o banco de dados
def get_db_connection() -> connection:
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host="postgres" # O nome do serviço no docker-compose
    )
    return conn

# Função de dependência para o FastAPI
def get_db():
    conn = None
    try:
        conn = get_db_connection()
        yield conn
    finally:
        if conn:
            conn.close()