from psycopg2.extensions import connection
from app.schemas.produto import ProdutoCreate
from fastapi import HTTPException, status
from psycopg2 import errors

def create_produto(conn: connection, produto: ProdutoCreate):
    """
    Cria um novo produto no banco de dados.
    """
    with conn.cursor() as cur:
        try:
            # A query usa os campos definidos no seu schema ProdutoCreate
            cur.execute(
                """
                INSERT INTO produtos (nome, codigo, empresa_id, categoria_id, estoque_minimo, unidade)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, nome, codigo, empresa_id, categoria_id, estoque_minimo, unidade, created_at;
                """,
                (produto.nome, produto.codigo, produto.empresa_id, produto.categoria_id, produto.estoque_minimo, produto.unidade)
            )
            new_produto_tuple = cur.fetchone()
            conn.commit()
            
            if new_produto_tuple:
                column_names = [desc[0] for desc in cur.description]
                return dict(zip(column_names, new_produto_tuple))

            raise HTTPException(status_code=500, detail="Falha ao obter dados do produto após a criação.")

        except errors.UniqueViolation:
            conn.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Produto com este código já existe.")
        except errors.ForeignKeyViolation:
            conn.rollback()
            raise HTTPException(status.HTTP_404_NOT_FOUND, "A empresa ou categoria especificada não existe.")
        except Exception as e:
            conn.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Erro ao criar produto: {e}")


def get_produtos(conn: connection, skip: int = 0, limit: int = 100):
    """
    Busca uma lista paginada de produtos no banco de dados.
    """
    produtos = []
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, nome, codigo, empresa_id, categoria_id, estoque_minimo, unidade, created_at FROM produtos ORDER BY nome LIMIT %s OFFSET %s;",
            (limit, skip)
        )
        column_names = [desc[0] for desc in cur.description]
        
        for row in cur.fetchall():
            produtos.append(dict(zip(column_names, row)))
            
    return produtos