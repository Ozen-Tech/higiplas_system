#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para processar movimentações de estoque fazendo correspondência por nome do produto
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from difflib import SequenceMatcher

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.connection import get_db
from app.db import models
from app.schemas import movimentacao_estoque as schemas_movimentacao
from app.crud import movimentacao_estoque as crud_movimentacao

def similarity(a, b):
    """Calcula a similaridade entre duas strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def encontrar_produto_por_nome(db, nome_produto, empresa_id, threshold=0.6):
    """Encontra produto por similaridade de nome."""
    produtos = db.query(models.Produto).filter(
        models.Produto.empresa_id == empresa_id
    ).all()
    
    melhor_produto = None
    melhor_score = 0
    
    for produto in produtos:
        score = similarity(nome_produto, produto.nome)
        if score > melhor_score and score >= threshold:
            melhor_score = score
            melhor_produto = produto
    
    return melhor_produto, melhor_score

def processar_movimentacoes_por_nome():
    """Processa movimentações fazendo correspondência por nome do produto."""
    
    print("=== Processador de Movimentações por Nome ===")
    
    # Caminho do arquivo JSON
    json_path = Path("/Users/ozen/higiplas_system/backend/dados_movimentacao_estoque.json")
    
    if not json_path.exists():
        print(f"❌ Arquivo JSON não encontrado: {json_path}")
        return
    
    # Carregar dados do JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    if not dados.get('movimentacoes'):
        print("❌ Nenhuma movimentação encontrada no JSON")
        return
    
    # Obter sessão do banco de dados
    db = next(get_db())
    
    # Buscar qualquer usuário disponível
    usuario_admin = db.query(models.Usuario).first()
    if not usuario_admin:
        print("❌ Nenhum usuário encontrado no banco de dados")
        return
    
    print(f"👤 Processando como usuário: {usuario_admin.nome} (ID: {usuario_admin.id})")
    print(f"🏢 Empresa: {usuario_admin.empresa_id}")
    
    total_movimentacoes = 0
    total_produtos_processados = 0
    total_produtos_nao_encontrados = 0
    total_produtos_encontrados_por_nome = 0
    
    print(f"\n📦 Processando {len(dados['movimentacoes'])} movimentações...")
    
    for movimentacao_data in dados['movimentacoes']:
        arquivo = movimentacao_data.get('arquivo', 'N/A')
        tipo = movimentacao_data.get('tipo', 'saida').upper()
        nota_fiscal = movimentacao_data.get('nota_fiscal', 'N/A')
        cliente = movimentacao_data.get('cliente', 'N/A')
        produtos = movimentacao_data.get('produtos', [])
        
        print(f"\n📄 Processando: {arquivo}")
        print(f"   📊 NF: {nota_fiscal}")
        print(f"   👥 Cliente: {cliente}")
        print(f"   📦 Produtos: {len(produtos)}")
        
        movimentacoes_criadas = 0
        produtos_nao_encontrados = 0
        produtos_encontrados_por_nome = 0
        
        for produto_data in produtos:
            codigo = produto_data.get('codigo')
            quantidade = produto_data.get('quantidade', 0)
            descricao = produto_data.get('descricao', 'N/A')
            
            if not descricao or descricao == 'N/A' or quantidade <= 0:
                continue
            
            # Primeiro, tentar buscar pelo código
            produto = db.query(models.Produto).filter(
                models.Produto.codigo == str(codigo),
                models.Produto.empresa_id == usuario_admin.empresa_id
            ).first()
            
            # Se não encontrou pelo código, tentar por nome
            if not produto:
                produto, score = encontrar_produto_por_nome(
                    db, descricao, usuario_admin.empresa_id
                )
                if produto:
                    produtos_encontrados_por_nome += 1
                    print(f"      🔍 Produto encontrado por nome: {descricao} → {produto.nome} (score: {score:.2f})")
            
            if not produto:
                produtos_nao_encontrados += 1
                print(f"      ⚠️  Produto não encontrado: {codigo} - {descricao}")
                continue
            
            # Verificar se a movimentação já existe (evitar duplicatas)
            observacao = f"Processamento automático - NF {nota_fiscal} - {descricao}"
            
            movimentacao_existente = db.query(models.MovimentacaoEstoque).filter(
                models.MovimentacaoEstoque.produto_id == produto.id,
                models.MovimentacaoEstoque.observacao == observacao
            ).first()
            
            if movimentacao_existente:
                print(f"      ℹ️  Movimentação já existe para produto {produto.codigo}")
                continue
            
            # Criar movimentação
            movimentacao_create = schemas_movimentacao.MovimentacaoEstoqueCreate(
                produto_id=produto.id,
                tipo_movimentacao=tipo,
                quantidade=quantidade,
                observacao=observacao
            )
            
            try:
                produto_atualizado = crud_movimentacao.create_movimentacao_estoque(
                    db=db,
                    movimentacao=movimentacao_create,
                    usuario_id=usuario_admin.id,
                    empresa_id=usuario_admin.empresa_id
                )
                
                movimentacoes_criadas += 1
                estoque_anterior = produto_atualizado.quantidade_em_estoque - (quantidade if tipo == 'ENTRADA' else -quantidade)
                
                print(f"      ✅ {produto.codigo} - {produto.nome}: {quantidade} unidades ({tipo})")
                print(f"         Estoque: {estoque_anterior} → {produto_atualizado.quantidade_em_estoque}")
                
            except Exception as e:
                produtos_nao_encontrados += 1
                print(f"      ❌ Erro ao processar {codigo}: {str(e)}")
        
        print(f"   📈 Movimentações criadas: {movimentacoes_criadas}")
        print(f"   🔍 Produtos encontrados por nome: {produtos_encontrados_por_nome}")
        print(f"   ⚠️  Produtos não encontrados: {produtos_nao_encontrados}")
        
        total_movimentacoes += movimentacoes_criadas
        total_produtos_processados += movimentacoes_criadas
        total_produtos_nao_encontrados += produtos_nao_encontrados
        total_produtos_encontrados_por_nome += produtos_encontrados_por_nome
    
    print(f"\n📊 Resumo Final:")
    print(f"   - Total de movimentações criadas: {total_movimentacoes}")
    print(f"   - Total de produtos processados: {total_produtos_processados}")
    print(f"   - Total de produtos encontrados por nome: {total_produtos_encontrados_por_nome}")
    print(f"   - Total de produtos não encontrados: {total_produtos_nao_encontrados}")
    
    db.close()
    print("\n✅ Processamento concluído!")

if __name__ == "__main__":
    processar_movimentacoes_por_nome()