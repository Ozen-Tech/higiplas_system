#!/usr/bin/env python3
"""
Script para analisar PDFs de movimentação de estoque (entrada e saída)
"""

import os
import sys
import json
from pathlib import Path
import PyPDF2
import pdfplumber
import re
from datetime import datetime

def extract_text_from_pdf(pdf_path):
    """Extrai texto de um PDF usando múltiplas bibliotecas"""
    text_content = ""
    
    # Tentar com pdfplumber primeiro (melhor para tabelas)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
    except Exception as e:
        print(f"Erro com pdfplumber: {e}")
    
    # Se não conseguiu extrair com pdfplumber, tentar PyPDF2
    if not text_content.strip():
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
        except Exception as e:
            print(f"Erro com PyPDF2: {e}")
    
    return text_content

def analyze_movement_pdf_structure(pdf_path):
    """Analisa a estrutura de um PDF de movimentação"""
    print(f"\n=== Analisando: {os.path.basename(pdf_path)} ===")
    
    # Extrair texto
    text = extract_text_from_pdf(pdf_path)
    
    if not text.strip():
        print("❌ Não foi possível extrair texto do PDF")
        return None
    
    print(f"✅ Texto extraído ({len(text)} caracteres)")
    
    # Salvar texto extraído para análise
    output_file = f"movimento_text_{os.path.basename(pdf_path).replace('.PDF', '.txt')}"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"📄 Texto salvo em: {output_file}")
    
    # Análise básica do conteúdo
    lines = text.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    print(f"📊 Estatísticas:")
    print(f"   - Total de linhas: {len(lines)}")
    print(f"   - Linhas não vazias: {len(non_empty_lines)}")
    
    # Procurar por padrões comuns em notas fiscais
    patterns = {
        'nota_fiscal': r'nota\s+fiscal|nf|n\.f\.',
        'data': r'\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}',
        'valor': r'R\$\s*\d+[,.]\d{2}|\d+[,.]\d{2}',
        'quantidade': r'\b\d+[,.]\d+\b|\b\d+\b',
        'codigo': r'\b\d{3,}\b',
        'cnpj': r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',
        'produto': r'[A-Z][A-Z\s]{10,}',
    }
    
    found_patterns = {}
    for pattern_name, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            found_patterns[pattern_name] = matches[:5]  # Primeiros 5 matches
    
    print(f"🔍 Padrões encontrados:")
    for pattern_name, matches in found_patterns.items():
        print(f"   - {pattern_name}: {len(re.findall(patterns[pattern_name], text, re.IGNORECASE))} ocorrências")
        if matches:
            print(f"     Exemplos: {matches}")
    
    # Procurar por estrutura de tabela
    table_indicators = ['ITEM', 'CÓDIGO', 'DESCRIÇÃO', 'QTD', 'VALOR', 'TOTAL', 'PRODUTO']
    table_lines = []
    for line in non_empty_lines:
        line_upper = line.upper()
        if any(indicator in line_upper for indicator in table_indicators):
            table_lines.append(line)
    
    if table_lines:
        print(f"📋 Possíveis cabeçalhos de tabela encontrados:")
        for line in table_lines[:3]:
            print(f"   - {line}")
    
    return {
        'file': os.path.basename(pdf_path),
        'text_length': len(text),
        'lines_count': len(non_empty_lines),
        'patterns': found_patterns,
        'table_headers': table_lines,
        'sample_text': non_empty_lines[:10] if non_empty_lines else []
    }

def main():
    """Função principal"""
    print("=== Analisador de PDFs de Movimentação de Estoque ===")
    
    # Diretórios de entrada e saída
    base_dir = Path("../dados de baixa e entrada no estoque")
    entrada_dir = base_dir / "entrada"
    saida_dir = base_dir / "saida"
    
    results = {
        'entrada': [],
        'saida': [],
        'analysis_date': datetime.now().isoformat()
    }
    
    # Analisar PDFs de entrada
    print("\n🔄 Analisando PDFs de ENTRADA...")
    if entrada_dir.exists():
        for pdf_file in entrada_dir.glob("*.PDF"):
            try:
                result = analyze_movement_pdf_structure(pdf_file)
                if result:
                    results['entrada'].append(result)
            except Exception as e:
                print(f"❌ Erro ao analisar {pdf_file}: {e}")
    else:
        print("⚠️  Diretório de entrada não encontrado")
    
    # Analisar PDFs de saída
    print("\n🔄 Analisando PDFs de SAÍDA...")
    if saida_dir.exists():
        for pdf_file in saida_dir.glob("*.PDF"):
            try:
                result = analyze_movement_pdf_structure(pdf_file)
                if result:
                    results['saida'].append(result)
            except Exception as e:
                print(f"❌ Erro ao analisar {pdf_file}: {e}")
    else:
        print("⚠️  Diretório de saída não encontrado")
    
    # Salvar resultados
    output_file = "movement_pdfs_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Análise concluída!")
    print(f"📊 Resumo:")
    print(f"   - PDFs de entrada analisados: {len(results['entrada'])}")
    print(f"   - PDFs de saída analisados: {len(results['saida'])}")
    print(f"   - Resultados salvos em: {output_file}")
    
    return results

if __name__ == "__main__":
    try:
        results = main()
        print("\n🎉 Script executado com sucesso!")
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        sys.exit(1)