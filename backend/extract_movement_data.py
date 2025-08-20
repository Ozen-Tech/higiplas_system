#!/usr/bin/env python3
"""
Script para extrair dados estruturados dos PDFs de movimentação de estoque
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
import pdfplumber
from typing import List, Dict, Optional

def extract_text_from_pdf(pdf_path):
    """Extrai texto de um PDF usando pdfplumber"""
    text_content = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
    except Exception as e:
        print(f"Erro ao extrair texto de {pdf_path}: {e}")
    return text_content

def parse_movement_pdf(pdf_path: str) -> Optional[Dict]:
    """Extrai dados estruturados de um PDF de movimentação"""
    print(f"\n📄 Processando: {os.path.basename(pdf_path)}")
    
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        print("❌ Não foi possível extrair texto")
        return None
    
    # Dados básicos da nota fiscal
    movement_data = {
        'arquivo': os.path.basename(pdf_path),
        'tipo': 'saida',  # Todos os PDFs estão na pasta saida
        'data_processamento': datetime.now().isoformat(),
        'nota_fiscal': None,
        'data_emissao': None,
        'cliente': None,
        'cnpj_cliente': None,
        'valor_total': None,
        'produtos': []
    }
    
    # Extrair número da nota fiscal
    nf_match = re.search(r'NFe\s+Nº\s+(\d+)', text)
    if nf_match:
        movement_data['nota_fiscal'] = nf_match.group(1)
    
    # Extrair data de emissão
    data_match = re.search(r'Data de Emissão\s+(\d{2}/\d{2}/\d{4})', text)
    if not data_match:
        data_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
    if data_match:
        movement_data['data_emissao'] = data_match.group(1)
    
    # Extrair cliente (destinatário)
    cliente_match = re.search(r'Destinatário:?\s*([^-]+?)\s*-', text)
    if cliente_match:
        movement_data['cliente'] = cliente_match.group(1).strip()
    
    # Extrair CNPJ do cliente
    cnpj_matches = re.findall(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', text)
    if len(cnpj_matches) >= 2:  # Primeiro é da empresa, segundo do cliente
        movement_data['cnpj_cliente'] = cnpj_matches[1]
    
    # Extrair valor total
    valor_match = re.search(r'Valor Total da Nota\s+Fiscal\s+([\d.,]+)', text)
    if valor_match:
        valor_str = valor_match.group(1).replace('.', '').replace(',', '.')
        try:
            movement_data['valor_total'] = float(valor_str)
        except ValueError:
            pass
    
    # Extrair produtos da tabela
    produtos = extract_products_from_text(text)
    movement_data['produtos'] = produtos
    
    print(f"✅ Extraído: NF {movement_data['nota_fiscal']}, {len(produtos)} produtos")
    return movement_data

def extract_products_from_text(text: str) -> List[Dict]:
    """Extrai produtos da seção 'Dados dos Produtos'"""
    produtos = []
    
    # Procurar pela seção de dados dos produtos
    lines = text.split('\n')
    in_products_section = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Identificar início da seção de produtos
        if 'Dados dos Produtos' in line or 'Cód. Prod.' in line:
            in_products_section = True
            continue
        
        # Identificar fim da seção de produtos
        if in_products_section and ('Dados Adicionais' in line or 'Informações Complementares' in line):
            break
        
        # Processar linhas de produtos
        if in_products_section and line and not line.startswith('Cód. Prod.'):
            produto = parse_product_line(line)
            if produto:
                produtos.append(produto)
    
    return produtos

def parse_product_line(line: str) -> Optional[Dict]:
    """Extrai dados de uma linha de produto"""
    # Padrão para linha de produto: número código descrição ... quantidade valor_unitario ... valor_total
    # Exemplo: "1 297 SUPORTE LT S/ CABO C/ PINCA P/ FIBRA (NOBRE) 96039000 0102 5102 UN 1,0000 19,1400 0,00 19,14"
    
    # Tentar extrair usando regex
    pattern = r'^(\d+)\s+(\d+)\s+(.+?)\s+(\d{8})\s+\d+\s+\d+\s+(\w+)\s+([\d,]+)\s+([\d,]+)\s+[\d,]+\s+([\d,]+)'
    match = re.match(pattern, line)
    
    if match:
        try:
            item_num = int(match.group(1))
            codigo = match.group(2)
            descricao = match.group(3).strip()
            ncm = match.group(4)
            unidade = match.group(5)
            quantidade_str = match.group(6).replace(',', '.')
            valor_unitario_str = match.group(7).replace(',', '.')
            valor_total_str = match.group(8).replace(',', '.')
            
            return {
                'item': item_num,
                'codigo': codigo,
                'descricao': descricao,
                'ncm': ncm,
                'unidade': unidade,
                'quantidade': float(quantidade_str),
                'valor_unitario': float(valor_unitario_str),
                'valor_total': float(valor_total_str)
            }
        except (ValueError, IndexError) as e:
            print(f"⚠️  Erro ao processar linha de produto: {line[:50]}... - {e}")
    
    return None

def main():
    """Função principal"""
    print("=== Extrator de Dados de Movimentação de Estoque ===")
    
    # Diretório de saída (onde estão os PDFs)
    saida_dir = Path("../dados de baixa e entrada no estoque/saida")
    
    if not saida_dir.exists():
        print(f"❌ Diretório não encontrado: {saida_dir}")
        return
    
    # Processar todos os PDFs
    all_movements = []
    pdf_files = list(saida_dir.glob("*.PDF"))
    
    print(f"📁 Encontrados {len(pdf_files)} PDFs para processar")
    
    for pdf_file in pdf_files:
        try:
            movement_data = parse_movement_pdf(pdf_file)
            if movement_data:
                all_movements.append(movement_data)
        except Exception as e:
            print(f"❌ Erro ao processar {pdf_file}: {e}")
    
    # Salvar dados extraídos
    output_file = "dados_movimentacao_estoque.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'movimentacoes': all_movements,
            'total_movimentacoes': len(all_movements),
            'data_extracao': datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    # Estatísticas
    total_produtos = sum(len(mov['produtos']) for mov in all_movements)
    total_valor = sum(mov['valor_total'] or 0 for mov in all_movements)
    
    print(f"\n✅ Processamento concluído!")
    print(f"📊 Estatísticas:")
    print(f"   - Movimentações processadas: {len(all_movements)}")
    print(f"   - Total de produtos: {total_produtos}")
    print(f"   - Valor total: R$ {total_valor:,.2f}")
    print(f"   - Dados salvos em: {output_file}")
    
    # Mostrar resumo por cliente
    clientes = {}
    for mov in all_movements:
        cliente = mov['cliente'] or 'Não identificado'
        if cliente not in clientes:
            clientes[cliente] = {'movimentacoes': 0, 'valor_total': 0}
        clientes[cliente]['movimentacoes'] += 1
        clientes[cliente]['valor_total'] += mov['valor_total'] or 0
    
    print(f"\n👥 Resumo por cliente:")
    for cliente, dados in sorted(clientes.items(), key=lambda x: x[1]['valor_total'], reverse=True):
        print(f"   - {cliente}: {dados['movimentacoes']} movimentações, R$ {dados['valor_total']:,.2f}")

if __name__ == "__main__":
    try:
        main()
        print("\n🎉 Script executado com sucesso!")
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        sys.exit(1)