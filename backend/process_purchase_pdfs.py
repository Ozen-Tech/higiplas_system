#!/usr/bin/env python3
"""
Script para processar PDFs de compra e extrair dados de custos e preços de venda
"""

import sys
import os
from pathlib import Path
import json
import re
from datetime import datetime
import PyPDF2
import pandas as pd
from decimal import Decimal, InvalidOperation

# Adicionar o diretório app ao path
sys.path.append(str(Path(__file__).parent / "app"))

class PurchasePDFProcessor:
    def __init__(self):
        self.backend_path = Path(__file__).parent
        self.purchase_files = [
            "COMPRA  - HIGIPLAS.pdf",
            "COMPRA  - HIGITEC.pdf"
        ]
        self.processed_data = []
        
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
    
    def clean_currency_value(self, value_str):
        """Limpa e converte valores monetários"""
        if not value_str:
            return 0.0
        
        # Remove espaços e caracteres especiais
        cleaned = re.sub(r'[^\d,.-]', '', str(value_str))
        
        # Substitui vírgula por ponto para decimais
        if ',' in cleaned and '.' in cleaned:
            # Se tem ambos, assume que vírgula é separador decimal
            cleaned = cleaned.replace('.', '').replace(',', '.')
        elif ',' in cleaned:
            # Se só tem vírgula, assume que é separador decimal
            cleaned = cleaned.replace(',', '.')
        
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    
    def extract_purchase_data(self, text, company):
        """Extrai dados de compra do texto do PDF"""
        lines = text.split('\n')
        current_data = []
        
        # Padrões para identificar produtos e valores
        product_patterns = [
            r'([A-ZÁÊÇÕ][A-ZÁÊÇÕ\s\d/.-]+)\s+(\d+[,.]?\d*)\s+([\d,.-]+)\s+([\d,.-]+)',
            r'([A-Z][A-Z\s\d/.-]{10,}).*?(\d+[,.]?\d*).*?([\d,.-]+).*?([\d,.-]+)',
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
                
            for pattern in product_patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        product_name = match.group(1).strip()
                        quantity = float(match.group(2).replace(',', '.'))
                        unit_cost = self.clean_currency_value(match.group(3))
                        total_cost = self.clean_currency_value(match.group(4))
                        
                        # Validações básicas
                        if len(product_name) > 5 and quantity > 0 and unit_cost > 0:
                            current_data.append({
                                'produto': product_name,
                                'empresa': company,
                                'quantidade_comprada': quantity,
                                'custo_unitario': unit_cost,
                                'custo_total': total_cost,
                                'data_processamento': datetime.now().isoformat()
                            })
                            break
                    except (ValueError, IndexError) as e:
                        continue
        
        return current_data
    
    def process_all_pdfs(self):
        """Processa todos os PDFs de compra"""
        print("🔄 Processando PDFs de compra...")
        
        for pdf_file in self.purchase_files:
            pdf_path = self.backend_path / pdf_file
            
            if not pdf_path.exists():
                print(f"⚠️  Arquivo não encontrado: {pdf_file}")
                continue
            
            print(f"Processando: {pdf_file}")
            
            # Determinar empresa
            company = "HIGIPLAS" if "HIGIPLAS" in pdf_file else "HIGITEC"
            
            # Extrair texto
            text = self.extract_text_from_pdf(pdf_path)
            
            if text:
                # Extrair dados
                purchase_data = self.extract_purchase_data(text, company)
                self.processed_data.extend(purchase_data)
                print(f"   ✅ Extraídos {len(purchase_data)} registros de compra")
            else:
                print(f"   ❌ Falha ao extrair texto do PDF")
        
        return self.processed_data
    
    def save_processed_data(self):
        """Salva os dados processados em JSON"""
        output_file = self.backend_path / "app" / "dados_compras_pdf_processados.json"
        
        summary = {
            "metadata": {
                "arquivos_processados": len(self.purchase_files),
                "total_registros_compra": len(self.processed_data),
                "empresas": list(set([item['empresa'] for item in self.processed_data])),
                "data_processamento": datetime.now().isoformat()
            },
            "dados_compra": self.processed_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"Dados salvos em: {output_file}")
        return output_file
    
    def generate_cost_analysis(self):
        """Gera análise de custos por produto"""
        if not self.processed_data:
            return
        
        # Agrupar por produto
        products_cost = {}
        
        for item in self.processed_data:
            product_key = f"{item['produto']} ({item['empresa']})"
            
            if product_key not in products_cost:
                products_cost[product_key] = {
                    'produto': item['produto'],
                    'empresa': item['empresa'],
                    'total_quantidade': 0,
                    'custo_total': 0,
                    'custo_medio': 0,
                    'registros': 0
                }
            
            products_cost[product_key]['total_quantidade'] += item['quantidade_comprada']
            products_cost[product_key]['custo_total'] += item['custo_total']
            products_cost[product_key]['registros'] += 1
        
        # Calcular custo médio
        for product in products_cost.values():
            if product['total_quantidade'] > 0:
                product['custo_medio'] = product['custo_total'] / product['total_quantidade']
        
        # Ordenar por custo total
        sorted_products = sorted(products_cost.values(), 
                               key=lambda x: x['custo_total'], reverse=True)
        
        print("\n=== TOP 10 PRODUTOS POR CUSTO TOTAL ===")
        for i, product in enumerate(sorted_products[:10], 1):
            print(f"{i}. {product['produto']} ({product['empresa']})")
            print(f"   Qtd: {product['total_quantidade']:.1f} - Custo Total: R$ {product['custo_total']:.2f}")
            print(f"   Custo Médio: R$ {product['custo_medio']:.2f}")
        
        return sorted_products

def main():
    processor = PurchasePDFProcessor()
    
    # Processar PDFs
    processed_data = processor.process_all_pdfs()
    
    if processed_data:
        print(f"\n✅ Total de {len(processed_data)} registros de compra extraídos")
        
        # Salvar dados
        processor.save_processed_data()
        
        # Gerar análise
        processor.generate_cost_analysis()
    else:
        print("❌ Nenhum dado de compra foi extraído")

if __name__ == "__main__":
    main()