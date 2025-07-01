import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extensions import connection as PgConnection

# Apenas declaramos a variável do pool aqui, mas não a inicializamos.
# Ela será None no início.
connection_pool: SimpleConnectionPool | None = None

def get_pool() -> SimpleConnectionPool:
    """Função para obter o pool de conexões. Levanta um erro se não for inicializado."""
    if connection_pool is None:
        raise RuntimeError("O pool de conexões não foi inicializado.")
    return connection_pool


def init_connection_pool():
    """Inicializa o pool de conexões. Será chamada no evento de startup da API."""
    global connection_pool
    if connection_pool is None:
        # --- A CORREÇÃO ESTÁ AQUI ---
        # Lendo as variáveis com os nomes corretos do arquivo .env
        DB_NAME = os.getenv("DB_NAME")
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = "postgres" # Nome do serviço no docker-compose
        DB_PORT = "5432"
        
        print("Inicializando o pool de conexões...")
        connection_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=20,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Pool de conexões inicializado com sucesso.")


def close_connection_pool():
    """Fecha todas as conexões no pool. Será chamada no evento de shutdown da API."""
    global connection_pool
    if connection_pool:
        print("Fechando o pool de conexões...")
        connection_pool.closeall()
        connection_pool = None
        print("Pool de conexões fechado.")

def get_db() -> PgConnection:
    """Dependência do FastAPI que obtém uma conexão do pool e a devolve no final."""
    pool = get_pool()
    conn = None
    try:
        conn = pool.getconn()
        yield conn
    finally:
        if conn:
            pool.putconn(conn)