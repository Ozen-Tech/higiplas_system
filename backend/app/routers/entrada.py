# backend/app/routers/entrada.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..db import models
import tempfile
import os
from datetime import datetime
from app.utils.pdf_extractor_melhorado import extrair_produtos_inteligente_entrada_melhorado
from app.utils.product_matcher import find_product_by_code_or_name

from ..crud import movimentacao_estoque as crud_movimentacao
from ..schemas import movimentacao_estoque as schemas_movimentacao
from ..schemas import produto as schemas_produto
from ..db.connection import get_db
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/entrada",
    tags=["Entrada de Estoque"],
    responses={404: {"description": "Não encontrado"}},
)

@router.post("/processar-pdf", response_model=dict)
async def processar_pdf_entrada(
    arquivo: UploadFile = File(..., description="Arquivo PDF da nota fiscal de entrada"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Processa um PDF de nota fiscal de ENTRADA e registra as movimentações automaticamente."""
    
    # Log para debug
    print(f"DEBUG: Arquivo de entrada recebido: {arquivo.filename if arquivo else 'None'}")
    print(f"DEBUG: Content type: {arquivo.content_type if arquivo else 'None'}")
    
    # Validar se o arquivo foi enviado
    if not arquivo or not arquivo.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum arquivo foi enviado"
        )
    
    if not arquivo.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos PDF são aceitos"
        )
    
    try:
        print(f"DEBUG: Iniciando processamento do arquivo de entrada {arquivo.filename}")
        
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await arquivo.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        print(f"DEBUG: Arquivo salvo temporariamente em: {temp_file_path}")
        
        # Extrair dados do PDF
        dados_pdf = extrair_dados_pdf_entrada(temp_file_path)
        print(f"DEBUG: Dados extraídos do PDF: {dados_pdf}")
        
        # Limpar arquivo temporário
        os.unlink(temp_file_path)
        
        if not dados_pdf.get('produtos'):
            return {
                "sucesso": True,
                "arquivo": arquivo.filename,
                "tipo": "ENTRADA",
                "nota_fiscal": dados_pdf.get('nota_fiscal'),
                "data_emissao": dados_pdf.get('data_emissao'),
                "fornecedor": dados_pdf.get('fornecedor'),
                "cnpj_fornecedor": dados_pdf.get('cnpj_fornecedor'),
                "movimentacoes_criadas": 0,
                "produtos_processados": [],
                "produtos_nao_encontrados": [],
                "total_produtos_pdf": 0
            }
        
        produtos_processados = []
        produtos_nao_encontrados = []
        movimentacoes_criadas = 0
        
        # Processar cada produto encontrado no PDF
        for produto_pdf in dados_pdf['produtos']:
            print(f"DEBUG: Processando produto: {produto_pdf}")
            
            codigo = produto_pdf.get('codigo')
            descricao = produto_pdf.get('descricao', '')
            
            # Buscar produto no sistema pelo código ou nome
            produto_sistema, metodo_busca, score = find_product_by_code_or_name(
                db, codigo, descricao, current_user.empresa_id
            )
            
            if produto_sistema and metodo_busca == 'nome':
                print(f"DEBUG: Produto encontrado por nome: {descricao} → {produto_sistema.nome} (score: {score:.2f})")
            
            if produto_sistema:
                try:
                    # Criar movimentação de entrada
                    movimentacao_data = schemas_movimentacao.MovimentacaoEstoqueCreate(
                        produto_id=produto_sistema.id,
                        tipo_movimentacao="ENTRADA",
                        quantidade=float(produto_pdf.get('quantidade', 0)),
                        observacao=f"Entrada automática - NF {dados_pdf.get('nota_fiscal', 'N/A')} - {arquivo.filename}"
                    )
                    
                    produto_atualizado = crud_movimentacao.create_movimentacao_estoque(
                        db=db,
                        movimentacao=movimentacao_data,
                        usuario_id=current_user.id,
                        empresa_id=current_user.empresa_id
                    )
                    
                    produtos_processados.append({
                        "codigo": produto_pdf.get('codigo'),
                        "nome": produto_sistema.nome,
                        "quantidade_entrada": produto_pdf.get('quantidade'),
                        "estoque_anterior": produto_sistema.estoque_atual,
                        "estoque_atual": produto_atualizado.estoque_atual
                    })
                    
                    movimentacoes_criadas += 1
                    print(f"DEBUG: Movimentação criada para produto {produto_sistema.nome}")
                    
                except Exception as e:
                    print(f"DEBUG: Erro ao criar movimentação para produto {produto_sistema.nome}: {e}")
                    produtos_nao_encontrados.append({
                        "codigo": produto_pdf.get('codigo'),
                        "descricao": produto_pdf.get('descricao', 'N/A'),
                        "quantidade": produto_pdf.get('quantidade'),
                        "erro": f"Erro ao processar: {str(e)}"
                    })
            else:
                print(f"DEBUG: Produto não encontrado no sistema: {produto_pdf.get('codigo')}")
                produtos_nao_encontrados.append({
                    "codigo": produto_pdf.get('codigo'),
                    "descricao": produto_pdf.get('descricao', 'N/A'),
                    "quantidade": produto_pdf.get('quantidade'),
                    "erro": "Produto não cadastrado no sistema"
                })
        
        return {
            "sucesso": True,
            "arquivo": arquivo.filename,
            "tipo": "ENTRADA",
            "nota_fiscal": dados_pdf.get('nota_fiscal'),
            "data_emissao": dados_pdf.get('data_emissao'),
            "fornecedor": dados_pdf.get('fornecedor'),
            "cnpj_fornecedor": dados_pdf.get('cnpj_fornecedor'),
            "movimentacoes_criadas": movimentacoes_criadas,
            "produtos_processados": produtos_processados,
            "produtos_nao_encontrados": produtos_nao_encontrados,
            "total_produtos_pdf": len(dados_pdf['produtos'])
        }
        
    except Exception as e:
        print(f"DEBUG: Erro geral no processamento: {e}")
        # Limpar arquivo temporário em caso de erro
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar PDF de entrada: {str(e)}"
        )


def extrair_dados_pdf_entrada(caminho_pdf: str) -> Dict[str, Any]:
    """Extrai dados específicos de PDFs de entrada (notas fiscais de compra)."""
    try:
        dados = extrair_produtos_inteligente_entrada_melhorado(caminho_pdf)
        return dados
    except Exception as e:
        print(f"Erro ao extrair dados do PDF de entrada: {e}")
        return {
            'produtos': [],
            'nota_fiscal': None,
            'data_emissao': None,
            'fornecedor': None,
            'cnpj_fornecedor': None
        }