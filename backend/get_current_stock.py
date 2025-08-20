import os
import psycopg2
import json

def get_current_stock():
    """Busca o estoque atual dos produtos no banco de dados."""
    db_url = "postgresql://higiplas_postgres_prod_user:T4UPwBadMURnW5EPOcAsogYUARNgWWXj@dpg-d1kpjbfdiees73ern72g-a/higiplas_postgres_prod"
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute("SELECT id, nome, quantidade_em_estoque FROM produtos")
        stock_data = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Converter para uma lista de dicionários
        stock_list = []
        for row in stock_data:
            stock_list.append({
                "id": row[0],
                "nome": row[1],
                "quantidade_em_estoque": row[2]
            })
            
        return stock_list
        
    except Exception as e:
        print(f"Erro ao conectar ou buscar dados no banco de dados: {e}")
        return None

if __name__ == "__main__":
    current_stock = get_current_stock()
    
    if current_stock:
        output_path = "/Users/ozen/higiplas_system/backend/estoque_atual.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(current_stock, f, indent=4, ensure_ascii=False)
            
        print(f"Dados de estoque atual salvos em: {output_path}")
        print(f"Total de produtos com estoque verificado: {len(current_stock)}")

        # Exibe os 5 primeiros registros para verificação
        if current_stock:
            print("\n### Primeiros 5 registros de estoque: ###")
            for record in current_stock[:5]:
                print(record)