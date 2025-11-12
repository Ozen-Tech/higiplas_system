# backend/app/routers/saida.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..db import models
import tempfile
import os
from datetime import datetime
from app.utils.product_matcher import find_product_by_code_or_name

from ..crud import movimentacao_estoque as crud_movimentacao
from ..schemas import movimentacao_estoque as schemas_movimentacao
from ..schemas import produto as schemas_produto
from ..db.connection import get_db
from app.dependencies import get_current_user
from app.core.logger import api_logger as logger

router = APIRouter(
    prefix="/saida",
    tags=["Saída de Estoque"],
    responses={404: {"description": "Não encontrado"}},
)

@router.post(
    "/processar-pdf",
    response_model=Dict[str, Any],
    summary="Processa PDF de nota fiscal de saída",
    description="Extrai dados de um PDF de nota fiscal de saída e registra as movimentações de estoque automaticamente."
)
async def processar_pdf_saida(
    arquivo: UploadFile = File(..., description="Arquivo PDF da nota fiscal de saída"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Processa um PDF de nota fiscal de SAÍDA e registra as movimentações automaticamente."""
    
    # Log para debug
    logger.debug(f"Arquivo de saída recebido: {arquivo.filename if arquivo else 'None'}, content_type: {arquivo.content_type if arquivo else 'None'}")
    
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
        logger.info(f"Iniciando processamento do arquivo de saída {arquivo.filename}")
        
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await arquivo.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        logger.debug(f"Arquivo salvo temporariamente em: {temp_file_path}")
        
        # Extrair dados do PDF
        dados_pdf = extrair_dados_pdf_saida(temp_file_path)
        logger.debug(f"Dados extraídos do PDF: {len(dados_pdf.get('produtos', []))} produtos encontrados")
        
        # Limpar arquivo temporário
        os.unlink(temp_file_path)
        
        if not dados_pdf.get('produtos'):
            return {
                "sucesso": True,
                "arquivo": arquivo.filename,
                "tipo": "SAÍDA",
                "nota_fiscal": dados_pdf.get('nota_fiscal'),
                "data_emissao": dados_pdf.get('data_emissao'),
                "cliente": dados_pdf.get('cliente'),
                "cnpj_cliente": dados_pdf.get('cnpj_cliente'),
                "movimentacoes_criadas": 0,
                "produtos_processados": [],
                "produtos_nao_encontrados": [],
                "produtos_sem_estoque": [],
                "total_produtos_pdf": 0
            }
        
        produtos_processados = []
        produtos_nao_encontrados = []
        produtos_sem_estoque = []
        movimentacoes_criadas = 0
        
        # Processar cada produto encontrado no PDF
        for produto_pdf in dados_pdf['produtos']:
            logger.debug(f"Processando produto: {produto_pdf}")
            
            codigo = produto_pdf.get('codigo')
            descricao = produto_pdf.get('descricao', '')
            
            # Buscar produto no sistema pelo código ou nome
            produto_sistema, metodo_busca, score = find_product_by_code_or_name(
                db, codigo, descricao, current_user.empresa_id
            )
            
            if produto_sistema and metodo_busca == 'nome':
                logger.debug(f"Produto encontrado por nome: {descricao} → {produto_sistema.nome} (score: {score:.2f})")
            
            if produto_sistema:
                quantidade_saida = float(produto_pdf.get('quantidade', 0))
                
                # Verificar se há estoque suficiente
                if produto_sistema.estoque_atual < quantidade_saida:
                    produtos_sem_estoque.append({
                        "codigo": produto_pdf.get('codigo'),
                        "nome": produto_sistema.nome,
                        "quantidade_solicitada": quantidade_saida,
                        "estoque_disponivel": produto_sistema.estoque_atual,
                        "erro": "Estoque insuficiente"
                    })
                    continue
                
                try:
                    # Criar movimentação de saída
                    movimentacao_data = schemas_movimentacao.MovimentacaoEstoqueCreate(
                        produto_id=produto_sistema.id,
                        tipo_movimentacao="SAIDA",
                        quantidade=quantidade_saida,
                        observacao=f"Saída automática - NF {dados_pdf.get('nota_fiscal', 'N/A')} - {arquivo.filename}"
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
                        "quantidade_saida": quantidade_saida,
                        "estoque_anterior": produto_sistema.estoque_atual,
                        "estoque_atual": produto_atualizado.estoque_atual
                    })
                    
                    movimentacoes_criadas += 1
                    logger.debug(f"Movimentação de saída criada para produto {produto_sistema.nome}")
                    
                except Exception as e:
                    logger.error(f"Erro ao criar movimentação para produto {produto_sistema.nome}: {e}", exc_info=True)
                    produtos_nao_encontrados.append({
                        "codigo": produto_pdf.get('codigo'),
                        "descricao": produto_pdf.get('descricao', 'N/A'),
                        "quantidade": produto_pdf.get('quantidade'),
                        "erro": f"Erro ao processar: {str(e)}"
                    })
            else:
                logger.warning(f"Produto não encontrado no sistema: {produto_pdf.get('codigo')}")
                produtos_nao_encontrados.append({
                    "codigo": produto_pdf.get('codigo'),
                    "descricao": produto_pdf.get('descricao', 'N/A'),
                    "quantidade": produto_pdf.get('quantidade'),
                    "erro": "Produto não cadastrado no sistema"
                })
        
        return {
            "sucesso": True,
            "arquivo": arquivo.filename,
            "tipo": "SAÍDA",
            "nota_fiscal": dados_pdf.get('nota_fiscal'),
            "data_emissao": dados_pdf.get('data_emissao'),
            "cliente": dados_pdf.get('cliente'),
            "cnpj_cliente": dados_pdf.get('cnpj_cliente'),
            "movimentacoes_criadas": movimentacoes_criadas,
            "produtos_processados": produtos_processados,
            "produtos_nao_encontrados": produtos_nao_encontrados,
            "produtos_sem_estoque": produtos_sem_estoque,
            "total_produtos_pdf": len(dados_pdf['produtos'])
        }
        
    except Exception as e:
        logger.error(f"Erro geral no processamento: {e}", exc_info=True)
        # Limpar arquivo temporário em caso de erro
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar PDF de saída: {str(e)}"
        )


def extrair_dados_pdf_saida(caminho_pdf: str) -> Dict[str, Any]:
    """Usa a versão antiga e funcional: delega para app.routers.movimentacoes.extrair_dados_pdf."""
    try:
        from app.routers.movimentacoes import extrair_dados_pdf
        return extrair_dados_pdf(caminho_pdf)
    except Exception as e:
        logger.error(f"Erro ao delegar extração de SAÍDA: {e}", exc_info=True)
        return {
            'nota_fiscal': None,
            'data_emissao': None,
            'cliente': None,
            'cnpj_cliente': None,
            'valor_total': None,
            'produtos': []
        }