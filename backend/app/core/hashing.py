from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# Configura o contexto de criptografia com bcrypt
# Usa truncate_verify_error=True para lidar com senhas > 72 bytes
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde à senha com hash."""
    try:
        # Valida entradas
        if not plain_password or not hashed_password:
            return False
        
        # Trunca a senha para 72 bytes se necessário (limite do bcrypt)
        if isinstance(plain_password, str):
            plain_password_bytes = plain_password.encode('utf-8')
            if len(plain_password_bytes) > 72:
                logger.warning(f"Senha truncada de {len(plain_password_bytes)} para 72 bytes")
                plain_password = plain_password_bytes[:72].decode('utf-8', errors='ignore')
        
        # Verifica se o hash é válido (deve começar com $2a$, $2b$ ou $2y$)
        if not hashed_password.startswith(('$2a$', '$2b$', '$2y$')):
            logger.error(f"Hash de senha inválido: não começa com prefixo bcrypt válido")
            return False
        
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError as e:
        # Erro específico do bcrypt (senha muito longa, hash inválido, etc)
        logger.error(f"Erro de validação ao verificar senha: {e}")
        return False
    except (TypeError, AttributeError) as e:
        logger.error(f"Erro de tipo ao verificar senha: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado ao verificar senha: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha."""
    try:
        if not password:
            raise ValueError("Senha não pode ser vazia")
        
        # Trunca a senha para 72 bytes se necessário (limite do bcrypt)
        if isinstance(password, str):
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                logger.warning(f"Senha truncada de {len(password_bytes)} para 72 bytes ao criar hash")
                password = password_bytes[:72].decode('utf-8', errors='ignore')
        
        return pwd_context.hash(password)
    except ValueError as e:
        logger.error(f"Erro de validação ao criar hash da senha: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao criar hash da senha: {e}")
        raise