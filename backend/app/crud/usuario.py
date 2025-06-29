from app.schemas.usuario import UsuarioCreate
from app.db.connection import get_db_cursor
from app.security import get_password_hash

def get_user_by_email(email: str):
    """Busca um usuário pelo email."""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        if user_data:
            # Converte a tupla para um dicionário para facilitar o acesso
            column_names = [desc[0] for desc in cursor.description]
            return dict(zip(column_names, user_data))
        return None

def create_user(user: UsuarioCreate):
    """Cria um novo usuário no banco com a senha hasheada."""
    hashed_password = get_password_hash(user.senha)
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO usuarios (nome, email, senha_hash, empresa_id, perfil)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, nome, email, empresa_id, perfil, is_active, created_at
            """,
            (user.nome, user.email, hashed_password, user.empresa_id, user.perfil)
        )
        new_user = cursor.fetchone()
        return new_user