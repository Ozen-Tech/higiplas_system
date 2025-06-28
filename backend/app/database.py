import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager

# Carrega as variáveis de ambiente
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = "db"  # O nome do serviço no docker-compose.yml
DB_PORT = "5432"

# Cria um pool de conexões
# Um pool é mais eficiente do que abrir e fechar conexões a cada requisição
connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

@contextmanager
def get_db_connection():
    """
    Gerenciador de contexto para obter uma conexão do pool.
    Garante que a conexão seja devolvida ao pool, mesmo que ocorram erros.
    """
    connection = connection_pool.getconn()
    try:
        yield connection
    finally:
        connection_pool.putconn(connection)

@contextmanager
def get_db_cursor(commit=False):
    """
    Gerenciador de contexto para obter um cursor.
    Realiza o commit se especificado.
    """
    with get_db_connection() as connection:
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()