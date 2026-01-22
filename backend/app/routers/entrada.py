# backend/app/routers/entrada.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..db import models
import tempfile
import os
from datetime import datetime
# Removido: from app.utils.pdf_extractor_melhorado import extrair_produtos_inteligente_entrada_melhorado
from app.utils.product_matcher import find_product_by_code_or_name
from app.services.nf_xml_processor_service import NFXMLProcessorService

from ..crud import movimentacao_estoque as crud_movimentacao
from ..schemas import movimentacao_estoque as schemas_movimentacao
from ..schemas import produto as schemas_produto
from ..db.connection import get_db
from app.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

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
        
        # Extrair dados do PDF (delegando para versão antiga e funcional)
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
    """Usa a versão antiga e funcional: delega para app.routers.movimentacoes.extrair_dados_pdf_entrada."""
    try:
        from app.routers.movimentacoes import extrair_dados_pdf_entrada as extrair_dados_pdf_entrada_mov
        return extrair_dados_pdf_entrada_mov(caminho_pdf)
    except Exception as e:
        print(f"DEBUG: Erro ao delegar extração de ENTRADA: {e}")
        return {
            'produtos': [],
            'nota_fiscal': None,
            'data_emissao': None,
            'fornecedor': None,
            'cnpj_fornecedor': None
        }


@router.post("/processar-xml", response_model=dict)
async def processar_xml_entrada(
    arquivo: UploadFile = File(..., description="Arquivo XML da nota fiscal de entrada"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Processa um XML de nota fiscal de ENTRADA (NF-e) e extrai todos os dados dos produtos.
    Retorna preview dos produtos para confirmação antes de registrar as movimentações.
    """
    
    logger.info(f"Arquivo XML recebido: {arquivo.filename if arquivo else 'None'}")
    logger.info(f"Content type: {arquivo.content_type if arquivo else 'None'}")
    
    # Validar se o arquivo foi enviado
    if not arquivo or not arquivo.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum arquivo foi enviado"
        )
    
    if not arquivo.filename.lower().endswith('.xml'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos XML são aceitos"
        )
    
    temp_file_path = None
    try:
        logger.info(f"Iniciando processamento do arquivo XML de entrada: {arquivo.filename}")
        
        # Salvar arquivo temporariamente e validar conteúdo
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as temp_file:
            content = await arquivo.read()
            
            # Validar se o conteúdo é realmente um XML
            if not content or len(content) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="O arquivo enviado está vazio"
                )
            
            # Verificar se o conteúdo começa com XML válido
            content_str = content.decode('utf-8', errors='ignore')[:200]  # Primeiros 200 caracteres
            if not ('<?xml' in content_str or '<nfeProc' in content_str or '<NFe' in content_str):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="O arquivo não é um XML de NF-e válido. Certifique-se de enviar apenas arquivos XML de Nota Fiscal Eletrônica (NF-e)."
                )
            
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        logger.info(f"Arquivo XML salvo temporariamente em: {temp_file_path}")
        
        # Processar XML usando o serviço
        xml_processor = NFXMLProcessorService(db)
        dados_nf = xml_processor.processar_nf_xml(
            caminho_xml=temp_file_path,
            tipo_movimentacao="ENTRADA",
            empresa_id_override=current_user.empresa_id
        )
        
        logger.info(f"XML processado com sucesso. Total de produtos: {dados_nf.get('total_produtos', 0)}")
        
        # Limpar arquivo temporário
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            temp_file_path = None
        
        # Formatar resposta compatível com o formato esperado pelo frontend
        produtos_encontrados = dados_nf.get('produtos_encontrados', [])
        produtos_nao_encontrados = dados_nf.get('produtos_nao_encontrados', [])
        
        # Transformar produtos para formato compatível com o preview do frontend
        produtos_formatados = []
        for prod in produtos_encontrados:
            produtos_formatados.append({
                "codigo": prod.get('codigo'),
                "descricao_pdf": prod.get('descricao'),
                "quantidade": prod.get('quantidade'),
                "valor_unitario": prod.get('valor_unitario'),
                "valor_total": prod.get('valor_total'),
                "encontrado": prod.get('encontrado', True),
                "produto_id": prod.get('produto_id'),
                "nome_sistema": prod.get('nome_sistema'),
                "codigo_sistema": prod.get('codigo'),
                "estoque_atual": prod.get('estoque_atual'),
                "estoque_projetado": prod.get('estoque_projetado')
            })
        
        for prod in produtos_nao_encontrados:
            produtos_formatados.append({
                "codigo": prod.get('codigo'),
                "descricao_pdf": prod.get('descricao'),
                "quantidade": prod.get('quantidade'),
                "valor_unitario": prod.get('valor_unitario'),
                "valor_total": prod.get('valor_total'),
                "encontrado": False,
                "produto_id": None,
                "nome_sistema": None,
                "codigo_sistema": None,
                "estoque_atual": None,
                "estoque_projetado": None
            })
        
        return {
            "sucesso": True,
            "arquivo": arquivo.filename,
            "tipo": "ENTRADA",
            "tipo_movimentacao": dados_nf.get('tipo_movimentacao', 'ENTRADA'),
            "empresa_id": dados_nf.get('empresa_id'),
            "nota_fiscal": dados_nf.get('nota_fiscal'),
            "chave_acesso": dados_nf.get('chave_acesso'),
            "data_emissao": dados_nf.get('data_emissao'),
            "fornecedor": dados_nf.get('nome_emitente'),
            "cnpj_fornecedor": dados_nf.get('cnpj_emitente'),
            "valor_total": dados_nf.get('valor_total'),
            "total_produtos_pdf": dados_nf.get('total_produtos', 0),
            "produtos_validos": len(produtos_encontrados),
            "produtos_encontrados": produtos_encontrados,
            "produtos_nao_encontrados": produtos_nao_encontrados,
            "produtos": produtos_formatados
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar XML de entrada: {str(e)}", exc_info=True)
        
        # Limpar arquivo temporário em caso de erro
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar XML de entrada: {str(e)}"
        )


@router.post("/confirmar-xml", response_model=dict)
async def confirmar_entrada_xml(
    nota_fiscal: str,
    produtos_confirmados: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Confirma a entrada de produtos processados do XML e cria as movimentações de estoque.
    
    Args:
        nota_fiscal: Número da nota fiscal
        produtos_confirmados: Lista de produtos com produto_id e quantidade a serem registrados
    """
    
    logger.info(f"Confirmando entrada da NF {nota_fiscal} com {len(produtos_confirmados)} produtos")
    
    try:
        movimentacoes_criadas = 0
        produtos_processados = []
        erros = []
        
        for produto_conf in produtos_confirmados:
            produto_id = produto_conf.get('produto_id')
            quantidade = produto_conf.get('quantidade', 0)
            
            if not produto_id or quantidade <= 0:
                continue
            
            try:
                # Buscar produto para pegar estoque atual
                produto_sistema = db.query(models.Produto).filter(
                    models.Produto.id == produto_id,
                    models.Produto.empresa_id == current_user.empresa_id
                ).first()
                
                if not produto_sistema:
                    erros.append({
                        "produto_id": produto_id,
                        "erro": "Produto não encontrado no sistema"
                    })
                    continue
                
                # Criar movimentação de entrada
                movimentacao_data = schemas_movimentacao.MovimentacaoEstoqueCreate(
                    produto_id=produto_id,
                    tipo_movimentacao="ENTRADA",
                    quantidade=float(quantidade),
                    observacao=f"Entrada XML - NF {nota_fiscal}"
                )
                
                produto_atualizado = crud_movimentacao.create_movimentacao_estoque(
                    db=db,
                    movimentacao=movimentacao_data,
                    usuario_id=current_user.id,
                    empresa_id=current_user.empresa_id
                )
                
                produtos_processados.append({
                    "produto_id": produto_id,
                    "nome": produto_sistema.nome,
                    "quantidade_entrada": quantidade,
                    "estoque_anterior": produto_sistema.quantidade_em_estoque,
                    "estoque_atual": produto_atualizado.quantidade_em_estoque
                })
                
                movimentacoes_criadas += 1
                logger.info(f"Movimentação criada: {produto_sistema.nome} +{quantidade}")
                
            except Exception as e:
                logger.error(f"Erro ao criar movimentação para produto {produto_id}: {e}")
                erros.append({
                    "produto_id": produto_id,
                    "erro": str(e)
                })
        
        return {
            "sucesso": True,
            "nota_fiscal": nota_fiscal,
            "movimentacoes_criadas": movimentacoes_criadas,
            "produtos_processados": produtos_processados,
            "erros": erros
        }
        
    except Exception as e:
        logger.error(f"Erro geral ao confirmar entrada XML: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao confirmar entrada: {str(e)}"
        )