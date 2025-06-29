from app.schemas.produto import ProdutoCreate
from app.db.connection import get_db_cursor

def create_produto(produto: ProdutoCreate):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO produtos (nome, codigo, empresa_id, categoria_id, estoque_minimo, unidade)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, nome, codigo, empresa_id, categoria_id, estoque_minimo, unidade, created_at
            """,
            (produto.nome, produto.codigo, produto.empresa_id, produto.categoria_id, produto.estoque_minimo, produto.unidade)
        )
        new_produto = cursor.fetchone()
        return new_produto

def get_produtos():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id, nome, codigo, empresa_id, categoria_id, estoque_minimo, unidade, created_at FROM produtos")
        produtos = cursor.fetchall()
        return produtos