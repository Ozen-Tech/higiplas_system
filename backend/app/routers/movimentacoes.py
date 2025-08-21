# backend/app/routers/movimentacoes.py

# Adicionamos 'Body' às importações do FastAPI
from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..db import models
import json
import os
import tempfile
import pdfplumber
import re
from datetime import datetime

from ..crud import movimentacao_estoque as crud_movimentacao
from ..schemas import movimentacao_estoque as schemas_movimentacao
from ..schemas import produto as schemas_produto
from ..schemas import usuario as schemas_usuario
from ..db.connection import get_db
from app.dependencies import get_current_user

router = APIRouter(
    #prefix="/movimentacoes",
    tags=["Movimentações de Estoque"],
    responses={404: {"description": "Não encontrado"}},
)

@router.post(
    "/",
    response_model=schemas_produto.Produto,
    summary="Cria uma nova movimentação de estoque",
    description="Registra uma ENTRADA ou SAIDA de um produto, atualizando seu estoque total. Retorna o produto com a quantidade atualizada."
)
def create_movimentacao(
    # --- AQUI ESTÁ A MÁGICA ---
    # Em vez de receber 'movimentacao' diretamente, usamos Body() para adicionar os exemplos.
    movimentacao: schemas_movimentacao.MovimentacaoEstoqueCreate = Body(
        examples={
            "Entrada de Estoque": {
                "summary": "Exemplo para adicionar produtos",
                "description": "Use este formato para registrar o recebimento de mercadorias.",
                "value": {
                    "produto_id": 1,
                    "tipo_movimentacao": "ENTRADA",
                    "quantidade": 50,
                    "observacao": "Recebimento do fornecedor XYZ - NF 12345"
                }
            },
            "Saída por Venda": {
                "summary": "Exemplo para remover produtos",
                "description": "Use este formato para registrar uma venda ou baixa de estoque.",
                "value": {
                    "produto_id": 1,
                    "tipo_movimentacao": "SAIDA",
                    "quantidade": 5,
                    "observacao": "Venda para o cliente João da Silva - Pedido #789"
                }
            }
        }
    ),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    try:
        produto_atualizado = crud_movimentacao.create_movimentacao_estoque(
            db=db, 
            movimentacao=movimentacao, 
            usuario_id=current_user.id,
            empresa_id=current_user.empresa_id
        )
        return produto_atualizado
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro interno: {e}")

@router.get(
    "/{produto_id}",
    response_model=List[schemas_movimentacao.MovimentacaoEstoqueResponse],
    summary="Lista o histórico de movimentações de um produto",
    description="Retorna todas as movimentações de estoque para um produto específico, ordenadas da mais recente para a mais antiga."
)
def read_movimentacoes_por_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return crud_movimentacao.get_movimentacoes_by_produto_id(
        db=db, 
        produto_id=produto_id, 
        empresa_id=current_user.empresa_id
    )

@router.post(
    "/preview-pdf",
    response_model=Dict[str, Any],
    summary="Visualiza dados extraídos do PDF",
    description="Extrai dados de um PDF de nota fiscal para visualização e confirmação antes do processamento."
)
async def preview_pdf_movimentacao(
    arquivo: UploadFile = File(..., description="Arquivo PDF da nota fiscal"),
    tipo_movimentacao: str = Form(..., description="Tipo de movimentação: ENTRADA ou SAIDA"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Extrai dados do PDF para visualização antes do processamento."""
    
    print(f"DEBUG: Arquivo recebido: {arquivo.filename}")
    print(f"DEBUG: Tipo de movimentação: {tipo_movimentacao}")
    print(f"DEBUG: Content type: {arquivo.content_type}")
    
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
    
    if tipo_movimentacao not in ['ENTRADA', 'SAIDA']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de movimentação deve ser ENTRADA ou SAIDA"
        )
    
    try:
        print(f"DEBUG: Iniciando preview do arquivo {arquivo.filename}")
        
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await arquivo.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        print(f"DEBUG: Arquivo salvo temporariamente em {temp_file_path}")
        
        # Extrair dados do PDF
        print(f"DEBUG: Iniciando extração de dados do PDF")
        dados_extraidos = extrair_dados_pdf(temp_file_path)
        print(f"DEBUG: Dados extraídos: {dados_extraidos}")
        
        # Limpar arquivo temporário
        os.unlink(temp_file_path)
        
        if not dados_extraidos or not dados_extraidos.get('produtos'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não foi possível extrair dados válidos do PDF"
            )
        
        # Enriquecer dados dos produtos com informações do banco
        produtos_enriquecidos = []
        produtos_nao_encontrados = []
        
        for produto_data in dados_extraidos['produtos']:
            codigo = produto_data.get('codigo')
            quantidade = produto_data.get('quantidade', 0)
            
            if not codigo or quantidade <= 0:
                continue
            
            # Buscar produto pelo código
            produto = db.query(models.Produto).filter(
                models.Produto.codigo == str(codigo),
                models.Produto.empresa_id == current_user.empresa_id
            ).first()
            
            produto_info = {
                'codigo': codigo,
                'descricao_pdf': produto_data.get('descricao', 'N/A'),
                'quantidade': quantidade,
                'valor_unitario': produto_data.get('valor_unitario', 0),
                'valor_total': produto_data.get('valor_total', 0),
                'encontrado': produto is not None
            }
            
            if produto:
                produto_info.update({
                    'produto_id': produto.id,
                    'nome_sistema': produto.nome,
                    'estoque_atual': produto.quantidade_estoque,
                    'estoque_projetado': produto.quantidade_estoque + (quantidade if tipo_movimentacao == 'ENTRADA' else -quantidade)
                })
                produtos_enriquecidos.append(produto_info)
            else:
                produtos_nao_encontrados.append(produto_info)
        
        return {
            'sucesso': True,
            'arquivo': arquivo.filename,
            'tipo_movimentacao': tipo_movimentacao,
            'nota_fiscal': dados_extraidos.get('nota_fiscal'),
            'data_emissao': dados_extraidos.get('data_emissao'),
            'cliente': dados_extraidos.get('cliente'),
            'produtos_encontrados': produtos_enriquecidos,
            'produtos_nao_encontrados': produtos_nao_encontrados,
            'total_produtos_pdf': len(dados_extraidos['produtos']),
            'produtos_validos': len(produtos_enriquecidos)
        }
        
    except HTTPException as he:
        print(f"DEBUG: HTTPException capturada: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        print(f"DEBUG: Exception geral capturada: {type(e).__name__} - {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar PDF: {str(e)}"
        )

@router.post(
    "/confirmar-movimentacoes",
    response_model=Dict[str, Any],
    summary="Confirma e processa movimentações de estoque",
    description="Processa as movimentações de estoque após confirmação do usuário."
)
async def confirmar_movimentacoes(
    dados: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Processa as movimentações após confirmação do usuário."""
    
    try:
        produtos_confirmados = dados.get('produtos_confirmados', [])
        tipo_movimentacao = dados.get('tipo_movimentacao')
        nota_fiscal = dados.get('nota_fiscal')
        
        if not produtos_confirmados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum produto foi confirmado para processamento"
            )
        
        movimentacoes_criadas = []
        produtos_atualizados = []
        
        for produto_data in produtos_confirmados:
            produto_id = produto_data.get('produto_id')
            quantidade = produto_data.get('quantidade', 0)
            
            if not produto_id or quantidade <= 0:
                continue
            
            # Buscar produto
            produto = db.query(models.Produto).filter(
                models.Produto.id == produto_id,
                models.Produto.empresa_id == current_user.empresa_id
            ).first()
            
            if not produto:
                continue
            
            # Calcular nova quantidade
            if tipo_movimentacao == 'ENTRADA':
                nova_quantidade = produto.quantidade_estoque + quantidade
            else:  # SAIDA
                nova_quantidade = produto.quantidade_estoque - quantidade
                if nova_quantidade < 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Estoque insuficiente para o produto {produto.nome}. Estoque atual: {produto.quantidade_estoque}, Quantidade solicitada: {quantidade}"
                    )
            
            # Criar movimentação
            movimentacao = models.MovimentacaoEstoque(
                produto_id=produto.id,
                tipo=tipo_movimentacao,
                quantidade=quantidade,
                quantidade_anterior=produto.quantidade_estoque,
                quantidade_nova=nova_quantidade,
                observacoes=f"Importação automática - NF: {nota_fiscal}",
                usuario_id=current_user.id,
                empresa_id=current_user.empresa_id
            )
            
            db.add(movimentacao)
            
            # Atualizar estoque do produto
            produto.quantidade_estoque = nova_quantidade
            
            movimentacoes_criadas.append({
                'produto_id': produto.id,
                'produto_nome': produto.nome,
                'tipo': tipo_movimentacao,
                'quantidade': quantidade,
                'estoque_anterior': movimentacao.quantidade_anterior,
                'estoque_novo': nova_quantidade
            })
            
            produtos_atualizados.append(produto.nome)
        
        db.commit()
        
        return {
            'sucesso': True,
            'mensagem': f'Processamento concluído com sucesso! {len(movimentacoes_criadas)} movimentações registradas.',
            'movimentacoes_criadas': len(movimentacoes_criadas),
            'produtos_atualizados': produtos_atualizados,
            'detalhes': movimentacoes_criadas
        }
        
    except HTTPException as he:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar movimentações: {str(e)}"
        )

@router.post(
    "/processar-pdf",
    response_model=Dict[str, Any],
    summary="Processa PDF de movimentação de estoque",
    description="Extrai dados de um PDF de nota fiscal e registra as movimentações de estoque automaticamente."
)
async def processar_pdf_movimentacao(
    arquivo: UploadFile = File(..., description="Arquivo PDF da nota fiscal"),
    tipo_movimentacao: str = Form(..., description="Tipo de movimentação: ENTRADA ou SAIDA"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Processa um PDF de nota fiscal e registra as movimentações automaticamente."""
    
    # Log para debug
    print(f"DEBUG: Arquivo recebido: {arquivo.filename if arquivo else 'None'}")
    print(f"DEBUG: Tipo movimentação: {tipo_movimentacao}")
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
    
    if tipo_movimentacao not in ['ENTRADA', 'SAIDA']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de movimentação deve ser ENTRADA ou SAIDA"
        )
    
    try:
        print(f"DEBUG: Iniciando processamento do arquivo {arquivo.filename}")
        
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await arquivo.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        print(f"DEBUG: Arquivo salvo temporariamente em {temp_file_path}")
        
        # Extrair dados do PDF
        print(f"DEBUG: Iniciando extração de dados do PDF")
        dados_extraidos = extrair_dados_pdf(temp_file_path)
        print(f"DEBUG: Dados extraídos: {dados_extraidos}")
        
        # Limpar arquivo temporário
        os.unlink(temp_file_path)
        
        if not dados_extraidos or not dados_extraidos.get('produtos'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não foi possível extrair dados válidos do PDF"
            )
        
        # Processar movimentações
        movimentacoes_criadas = []
        produtos_nao_encontrados = []
        
        for produto_data in dados_extraidos['produtos']:
            codigo = produto_data.get('codigo')
            quantidade = produto_data.get('quantidade', 0)
            
            if not codigo or quantidade <= 0:
                continue
            
            # Buscar produto pelo código
            produto = db.query(models.Produto).filter(
                models.Produto.codigo == str(codigo),
                models.Produto.empresa_id == current_user.empresa_id
            ).first()
            
            if not produto:
                produtos_nao_encontrados.append({
                    'codigo': codigo,
                    'descricao': produto_data.get('descricao', 'N/A')
                })
                continue
            
            # Criar movimentação
            observacao = f"Processamento automático - NF {dados_extraidos.get('nota_fiscal', 'N/A')} - {produto_data.get('descricao', '')}"
            
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
                    usuario_id=current_user.id,
                    empresa_id=current_user.empresa_id
                )
                
                movimentacoes_criadas.append({
                    'produto_id': produto.id,
                    'codigo': codigo,
                    'nome': produto.nome,
                    'quantidade': quantidade,
                    'estoque_anterior': produto_atualizado.quantidade_estoque - (quantidade if tipo_movimentacao == 'ENTRADA' else -quantidade),
                    'estoque_atual': produto_atualizado.quantidade_estoque
                })
            except Exception as e:
                produtos_nao_encontrados.append({
                    'codigo': codigo,
                    'descricao': produto_data.get('descricao', 'N/A'),
                    'erro': str(e)
                })
        
        return {
            'sucesso': True,
            'arquivo': arquivo.filename,
            'nota_fiscal': dados_extraidos.get('nota_fiscal'),
            'data_emissao': dados_extraidos.get('data_emissao'),
            'cliente': dados_extraidos.get('cliente'),
            'movimentacoes_criadas': len(movimentacoes_criadas),
            'produtos_processados': movimentacoes_criadas,
            'produtos_nao_encontrados': produtos_nao_encontrados,
            'total_produtos_pdf': len(dados_extraidos['produtos'])
        }
        
    except HTTPException as he:
        print(f"DEBUG: HTTPException capturada: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        print(f"DEBUG: Exception geral capturada: {type(e).__name__} - {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar PDF: {str(e)}"
        )

def extrair_dados_pdf(caminho_pdf: str) -> Dict[str, Any]:
    """Extrai dados estruturados de um PDF de nota fiscal."""
    
    print(f"DEBUG: Iniciando extração de dados do arquivo: {caminho_pdf}")
    
    dados = {
        'nota_fiscal': None,
        'data_emissao': None,
        'cliente': None,
        'cnpj_cliente': None,
        'valor_total': None,
        'produtos': []
    }
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_completo = ""
            for page in pdf.pages:
                texto_completo += page.extract_text() or ""
        
        print(f"DEBUG: Texto extraído ({len(texto_completo)} caracteres)")
        
        # Extrair número da nota fiscal - padrão: NFe Nº 0000004538
        nf_match = re.search(r'NFe\s+Nº\s+(\d+)', texto_completo, re.IGNORECASE)
        if nf_match:
            dados['nota_fiscal'] = nf_match.group(1)
            print(f"DEBUG: Nota fiscal encontrada: {dados['nota_fiscal']}")
        
        # Extrair data de emissão - padrão: Data de Emissão 19/08/2025
        data_match = re.search(r'Data de Emissão\s+(\d{2}/\d{2}/\d{4})', texto_completo, re.IGNORECASE)
        if data_match:
            dados['data_emissao'] = data_match.group(1)
            print(f"DEBUG: Data de emissão encontrada: {dados['data_emissao']}")
        
        # Extrair cliente - padrão: Nome/Razão Social J S GONDIM LINHARES FILHO
        cliente_match = re.search(r'Nome/Razão Social\s+([A-Z][A-Z\s&.-]+?)\s+\d{2}\.\d{3}\.\d{3}', texto_completo, re.IGNORECASE)
        if cliente_match:
            dados['cliente'] = cliente_match.group(1).strip()
            print(f"DEBUG: Cliente encontrado: {dados['cliente']}")
        
        # Extrair CNPJ - buscar todos os CNPJs e pegar o do destinatário
        cnpj_matches = re.findall(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', texto_completo)
        if cnpj_matches:
            # O segundo CNPJ geralmente é do destinatário
            dados['cnpj_cliente'] = cnpj_matches[1] if len(cnpj_matches) > 1 else cnpj_matches[0]
            print(f"DEBUG: CNPJ cliente encontrado: {dados['cnpj_cliente']}")
        
        # Extrair valor total - padrão: Valor Total da Nota Fiscal 1.571,12
        valor_match = re.search(r'Valor Total da Nota\s+Fiscal\s+([\d.,]+)', texto_completo, re.IGNORECASE)
        if valor_match:
            valor_str = valor_match.group(1).replace('.', '').replace(',', '.')
            dados['valor_total'] = float(valor_str)
            print(f"DEBUG: Valor total encontrado: {dados['valor_total']}")
        
        # Extrair produtos - padrão da tabela de produtos
        linhas = texto_completo.split('\n')
        produtos = []
        
        # Procurar pela seção "Dados dos Produtos"
        inicio_produtos = False
        for i, linha in enumerate(linhas):
            if 'Dados dos Produtos' in linha:
                inicio_produtos = True
                continue
            
            if inicio_produtos and 'Dados Adicionais' in linha:
                break
                
            if inicio_produtos:
                # Padrão: 1 297 SUPORTE LT S/ CABO C/ PINCA P/ FIBRA (NOBRE) 96039000 0102 5102 UN 1,0000 19,1400 0,00 19,14
                produto_match = re.match(r'^(\d+)\s+(\d+)\s+(.+?)\s+(\d{8})\s+\d{4}\s+\d{4}\s+(\w+)\s+([\d,]+)\s+([\d,]+)\s+[\d,]+\s+([\d,]+)', linha)
                
                if produto_match:
                    try:
                        item = int(produto_match.group(1))
                        codigo = produto_match.group(2)
                        descricao = produto_match.group(3).strip()
                        ncm = produto_match.group(4)
                        unidade = produto_match.group(5)
                        quantidade = float(produto_match.group(6).replace(',', '.'))
                        valor_unitario = float(produto_match.group(7).replace(',', '.'))
                        valor_total = float(produto_match.group(8).replace(',', '.'))
                        
                        produto = {
                            'item': item,
                            'codigo': codigo,
                            'descricao': descricao,
                            'ncm': ncm,
                            'unidade': unidade,
                            'quantidade': quantidade,
                            'valor_unitario': valor_unitario,
                            'valor_total': valor_total
                        }
                        
                        produtos.append(produto)
                        print(f"DEBUG: Produto encontrado: {codigo} - {descricao} - Qtd: {quantidade}")
                        
                    except (ValueError, IndexError) as e:
                        print(f"DEBUG: Erro ao processar linha de produto: {linha} - Erro: {e}")
                        continue
        
        dados['produtos'] = produtos
        print(f"DEBUG: Extração concluída. Produtos encontrados: {len(produtos)}")
        
    except Exception as e:
        print(f"DEBUG: Erro ao extrair dados do PDF: {type(e).__name__} - {str(e)}")
        import traceback
        print(f"DEBUG: Traceback na extração: {traceback.format_exc()}")
    
    print(f"DEBUG: Retornando dados: {dados}")
    return dados