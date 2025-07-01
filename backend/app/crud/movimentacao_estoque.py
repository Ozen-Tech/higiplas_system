from psycopg2.extensions import connection
from app.schemas.movimentacao_estoque import MovimentacaoEstoqueCreate
from fastapi import HTTPException, status

def create_movimentacao_estoque(conn: connection, movimentacao: MovimentacaoEstoqueCreate, usuario_id: int):
    with conn.cursor() as cur:
        try:
            # --- INÍCIO DA TRANSAÇÃO ---

            # 1. Verificar o estoque atual e se o produto existe
            cur.execute("SELECT estoque_atual FROM produtos WHERE id = %s FOR UPDATE;", (movimentacao.produto_id,))
            produto_estoque = cur.fetchone()

            if produto_estoque is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")

            estoque_atual = produto_estoque[0]

            # 2. Calcular o novo estoque e validar a operação de saída
            if movimentacao.tipo_movimentacao == 'SAIDA':
                if estoque_atual < movimentacao.quantidade:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estoque insuficiente para a saída")
                novo_estoque = estoque_atual - movimentacao.quantidade
            else: # 'ENTRADA'
                novo_estoque = estoque_atual + movimentacao.quantidade

            # 3. Atualizar o estoque na tabela de produtos
            cur.execute(
                "UPDATE produtos SET estoque_atual = %s WHERE id = %s;",
                (novo_estoque, movimentacao.produto_id)
            )

            # 4. Inserir o registro na tabela de movimentações
            cur.execute(
                """
                INSERT INTO movimentacoes_estoque (produto_id, tipo_movimentacao, quantidade, usuario_id, observacao)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, produto_id, tipo_movimentacao, quantidade, data_movimentacao, usuario_id, observacao;
                """,
                (
                    movimentacao.produto_id,
                    movimentacao.tipo_movimentacao,
                    movimentacao.quantidade,
                    usuario_id,
                    movimentacao.observacao
                )
            )
            
            # Pega o registro recém-criado para retornar
            created_movimentacao = cur.fetchone()
            
            # --- FIM DA TRANSAÇÃO ---
            conn.commit() # Efetiva todas as operações no banco

            # Converte a tupla do banco para um dicionário
            column_names = [desc[0] for desc in cur.description]
            return dict(zip(column_names, created_movimentacao))

        except HTTPException as e:
            conn.rollback() # Desfaz a transação em caso de erro de negócio (estoque insuficiente)
            raise e
        except Exception as e:
            conn.rollback() # Desfaz a transação em caso de qualquer outro erro
            # Para depuração, você pode querer logar o erro 'e'
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ocorreu um erro no servidor")

def get_movimentacoes_by_produto_id(conn: connection, produto_id: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, produto_id, tipo_movimentacao, quantidade, data_movimentacao, usuario_id, observacao
            FROM movimentacoes_estoque
            WHERE produto_id = %s
            ORDER BY data_movimentacao DESC;
            """,
            (produto_id,)
        )
        movimentacoes = cur.fetchall()
        if not movimentacoes:
            return []
        
        # Converte a lista de tuplas para uma lista de dicionários
        column_names = [desc[0] for desc in cur.description]
        return [dict(zip(column_names, row)) for row in movimentacoes]