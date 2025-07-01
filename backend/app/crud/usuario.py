# app/crud/usuario.py

from psycopg2.extensions import connection
from psycopg2 import errors
from fastapi import HTTPException, status
from app.schemas.usuario import UsuarioCreate
from app.core import get_password_hash

def get_user_by_email(conn: connection, email: str):
    """
    Busca um usuário pelo e-mail. Recebe a conexão como argumento.
    Retorna um dicionário representando o usuário se encontrado, senão None.
    """
    with conn.cursor() as cur:
        # Seleciona todas as colunas para garantir que o objeto retornado seja completo
        cur.execute("SELECT * FROM usuarios WHERE email = %s;", (email,))
        user = cur.fetchone()
        if user:
            # Converte o resultado (tupla) em um dicionário
            column_names = [desc[0] for desc in cur.description]
            return dict(zip(column_names, user))
    return None

def create_user(conn: connection, user: UsuarioCreate):
    """
    Cria um novo usuário no banco de dados. Recebe a conexão como argumento.
    """
    hashed_password = get_password_hash(user.password)
    
    # Definimos um perfil padrão para cada novo usuário.
    # No futuro, isso pode vir do próprio request se o schema for alterado.
    perfil_padrao = "vendedor"

    with conn.cursor() as cur:
        try:
            # A query SQL foi corrigida para:
            # 1. Incluir a coluna 'perfil' no INSERT.
            # 2. Incluir o valor 'perfil_padrao' nos dados.
            # 3. O 'RETURNING' agora pede TODOS os campos que o schema de resposta espera.
            cur.execute(
                """
                INSERT INTO usuarios (email, hashed_password, nome, empresa_id, perfil)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, nome, email, empresa_id, perfil, is_active, created_at;
                """,
                (user.email, hashed_password, user.nome, user.empresa_id, perfil_padrao)
            )
            created_user_tuple = cur.fetchone()
            
            # Commit é crucial para salvar as alterações no banco de dados
            conn.commit()

            if created_user_tuple:
                # Converte a tupla retornada em um dicionário para o FastAPI
                column_names = [desc[0] for desc in cur.description]
                return dict(zip(column_names, created_user_tuple))
            
            # Fallback para um caso improvável
            raise HTTPException(status_code=500, detail="Falha ao obter dados do usuário após a criação.")

        except errors.UniqueViolation:
            # Se o e-mail já existe, desfaz a transação e informa o cliente
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="O e-mail fornecido já está cadastrado."
            )
        except errors.ForeignKeyViolation:
            # Se a empresa_id não existe, desfaz a transação e informa o cliente
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"A empresa com ID {user.empresa_id} não foi encontrada."
            )
        except Exception as e:
            # Para qualquer outro erro, desfaz a transação e loga o erro
            conn.rollback()
            print(f"ERRO INESPERADO NO CRUD DE USUÁRIO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ocorreu um erro interno inesperado ao criar o usuário."
            )