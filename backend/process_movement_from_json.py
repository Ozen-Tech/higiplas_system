#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para processar movimentações de estoque usando dados já extraídos do JSON
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.connection import get_db
from app.db import models
from app.schemas import movimentacao_estoque as schemas_movimentacao
from app.crud import movimentacao_estoque as crud_movimentacao

def processar_movimentacoes_do_json():
    """Processa movimentações usando dados já extraídos do JSON."""
    
    print("=== Processador de Movimentações de Estoque (JSON) ===")
    
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
        
        for produto_data in produtos:
            codigo = produto_data.get('codigo')
            quantidade = produto_data.get('quantidade', 0)
            descricao = produto_data.get('descricao', 'N/A')
            
            if not codigo or quantidade <= 0:
                continue
            
            # Buscar produto pelo código
            produto = db.query(models.Produto).filter(
                models.Produto.codigo == str(codigo),
                models.Produto.empresa_id == usuario_admin.empresa_id
            ).first()
            
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
                print(f"      ℹ️  Movimentação já existe para produto {codigo}")
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
                estoque_anterior = produto_atualizado.quantidade_estoque - (quantidade if tipo == 'ENTRADA' else -quantidade)
                
                print(f"      ✅ {codigo} - {produto.nome}: {quantidade} unidades ({tipo})")
                print(f"         Estoque: {estoque_anterior} → {produto_atualizado.quantidade_estoque}")
                
            except Exception as e:
                produtos_nao_encontrados += 1
                print(f"      ❌ Erro ao processar {codigo}: {str(e)}")
        
        print(f"   📈 Movimentações criadas: {movimentacoes_criadas}")
        print(f"   ⚠️  Produtos não encontrados: {produtos_nao_encontrados}")
        
        total_movimentacoes += movimentacoes_criadas
        total_produtos_processados += movimentacoes_criadas
        total_produtos_nao_encontrados += produtos_nao_encontrados
    
    print(f"\n📊 Resumo Final:")
    print(f"   - Total de movimentações criadas: {total_movimentacoes}")
    print(f"   - Total de produtos processados: {total_produtos_processados}")
    print(f"   - Total de produtos não encontrados: {total_produtos_nao_encontrados}")
    
    db.close()
    print("\n✅ Processamento concluído!")

if __name__ == "__main__":
    processar_movimentacoes_do_json()