# backend/app/db/connection.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extensions import connection as PgConnection

from app.core.config import settings


connection_pool: SimpleConnectionPool | None = None

def init_connection_pool():
    global connection_pool
    if connection_pool is None:
        DB_NAME = os.getenv("DB_NAME")
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = "postgres"
        DB_PORT = "5432"
        print("Inicializando o pool de conexões psycopg2...")
        connection_pool = SimpleConnectionPool(minconn=1, maxconn=20, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        print("Pool psycopg2 inicializado.")

def close_connection_pool():
    global connection_pool
    if connection_pool:
        print("Fechando o pool de conexões psycopg2...")
        connection_pool.closeall()
        connection_pool = None
        print("Pool psycopg2 fechado.")

# --- CONFIGURAÇÃO DO SQLALCHEMY ---
# A URL de conexão agora vem diretamente do objeto de configurações (settings),
# que já possui a lógica correta para diferenciar ambientes de produção e desenvolvimento.
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# ===================================================================
# <<< Câmera de Debug para a URL de Conexão >>>
print("--- [DEBUG] URL DE CONEXÃO VINDA DAS CONFIGURAÇÕES ---")
print(f"--- [DEBUG] URL: {SQLALCHEMY_DATABASE_URL}")
print("----------------------------------------------------")
# ===================================================================

# O 'engine' do SQLAlchemy usa a URL acima para se conectar.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# A fábrica de sessões que o CRUD precisa
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A 'Base' que o models.py precisa para funcionar
Base = declarative_base()


# --- DEPENDÊNCIA get_db ---
# Esta função retorna uma SESSÃO do SQLAlchemy,
# que é o que as nossas funções em `crud/` esperam receber.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()