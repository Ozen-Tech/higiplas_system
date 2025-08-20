#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para processar PDFs de movimentação existentes e atualizar o banco de dados
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
from app.routers.movimentacoes import extrair_dados_pdf

def processar_pdfs_existentes():
    """Processa todos os PDFs de movimentação existentes."""
    
    print("=== Processador de PDFs de Movimentação Existentes ===")
    
    # Caminhos dos diretórios
    base_dir = Path("/Users/ozen/higiplas_system")
    entrada_dir = base_dir / "dados de baixa e entrada no estoque" / "entrada"
    saida_dir = base_dir / "dados de baixa e entrada no estoque" / "saida"
    
    # Verificar se os diretórios existem
    if not entrada_dir.exists():
        print(f"❌ Diretório de entrada não encontrado: {entrada_dir}")
        return
    
    if not saida_dir.exists():
        print(f"❌ Diretório de saída não encontrado: {saida_dir}")
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
    
    # Processar PDFs de entrada
    print("\n📥 Processando PDFs de ENTRADA...")
    processar_diretorio(entrada_dir, "ENTRADA", db, usuario_admin)
    
    # Processar PDFs de saída
    print("\n📤 Processando PDFs de SAÍDA...")
    processar_diretorio(saida_dir, "SAIDA", db, usuario_admin)
    
    db.close()
    print("\n✅ Processamento concluído!")

def processar_diretorio(diretorio: Path, tipo_movimentacao: str, db: Session, usuario: models.Usuario):
    """Processa todos os PDFs de um diretório específico."""
    
    pdfs = list(diretorio.glob("*.pdf")) + list(diretorio.glob("*.PDF"))
    
    if not pdfs:
        print(f"   ⚠️  Nenhum PDF encontrado em {diretorio}")
        return
    
    print(f"   📁 Encontrados {len(pdfs)} PDFs")
    
    total_movimentacoes = 0
    total_produtos_processados = 0
    total_produtos_nao_encontrados = 0
    
    for pdf_path in pdfs:
        print(f"\n   📄 Processando: {pdf_path.name}")
        
        try:
            # Extrair dados do PDF
            dados_extraidos = extrair_dados_pdf(str(pdf_path))
            
            if not dados_extraidos or not dados_extraidos.get('produtos'):
                print(f"      ❌ Não foi possível extrair dados válidos")
                continue
            
            print(f"      📊 NF: {dados_extraidos.get('nota_fiscal', 'N/A')}")
            print(f"      📅 Data: {dados_extraidos.get('data_emissao', 'N/A')}")
            print(f"      👥 Cliente: {dados_extraidos.get('cliente', 'N/A')}")
            print(f"      📦 Produtos encontrados: {len(dados_extraidos['produtos'])}")
            
            movimentacoes_criadas = 0
            produtos_nao_encontrados = 0
            
            for produto_data in dados_extraidos['produtos']:
                codigo = produto_data.get('codigo')
                quantidade = produto_data.get('quantidade', 0)
                
                if not codigo or quantidade <= 0:
                    continue
                
                # Buscar produto pelo código
                produto = db.query(models.Produto).filter(
                    models.Produto.codigo == str(codigo),
                    models.Produto.empresa_id == usuario.empresa_id
                ).first()
                
                if not produto:
                    produtos_nao_encontrados += 1
                    print(f"         ⚠️  Produto não encontrado: {codigo} - {produto_data.get('descricao', 'N/A')}")
                    continue
                
                # Verificar se a movimentação já existe (evitar duplicatas)
                observacao = f"Processamento automático - NF {dados_extraidos.get('nota_fiscal', 'N/A')} - {produto_data.get('descricao', '')}"
                
                movimentacao_existente = db.query(models.MovimentacaoEstoque).filter(
                    models.MovimentacaoEstoque.produto_id == produto.id,
                    models.MovimentacaoEstoque.observacao == observacao
                ).first()
                
                if movimentacao_existente:
                    print(f"         ℹ️  Movimentação já existe para produto {codigo}")
                    continue
                
                # Criar movimentação
                movimentacao_data = schemas_movimentacao.MovimentacaoEstoqueCreate(
                    produto_id=produto.id,
                    tipo_movimentacao=tipo_movimentacao,
                    quantidade=quantidade,
                    observacao=observacao
                )
                
                try:
                    produto_atualizado = crud_movimentacao.create_movimentacao_estoque(
                        db=db,
                        movimentacao=movimentacao_data,
                        usuario_id=usuario.id,
                        empresa_id=usuario.empresa_id
                    )
                    
                    movimentacoes_criadas += 1
                    print(f"         ✅ {codigo} - {produto.nome}: {quantidade} unidades ({tipo_movimentacao})")
                    
                except Exception as e:
                    produtos_nao_encontrados += 1
                    print(f"         ❌ Erro ao processar {codigo}: {str(e)}")
            
            print(f"      📈 Movimentações criadas: {movimentacoes_criadas}")
            print(f"      ⚠️  Produtos não encontrados: {produtos_nao_encontrados}")
            
            total_movimentacoes += movimentacoes_criadas
            total_produtos_processados += movimentacoes_criadas
            total_produtos_nao_encontrados += produtos_nao_encontrados
            
        except Exception as e:
            print(f"      ❌ Erro ao processar PDF: {str(e)}")
    
    print(f"\n   📊 Resumo do diretório {tipo_movimentacao}:")
    print(f"      - Total de movimentações criadas: {total_movimentacoes}")
    print(f"      - Total de produtos processados: {total_produtos_processados}")
    print(f"      - Total de produtos não encontrados: {total_produtos_nao_encontrados}")

if __name__ == "__main__":
    processar_pdfs_existentes()