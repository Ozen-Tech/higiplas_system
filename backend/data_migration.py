# /backend/data_migration.py

from bs4 import BeautifulSoup
import re
import json
from app.db.connection import SessionLocal
from app.db.models import VendaHistorica

def parse_number(s: str) -> float:
    """Converte uma string numérica brasileira (ex: '1.288,7400') para float."""
    if not isinstance(s, str) or not s:
        return 0.0
    # Limpa espaços e troca os separadores
    cleaned_s = s.strip().replace('.', '').replace(',', '.')
    try:
        return float(cleaned_s)
    except (ValueError, TypeError):
        return 0.0

def parse_report_html(file_path: str):
    """
    Lê um arquivo HTML de relatório e extrai os dados da tabela de vendas 
    de forma mais robusta.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'lxml')
    
    all_products = []
    print(f"\n--- Processando Arquivo: {file_path} ---")

    # Encontra todas as linhas de tabelas (tr) no documento
    all_rows = soup.find_all('tr')

    print(f"Encontradas {len(all_rows)} linhas <tr> no total.")
    found_products_in_file = 0

    # Iteramos sobre cada linha encontrada
    for row in all_rows:
        # Pega todas as células <td> da linha
        cells = row.find_all('td')
        
        # Filtro de Validação: uma linha de dados de produto deve:
        # 1. Ter um número razoável de células (pelo menos 8)
        # 2. A primeira célula deve conter um número (o "Ident.")
        if len(cells) >= 8 and cells[0].get_text(strip=True).isdigit():
            try:
                # O HTML usa `colspan` para a descrição. A BeautifulSoup lida com isso.
                # A estrutura parece ser [id, desc, qtd, custo, vendido, lucro, margem] quando extraído.
                ident = cells[0].get_text(strip=True)
                descricao = cells[1].get_text(strip=True)
                
                # Vamos encontrar os valores numéricos. Eles geralmente estão em colunas mais à direita.
                # Procuramos de trás para frente para evitar colunas de descrição com números.
                numeric_cells_text = [cell.get_text(strip=True) for cell in cells[-7:]]

                quantidade_vendida_total = parse_number(numeric_cells_text[0])
                custo_compra_total = parse_number(numeric_cells_text[1])
                valor_vendido_total = parse_number(numeric_cells_text[2])
                lucro_bruto_total = parse_number(numeric_cells_text[3])
                margem_lucro_percentual = parse_number(numeric_cells_text[4]) # Pode falhar, é a última

                product_data = {
                    "ident_antigo": int(ident),
                    "descricao": descricao,
                    "quantidade_vendida_total": quantidade_vendida_total,
                    "custo_compra_total": custo_compra_total,
                    "valor_vendido_total": valor_vendido_total,
                    "lucro_bruto_total": lucro_bruto_total,
                    "margem_lucro_percentual": margem_lucro_percentual
                }
                
                all_products.append(product_data)
                found_products_in_file += 1

            except Exception as e:
                # Se algo der errado numa linha específica, logamos o erro e continuamos
                # print(f"AVISO: Pulando linha com formato inesperado. Erro: {e}")
                pass
                
    print(f"Encontrados e processados {found_products_in_file} registros de produtos neste arquivo.")
    return all_products

# --- Ponto de Execução Principal ---
if __name__ == "__main__":
    
    higiplas_data = parse_report_html("2015 - 2025 - HIGIPLAS.html")
    higitec_data = parse_report_html("2020 - 2025 - HIGITEC.html")
    
    # Validação para ter certeza de que não está vazio
    if not higiplas_data and not higitec_data:
        print("\n❌ ERRO FATAL: Nenhum dado foi extraído de nenhum dos arquivos. Verifique os seletores no script 'parse_report_html'.")
    else:
        # Combinando os dados de ambos os relatórios
        all_historical_data = higiplas_data + higitec_data

        output_file = "dados_historicos_vendas.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_historical_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Concluído! {len(all_historical_data)} registros totais de vendas foram salvos em '{output_file}'.")


    def populate_historical_data(db: Session, data: list):
        print("Populando a tabela de vendas históricas...")
        for item in data:
            db_item = VendaHistorica(**item)
            db.add(db_item)
        db.commit()
        print("Dados históricos inseridos com sucesso!")

    if __name__ == "__main__":
        # ... código anterior para gerar o JSON ...

        # Novo trecho para popular o banco
        db = SessionLocal()
        try:
            with open("dados_historicos_vendas.json", 'r', encoding='utf-8') as f:
                historical_data = json.load(f)
            populate_historical_data(db, historical_data)
        finally:
            db.close()