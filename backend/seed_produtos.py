#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para popular a tabela produtos com dados de exemplo.
"""

import sys
import os
from datetime import date, datetime
from sqlalchemy.orm import Session

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.connection import get_db
from app.db.models import Produto, Empresa
from app.schemas.produto import ProdutoCreate
from app.crud.produto import create_produto

def seed_produtos():
    """Popula a tabela produtos com dados de exemplo."""
    
    # Conecta ao banco
    db: Session = next(get_db())
    
    try:
        # Verifica se já existem produtos
        existing_count = db.query(Produto).count()
        if existing_count > 0:
            print(f"⚠️  Já existem {existing_count} produtos no banco. Pulando seed...")
            return
        
        # Busca a empresa Higiplas
        empresa = db.query(Empresa).filter(Empresa.nome == "Higiplas").first()
        if not empresa:
            print("❌ Empresa Higiplas não encontrada. Execute primeiro o script de criação da empresa.")
            return
        
        print(f"🏢 Usando empresa: {empresa.nome} (ID: {empresa.id})")
        
        # Lista de produtos de exemplo baseados nos dados do usuário
        produtos_exemplo = [
            {
                "nome": "ALCOOL BIOELITICO 96% 1L",
                "codigo": "ALC001",
                "categoria": "Limpeza",
                "descricao": "Álcool bioetílico 96% para limpeza",
                "preco_custo": 8.50,
                "preco_venda": 12.90,
                "unidade_medida": "UN",
                "estoque_minimo": 10,
                "quantidade_em_estoque": 25,
                "data_validade": date(2025, 12, 31)
            },
            {
                "nome": "CLORMAQ BB5L",
                "codigo": "CLR001",
                "categoria": "Limpeza",
                "descricao": "Desinfetante clorado 5 litros",
                "preco_custo": 45.00,
                "preco_venda": 68.50,
                "unidade_medida": "UN",
                "estoque_minimo": 5,
                "quantidade_em_estoque": 15,
                "data_validade": date(2025, 6, 30)
            },
            {
                "nome": "COLETOR P/ ABSORVENTE",
                "codigo": "COL001",
                "categoria": "Higiene",
                "descricao": "Coletor para absorvente feminino",
                "preco_custo": 15.00,
                "preco_venda": 22.90,
                "unidade_medida": "UN",
                "estoque_minimo": 8,
                "quantidade_em_estoque": 12,
                "data_validade": None
            },
            {
                "nome": "ESCOVA SANITÁRIA COM SUPORTE",
                "codigo": "ESC001",
                "categoria": "Limpeza",
                "descricao": "Escova sanitária com suporte plástico",
                "preco_custo": 12.00,
                "preco_venda": 18.50,
                "unidade_medida": "UN",
                "estoque_minimo": 6,
                "quantidade_em_estoque": 20,
                "data_validade": None
            },
            {
                "nome": "ESPANADOR ELETROESTÁTICO",
                "codigo": "ESP001",
                "categoria": "Limpeza",
                "descricao": "Espanador eletroestático para móveis",
                "preco_custo": 8.90,
                "preco_venda": 14.90,
                "unidade_medida": "UN",
                "estoque_minimo": 10,
                "quantidade_em_estoque": 30,
                "data_validade": None
            },
            {
                "nome": "FD PAPEL HIGIÊNICO MILI",
                "codigo": "PAP001",
                "categoria": "Higiene",
                "descricao": "Papel higiênico folha dupla Mili",
                "preco_custo": 2.50,
                "preco_venda": 4.20,
                "unidade_medida": "UN",
                "estoque_minimo": 50,
                "quantidade_em_estoque": 100,
                "data_validade": date(2026, 3, 15)
            },
            {
                "nome": "ESPONJA DUPLA FACE",
                "codigo": "ESP002",
                "categoria": "Limpeza",
                "descricao": "Esponja dupla face para limpeza",
                "preco_custo": 0.65,
                "preco_venda": 0.97,
                "unidade_medida": "UN",
                "estoque_minimo": 100,
                "quantidade_em_estoque": 250,
                "data_validade": None
            },
            {
                "nome": "ALUMICROST",
                "codigo": "ALU001",
                "categoria": "Limpeza",
                "descricao": "Limpa alumínio concentrado",
                "preco_custo": 98.50,
                "preco_venda": 145.87,
                "unidade_medida": "UN",
                "estoque_minimo": 3,
                "quantidade_em_estoque": 8,
                "data_validade": date(2025, 8, 20)
            },
            {
                "nome": "GEL ANTISSEPTICO BB5L",
                "codigo": "GEL001",
                "categoria": "Higiene",
                "descricao": "Gel antisséptico para mãos 5 litros",
                "preco_custo": 85.20,
                "preco_venda": 126.31,
                "unidade_medida": "UN",
                "estoque_minimo": 5,
                "quantidade_em_estoque": 12,
                "data_validade": date(2025, 11, 30)
            },
            {
                "nome": "SUPORTE MOP PÓ 60 CM",
                "codigo": "SUP001",
                "categoria": "Limpeza",
                "descricao": "Suporte para mop de pó 60cm",
                "preco_custo": 26.80,
                "preco_venda": 39.80,
                "unidade_medida": "UN",
                "estoque_minimo": 5,
                "quantidade_em_estoque": 15,
                "data_validade": None
            }
        ]
        
        print(f"🌱 Inserindo {len(produtos_exemplo)} produtos de exemplo...")
        
        produtos_criados = 0
        for produto_data in produtos_exemplo:
            try:
                # Cria o schema Pydantic
                produto_schema = ProdutoCreate(**produto_data)
                
                # Cria o produto no banco
                produto_criado = create_produto(
                    db=db, 
                    produto=produto_schema, 
                    empresa_id=empresa.id
                )
                
                produtos_criados += 1
                print(f"✅ Produto criado: {produto_criado.nome} (ID: {produto_criado.id})")
                
            except Exception as e:
                print(f"❌ Erro ao criar produto {produto_data['nome']}: {str(e)}")
                continue
        
        print(f"\n🎉 Seed concluído! {produtos_criados} produtos foram criados com sucesso.")
        
    except Exception as e:
        print(f"❌ Erro durante o seed: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Iniciando seed de produtos...")
    seed_produtos()
    print("✨ Processo finalizado!")