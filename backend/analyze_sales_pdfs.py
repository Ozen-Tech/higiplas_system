import pdfplumber
import re
import json
import os

def extract_text_from_pdf(pdf_path):
    """Extrai texto de um arquivo PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Erro ao ler o PDF {pdf_path}: {e}")
        return None

def analyze_pdf_format(pdf_path):
    """Analisa e exibe o formato do texto extraído de um PDF."""
    print(f"--- Analisando o formato de: {os.path.basename(pdf_path)} ---")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("Não foi possível extrair texto do PDF.")
        return

    lines = text.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]

    print("\n### Primeiras 20 linhas não vazias ###")
    for line in non_empty_lines[:20]:
        print(line)

    # Padrões de regex para identificar informações relevantes
    price_pattern = re.compile(r'\b\d{1,3}(?:\.\d{3})*,\d{2}\b')
    product_pattern = re.compile(r'([A-ZÁÉÍÓÚÇÃÕÂÊÔÀÈÌÒÙÄËÏÖÜÑ\s/\-]+)')
    combined_pattern = re.compile(r'(\d+)\s+(.*?)\s+(\d+,\d+)\s+(\d+,\d+)')

    print("\n### Análise de Padrões ###")
    product_lines = []
    price_lines = []
    combined_lines = []

    for line in non_empty_lines:
        if price_pattern.search(line):
            price_lines.append(line)
        if product_pattern.match(line):
            product_lines.append(line)
        if combined_pattern.search(line):
            combined_lines.append(line)

    print(f"Linhas com padrão de produto encontradas: {len(product_lines)}")
    print(f"Linhas com padrão de preço encontradas: {len(price_lines)}")
    print(f"Linhas com padrão combinado (código, produto, valores) encontradas: {len(combined_lines)}")

    if combined_lines:
        print("\n### Exemplos de Linhas com Padrão Combinado ###")
        for i, line in enumerate(combined_lines[:5]):
            match = combined_pattern.search(line)
            if match:
                code, product, unit_price, total_price = match.groups()
                print(f"  Exemplo {i+1}: Código='{code}', Produto='{product}', Preço Unitário='{unit_price}', Preço Total='{total_price}'")

    print(f"--- Fim da análise de {os.path.basename(pdf_path)} ---\n")


if __name__ == "__main__":
    pdf_files = [
        "/Users/ozen/higiplas_system/backend/HIGIPLAS - MAIO - JULHO (1).pdf",
        "/Users/ozen/higiplas_system/backend/HIGITEC - MAIO - JULHO.pdf"
    ]

    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            analyze_pdf_format(pdf_file)
        else:
            print(f"Arquivo não encontrado: {pdf_file}")