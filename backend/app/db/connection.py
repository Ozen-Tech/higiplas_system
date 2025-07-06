# backend/app/db/connection.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extensions import connection as PgConnection


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

# --- CONFIGURAÇÃO DO SQLALCHEMY (A parte que estamos depurando) ---
# Lendo as variáveis de ambiente para o SQLAlchemy
DB_USER_SA = os.getenv("DB_USER")
DB_PASSWORD_SA = os.getenv("DB_PASSWORD")
DB_NAME_SA = os.getenv("DB_NAME")
DB_HOST_SA = "postgres"  # O nome do serviço no docker-compose
DB_PORT_SA = "5432"

# Montando a string de conexão que o SQLAlchemy entende
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# ===================================================================
# <<< ADICIONADO: Câmera de Debug para a URL de Conexão >>>
# Esta linha vai nos mostrar no log do Docker exatamente como a URL
# está sendo montada, revelando o problema.
print("--- [DEBUG] URL DE CONEXÃO GERADA ---")
print(f"--- [DEBUG] URL: {SQLALCHEMY_DATABASE_URL}")
print("-------------------------------------")
# ===================================================================

# O 'engine' do SQLAlchemy usa a URL acima para se conectar.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# A fábrica de sessões que o CRUD precisa
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A 'Base' que o models.py precisa para funcionar
Base = declarative_base()


# --- NOVA DEPENDÊNCIA get_db ---
# Esta função agora retorna uma SESSÃO do SQLAlchemy,
# que é o que as nossas funções em `crud/` esperam receber.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()