# /backend/app/services/pdf_processor.py

import PyPDF2
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import os
from pathlib import Path

class PDFSalesProcessor:
    """Processador de PDFs de vendas para extrair dados históricos."""
    
    def __init__(self):
        self.backend_path = Path(__file__).parent.parent.parent
        self.pdf_files = [
            "HIGIPLAS - MAIO - JULHO.pdf",
            "HIGITEC - MAIO - JULHO.pdf"
        ]
        self.extracted_data = []
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrai texto de um arquivo PDF."""
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
    
    def parse_sales_data(self, text: str, company: str) -> List[Dict[str, Any]]:
        """Analisa o texto extraído e identifica dados de vendas baseado no formato específico dos PDFs."""
        sales_data = []
        lines = text.split('\n')
        
        current_item = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Identifica linha de item (formato: "Item: X - NOME DO PRODUTO")
            item_match = re.match(r'Item:\s*(\d+)\s*-\s*(.+)', line)
            if item_match:
                current_item = {
                    'codigo': item_match.group(1),
                    'produto': item_match.group(2).strip(),
                    'empresa': company,
                    'periodo': '2025-05-01 a 2025-07-31'
                }
                continue
            
            # Se temos um item atual, procura por linhas de dados de venda
            if current_item and not line.startswith('Cód.'):
                # Formato: "CODIGO CLIENTE QUANTIDADE CUSTO VENDIDO LUCRO PERCENTUAL"
                # Exemplo: "302 COLEGIO EDUCALLIS FIGUEIREDO LTDA 16,0000 292,8000 484,0000 191,2000 65,3005"
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        # Tenta extrair os dados numéricos do final da linha
                        numeric_parts = []
                        cliente_parts = []
                        
                        for part in parts[1:]:  # Pula o código do cliente
                            if re.match(r'^\d+[,.]\d+$', part):
                                numeric_parts.append(float(part.replace(',', '.')))
                            elif not numeric_parts:  # Ainda coletando nome do cliente
                                cliente_parts.append(part)
                        
                        if len(numeric_parts) >= 3:  # quantidade, custo, vendido
                            quantidade = numeric_parts[0]
                            valor_vendido = numeric_parts[2]  # Valor vendido
                            
                            sale_record = current_item.copy()
                            sale_record.update({
                                'cliente': ' '.join(cliente_parts),
                                'quantidade': quantidade,
                                'valor': valor_vendido
                            })
                            
                            sales_data.append(sale_record)
                            
                    except (ValueError, IndexError) as e:
                        continue
            
            # Verifica se chegou na linha de totais para resetar o item atual
            if 'Totais:' in line:
                current_item = None
        
        return sales_data
    
    def process_all_pdfs(self) -> Dict[str, Any]:
        """Processa todos os PDFs e retorna dados consolidados."""
        all_sales_data = []
        processing_summary = {
            'files_processed': 0,
            'total_sales_records': 0,
            'companies': [],
            'processing_date': datetime.now().isoformat(),
            'period': '2025-05-01 a 2025-07-31'
        }
        
        for pdf_file in self.pdf_files:
            pdf_path = self.backend_path / pdf_file
            
            if not pdf_path.exists():
                print(f"Arquivo não encontrado: {pdf_path}")
                continue
            
            print(f"Processando: {pdf_file}")
            
            # Extrai texto do PDF
            text = self.extract_text_from_pdf(str(pdf_path))
            
            if not text:
                continue
            
            # Determina a empresa baseada no nome do arquivo
            company = "HIGIPLAS" if "HIGIPLAS" in pdf_file else "HIGITEC"
            
            # Analisa dados de vendas
            sales_data = self.parse_sales_data(text, company)
            
            all_sales_data.extend(sales_data)
            processing_summary['files_processed'] += 1
            
            if company not in processing_summary['companies']:
                processing_summary['companies'].append(company)
        
        processing_summary['total_sales_records'] = len(all_sales_data)
        
        # Salva dados processados
        self.save_processed_data(all_sales_data, processing_summary)
        
        return {
            'sales_data': all_sales_data,
            'summary': processing_summary
        }
    
    def save_processed_data(self, sales_data: List[Dict], summary: Dict):
        """Salva os dados processados em arquivo JSON."""
        output_file = self.backend_path / 'app' / 'dados_vendas_pdf_processados.json'
        
        data_to_save = {
            'metadata': summary,
            'sales_data': sales_data
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            print(f"Dados salvos em: {output_file}")
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
    
    def get_top_selling_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna os produtos mais vendidos baseado nos dados processados."""
        data_file = self.backend_path / 'app' / 'dados_vendas_pdf_processados.json'
        
        if not data_file.exists():
            return []
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sales_data = data.get('sales_data', [])
            
            # Agrupa por produto
            product_sales = {}
            for sale in sales_data:
                produto = sale.get('produto', 'Produto Desconhecido')
                quantidade = sale.get('quantidade', 0)
                valor = sale.get('valor', 0)
                
                if produto not in product_sales:
                    product_sales[produto] = {
                        'produto': produto,
                        'total_quantidade': 0,
                        'total_valor': 0,
                        'numero_vendas': 0
                    }
                
                product_sales[produto]['total_quantidade'] += quantidade
                product_sales[produto]['total_valor'] += valor
                product_sales[produto]['numero_vendas'] += 1
            
            # Ordena por quantidade vendida
            top_products = sorted(
                product_sales.values(),
                key=lambda x: x['total_quantidade'],
                reverse=True
            )[:limit]
            
            return top_products
            
        except Exception as e:
            print(f"Erro ao processar produtos mais vendidos: {e}")
            return []
    
    def calculate_minimum_stock(self, product_name: str) -> Dict[str, Any]:
        """Calcula estoque mínimo baseado nos dados de vendas."""
        data_file = self.backend_path / 'app' / 'dados_vendas_pdf_processados.json'
        
        if not data_file.exists():
            return {'error': 'Dados não processados'}
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sales_data = data.get('sales_data', [])
            
            # Filtra vendas do produto específico
            product_sales = [
                sale for sale in sales_data 
                if sale.get('produto', '').lower() == product_name.lower()
            ]
            
            if not product_sales:
                return {'error': f'Produto {product_name} não encontrado nos dados'}
            
            # Calcula métricas
            total_vendido = sum(sale.get('quantidade', 0) for sale in product_sales)
            numero_vendas = len(product_sales)
            media_por_venda = total_vendido / numero_vendas if numero_vendas > 0 else 0
            
            # Período de 3 meses (maio-julho)
            periodo_dias = 92  # aproximadamente 3 meses
            media_diaria = total_vendido / periodo_dias
            
            # Estoque mínimo: 15 dias de vendas + margem de segurança (20%)
            estoque_minimo = int((media_diaria * 15) * 1.2)
            
            return {
                'produto': product_name,
                'total_vendido_periodo': total_vendido,
                'numero_vendas': numero_vendas,
                'media_por_venda': round(media_por_venda, 2),
                'media_diaria': round(media_diaria, 2),
                'estoque_minimo_sugerido': estoque_minimo,
                'periodo_analise': '2025-05-01 a 2025-07-31',
                'criterio': '15 dias de vendas + 20% margem de segurança'
            }
            
        except Exception as e:
            print(f"Erro ao calcular estoque mínimo: {e}")
            return {'error': str(e)}

# Instância global do processador
pdf_processor = PDFSalesProcessor()