#!/usr/bin/env python3
"""
Script para analisar o formato dos PDFs de compra e identificar padrões
"""

import sys
import os
from pathlib import Path
import re
from datetime import datetime
import PyPDF2

class PDFFormatAnalyzer:
    def __init__(self):
        self.backend_path = Path(__file__).parent
        self.purchase_files = [
            "COMPRA  - HIGIPLAS.pdf",
            "COMPRA  - HIGITEC.pdf"
        ]
        
    def extract_text_from_pdf(self, pdf_path):
        """Extrai texto do PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Erro ao extrair texto do PDF {pdf_path}: {e}")
            return ""
    
    def analyze_pdf_format(self, pdf_file):
        """Analisa o formato do PDF e mostra amostras de linhas"""
        pdf_path = self.backend_path / pdf_file
        
        if not pdf_path.exists():
            print(f"⚠️  Arquivo não encontrado: {pdf_file}")
            return
        
        print(f"\n=== ANALISANDO: {pdf_file} ===")
        
        # Extrair texto
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            print("❌ Falha ao extrair texto")
            return
        
        lines = text.split('\n')
        print(f"Total de linhas: {len(lines)}")
        
        # Mostrar primeiras 20 linhas não vazias
        print("\n--- PRIMEIRAS 20 LINHAS NÃO VAZIAS ---")
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        for i, line in enumerate(non_empty_lines[:20], 1):
            print(f"{i:2d}: {line}")
        
        # Procurar por padrões de números (possíveis preços)
        print("\n--- LINHAS COM PADRÕES DE PREÇOS ---")
        price_patterns = [
            r'\d+[,.]\d{2}',  # Números com 2 casas decimais
            r'\d{1,3}[,.]\d{2}\s+\d{1,5}[,.]\d{2}',  # Dois valores monetários
        ]
        
        price_lines = []
        for line in non_empty_lines:
            for pattern in price_patterns:
                if re.search(pattern, line):
                    price_lines.append(line)
                    break
        
        for i, line in enumerate(price_lines[:15], 1):
            print(f"{i:2d}: {line}")
        
        # Procurar por padrões de produtos
        print("\n--- LINHAS COM POSSÍVEIS PRODUTOS ---")
        product_lines = []
        for line in non_empty_lines:
            # Linhas que começam com letra maiúscula e têm pelo menos 10 caracteres
            if re.match(r'^[A-ZÁÊÇÕ][A-ZÁÊÇÕ\s\d/.-]{10,}', line):
                product_lines.append(line)
        
        for i, line in enumerate(product_lines[:15], 1):
            print(f"{i:2d}: {line}")
        
        # Procurar por linhas que podem conter produto + quantidade + preços
        print("\n--- LINHAS COM PRODUTO + NÚMEROS ---")
        combined_lines = []
        for line in non_empty_lines:
            # Linhas que têm texto + números
            if (re.search(r'^[A-ZÁÊÇÕ][A-ZÁÊÇÕ\s\d/.-]{5,}', line) and 
                re.search(r'\d+', line) and 
                len(line) > 15):
                combined_lines.append(line)
        
        for i, line in enumerate(combined_lines[:20], 1):
            print(f"{i:2d}: {line}")
    
    def analyze_all_pdfs(self):
        """Analisa todos os PDFs"""
        for pdf_file in self.purchase_files:
            self.analyze_pdf_format(pdf_file)

def main():
    analyzer = PDFFormatAnalyzer()
    analyzer.analyze_all_pdfs()

if __name__ == "__main__":
    main()