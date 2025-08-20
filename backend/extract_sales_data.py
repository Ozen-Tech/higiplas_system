import pdfplumber
import re
import json
import os

def parse_float(value_str):
    """Converte uma string de valor para float."""
    return float(value_str.replace('.', '').replace(',', '.'))

def extract_sales_data_from_pdfs(pdf_paths):
    """Extrai dados de vendas de uma lista de arquivos PDF."""
    sales_data = []
    item_pattern = re.compile(r'^Item: (\d+) - (.*)$')
    client_sale_pattern = re.compile(r'^(\d+)\s+(.*?)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,-]+)\s+([\d.,-]+)$')

    for pdf_path in pdf_paths:
        print(f"Processando o arquivo: {os.path.basename(pdf_path)}")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                current_item = None
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        item_match = item_pattern.match(line)
                        if item_match:
                            current_item = {
                                "id": int(item_match.group(1)),
                                "nome": item_match.group(2).strip()
                            }
                            continue

                        if current_item:
                            sale_match = client_sale_pattern.match(line)
                            if sale_match:
                                try:
                                    client_id = int(sale_match.group(1))
                                    quantity = parse_float(sale_match.group(3))
                                    total_sold = parse_float(sale_match.group(4))
                                    
                                    sales_data.append({
                                        "produto_id": current_item["id"],
                                        "produto_nome": current_item["nome"],
                                        "cliente_id": client_id,
                                        "quantidade": quantity,
                                        "valor_vendido": total_sold,
                                        "empresa": "HIGIPLAS" if "HIGIPLAS" in pdf_path else "HIGITEC"
                                    })
                                except (ValueError, IndexError):
                                    # Ignora linhas que não correspondem ao padrão esperado
                                    pass
        except Exception as e:
            print(f"Erro ao processar o PDF {pdf_path}: {e}")

    return sales_data

if __name__ == "__main__":
    pdf_files = [
        "/Users/ozen/higiplas_system/backend/HIGIPLAS - MAIO - JULHO (1).pdf",
        "/Users/ozen/higiplas_system/backend/HIGITEC - MAIO - JULHO.pdf"
    ]
    
    extracted_data = extract_sales_data_from_pdfs(pdf_files)
    
    output_path = "/Users/ozen/higiplas_system/backend/dados_vendas_processados.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=4, ensure_ascii=False)
        
    print(f"\nDados de vendas extraídos e salvos em: {output_path}")
    print(f"Total de registros de vendas extraídos: {len(extracted_data)}")

    # Exibe os 5 primeiros registros para verificação
    if extracted_data:
        print("\n### Primeiros 5 registros extraídos: ###")
        for record in extracted_data[:5]:
            print(record)