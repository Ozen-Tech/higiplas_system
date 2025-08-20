#!/usr/bin/env python3
"""
Script para integrar dados de compra com produtos existentes
Atualiza custos e calcula preços de venda
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

# Adicionar o diretório app ao path
sys.path.append(str(Path(__file__).parent / "app"))

from app.db.connection import engine
from app.db.models import Produto
# Imports removidos - usando SQLAlchemy diretamente

class PurchaseDataIntegrator:
    def __init__(self):
        self.backend_path = Path(__file__).parent
        self.purchase_data_file = self.backend_path / "app" / "dados_compras_pdf_processados_corrected.json"
        self.sales_data_file = self.backend_path / "app" / "dados_vendas_pdf_processados.json"
        self.margin_percentage = 0.30  # 30% de margem padrão
        
    def load_purchase_data(self):
        """Carrega dados de compra processados"""
        try:
            with open(self.purchase_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('dados_compra', [])
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {self.purchase_data_file}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
            return []
    
    def load_sales_data(self):
        """Carrega dados de vendas para calcular preços médios de venda"""
        try:
            with open(self.sales_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('dados_vendas', [])
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {self.sales_data_file}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
            return []
    
    def normalize_product_name(self, name):
        """Normaliza nome do produto para comparação"""
        if not name:
            return ""
        
        # Remove códigos numéricos no final
        import re
        normalized = re.sub(r'\s+\d+\s*$', '', name.strip())
        normalized = re.sub(r'\s+\d{3,}\s+\d{8,}\s*$', '', normalized)
        
        # Remove espaços extras
        normalized = ' '.join(normalized.split())
        
        return normalized.upper()
    
    def find_matching_product(self, db: Session, purchase_item):
        """Encontra produto correspondente no banco de dados"""
        purchase_name = self.normalize_product_name(purchase_item['produto'])
        
        # Buscar produtos existentes
        produtos = db.query(Produto).all()
        
        for produto in produtos:
            produto_name = self.normalize_product_name(produto.nome)
            
            # Comparação exata
            if produto_name == purchase_name:
                return produto
            
            # Comparação parcial (produto contém o nome da compra ou vice-versa)
            if len(purchase_name) > 10 and purchase_name in produto_name:
                return produto
            if len(produto_name) > 10 and produto_name in purchase_name:
                return produto
        
        return None
    
    def calculate_sale_price_from_sales_data(self, product_name, company, sales_data):
        """Calcula preço de venda baseado nos dados históricos de vendas"""
        normalized_name = self.normalize_product_name(product_name)
        
        matching_sales = []
        for sale in sales_data:
            sale_name = self.normalize_product_name(sale.get('produto', ''))
            sale_company = sale.get('empresa', '')
            
            if (normalized_name in sale_name or sale_name in normalized_name) and sale_company == company:
                if sale.get('quantidade', 0) > 0:
                    unit_price = sale.get('valor_total', 0) / sale.get('quantidade', 1)
                    matching_sales.append(unit_price)
        
        if matching_sales:
            return sum(matching_sales) / len(matching_sales)  # Preço médio
        
        return None
    
    def integrate_purchase_data(self):
        """Integra dados de compra com produtos existentes"""
        print("🔄 Integrando dados de compra com produtos existentes...")
        
        purchase_data = self.load_purchase_data()
        sales_data = self.load_sales_data()
        
        if not purchase_data:
            print("❌ Nenhum dado de compra encontrado")
            return
        
        updated_products = 0
        created_products = 0
        errors = 0
        
        with Session(engine) as db:
            # Agrupar dados de compra por produto
            product_costs = {}
            
            for item in purchase_data:
                key = f"{item['produto']}_{item['empresa']}"
                
                if key not in product_costs:
                    product_costs[key] = {
                        'produto': item['produto'],
                        'empresa': item['empresa'],
                        'total_quantidade': 0,
                        'total_custo': 0,
                        'registros': []
                    }
                
                product_costs[key]['total_quantidade'] += item['quantidade_comprada']
                product_costs[key]['total_custo'] += item['custo_total']
                product_costs[key]['registros'].append(item)
            
            # Processar cada produto agrupado
            for key, cost_data in product_costs.items():
                try:
                    # Calcular custo médio
                    if cost_data['total_quantidade'] > 0:
                        custo_medio = cost_data['total_custo'] / cost_data['total_quantidade']
                    else:
                        continue
                    
                    # Buscar produto existente
                    produto_existente = self.find_matching_product(db, cost_data)
                    
                    # Calcular preço de venda
                    preco_venda_historico = self.calculate_sale_price_from_sales_data(
                        cost_data['produto'], 
                        cost_data['empresa'], 
                        sales_data
                    )
                    
                    if preco_venda_historico:
                        preco_venda = preco_venda_historico
                    else:
                        # Usar margem padrão se não houver dados históricos
                        preco_venda = custo_medio * (1 + self.margin_percentage)
                    
                    if produto_existente:
                        # Atualizar produto existente
                        produto_existente.preco_custo = custo_medio
                        produto_existente.preco_venda = preco_venda
                        
                        db.commit()
                        updated_products += 1
                        
                        print(f"✅ Atualizado: {produto_existente.nome}")
                        print(f"   Custo: R$ {custo_medio:.2f} | Venda: R$ {preco_venda:.2f}")
                    
                    else:
                        # Criar novo produto
                        novo_produto = Produto(
                            nome=cost_data['produto'],
                            codigo=f"AUTO_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{created_products}",
                            categoria="IMPORTADO_COMPRA",
                            descricao=f"Produto importado dos dados de compra - {cost_data['empresa']}",
                            preco_custo=custo_medio,
                            preco_venda=preco_venda,
                            unidade_medida="UN",
                            estoque_minimo=0,
                            quantidade_em_estoque=0,
                            empresa_id=1  # Assumindo empresa padrão
                        )
                        
                        db.add(novo_produto)
                        db.commit()
                        created_products += 1
                        
                        print(f"🆕 Criado: {novo_produto.nome}")
                        print(f"   Custo: R$ {custo_medio:.2f} | Venda: R$ {preco_venda:.2f}")
                
                except Exception as e:
                    print(f"❌ Erro ao processar {cost_data['produto']}: {e}")
                    errors += 1
                    db.rollback()
                    continue
        
        print(f"\n=== RESUMO DA INTEGRAÇÃO ===")
        print(f"✅ Produtos atualizados: {updated_products}")
        print(f"🆕 Produtos criados: {created_products}")
        print(f"❌ Erros: {errors}")
        print(f"📊 Total processado: {len(product_costs)} produtos únicos")
    
    def generate_cost_report(self):
        """Gera relatório de custos atualizados"""
        print("\n🔄 Gerando relatório de custos...")
        
        with Session(engine) as db:
            # Buscar produtos com custo atualizado
            produtos_com_custo = db.query(Produto).filter(
                Produto.preco_custo.isnot(None),
                Produto.preco_custo > 0
            ).order_by(Produto.preco_custo.desc()).limit(20).all()
            
            print("\n=== TOP 20 PRODUTOS POR CUSTO ===")
            for i, produto in enumerate(produtos_com_custo, 1):
                margem = 0
                if produto.preco_custo and produto.preco_venda:
                    margem = ((produto.preco_venda - produto.preco_custo) / produto.preco_custo) * 100
                
                print(f"{i}. {produto.nome[:60]}...")
                print(f"   Custo: R$ {produto.preco_custo:.2f} | Venda: R$ {produto.preco_venda:.2f} | Margem: {margem:.1f}%")

def main():
    integrator = PurchaseDataIntegrator()
    
    # Integrar dados
    integrator.integrate_purchase_data()
    
    # Gerar relatório
    integrator.generate_cost_report()

if __name__ == "__main__":
    main()