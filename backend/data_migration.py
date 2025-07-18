# /backend/data_migration.py
# OBJETIVO: Apenas extrair dados dos HTMLs e criar o arquivo JSON.

from bs4 import BeautifulSoup
import re
import json

def parse_number(s: str) -> float:
    if not isinstance(s, str) or not s:
        return 0.0
    cleaned_s = s.strip().replace('.', '').replace(',', '.')
    try:
        return float(cleaned_s)
    except (ValueError, TypeError):
        return 0.0

def parse_report_html(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'lxml')
    all_products = []
    print(f"\n--- Processando Arquivo: {file_path} ---")
    all_rows = soup.find_all('tr')
    
    found_products_in_file = 0
    for row in all_rows:
        cells = row.find_all('td')
        if len(cells) >= 8 and cells[0].get_text(strip=True).isdigit():
            try:
                ident = cells[0].get_text(strip=True)
                descricao = cells[1].get_text(strip=True)
                numeric_cells_text = [cell.get_text(strip=True) for cell in cells[-7:]]

                product_data = {
                    "ident_antigo": int(ident),
                    "descricao": descricao,
                    "quantidade_vendida_total": parse_number(numeric_cells_text[0]),
                    "custo_compra_total": parse_number(numeric_cells_text[1]),
                    "valor_vendido_total": parse_number(numeric_cells_text[2]),
                    "lucro_bruto_total": parse_number(numeric_cells_text[3]),
                    "margem_lucro_percentual": parse_number(numeric_cells_text[4])
                }
                all_products.append(product_data)
                found_products_in_file += 1
            except Exception:
                pass
                
    print(f"Encontrados e processados {found_products_in_file} registros de produtos neste arquivo.")
    return all_products

if __name__ == "__main__":
    higiplas_data = parse_report_html("2015 - 2025 - HIGIPLAS.html")
    higitec_data = parse_report_html("2020 - 2025 - HIGITEC.html")

    if not higiplas_data and not higitec_data:
        print("\n❌ ERRO FATAL: Nenhum dado foi extraído dos arquivos.")
    else:
        # A nova lógica de combinação de dados:
        # Cria um dicionário para agrupar os dados por 'ident_antigo'
        combined_data = {}
        for item in (higiplas_data + higitec_data):
            key = item['ident_antigo']
            if key not in combined_data:
                combined_data[key] = item
            else:
                # Se já existe, soma os valores numéricos
                for field in ["quantidade_vendida_total", "custo_compra_total", "valor_vendido_total", "lucro_bruto_total"]:
                    combined_data[key][field] += item[field]
        
        final_list = list(combined_data.values())

        output_file = "dados_historicos_vendas.json"
        
        # O arquivo será salvo na raiz da pasta `backend`, mova-o para `backend/app` depois.
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_list, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Concluído! {len(final_list)} registros únicos totais de vendas foram salvos em '{output_file}'.")
        print("--> PRÓXIMO PASSO: Mova este arquivo para a pasta 'backend/app/' e faça o commit.")