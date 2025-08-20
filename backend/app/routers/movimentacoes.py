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
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await arquivo.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Extrair dados do PDF
        dados_extraidos = extrair_dados_pdf(temp_file_path)
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar PDF: {str(e)}"
        )

def extrair_dados_pdf(caminho_pdf: str) -> Dict[str, Any]:
    """Extrai dados estruturados de um PDF de nota fiscal."""
    
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
        
        # Extrair número da nota fiscal
        nf_match = re.search(r'(?:NOTA FISCAL|NF|N°)\s*:?\s*(\d+)', texto_completo, re.IGNORECASE)
        if nf_match:
            dados['nota_fiscal'] = nf_match.group(1).zfill(10)
        
        # Extrair data de emissão
        data_match = re.search(r'(?:Data de Emissão|Emissão)\s*:?\s*(\d{2}/\d{2}/\d{4})', texto_completo, re.IGNORECASE)
        if data_match:
            dados['data_emissao'] = data_match.group(1)
        
        # Extrair cliente
        cliente_match = re.search(r'(?:Cliente|Razão Social)\s*:?\s*([A-Z][A-Z\s&.-]+)', texto_completo, re.IGNORECASE)
        if cliente_match:
            dados['cliente'] = cliente_match.group(1).strip()
        
        # Extrair CNPJ
        cnpj_match = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', texto_completo)
        if cnpj_match:
            dados['cnpj_cliente'] = cnpj_match.group(1)
        
        # Extrair produtos usando padrões mais robustos
        linhas = texto_completo.split('\n')
        produtos = []
        
        for i, linha in enumerate(linhas):
            # Procurar por padrões de produtos
            produto_match = re.match(r'(\d+)\s+(\d+)\s+(.+?)\s+(\d{8})\s+(\w+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)', linha)
            
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
                    
                    produtos.append({
                        'item': item,
                        'codigo': codigo,
                        'descricao': descricao,
                        'ncm': ncm,
                        'unidade': unidade,
                        'quantidade': quantidade,
                        'valor_unitario': valor_unitario,
                        'valor_total': valor_total
                    })
                except (ValueError, IndexError):
                    continue
        
        dados['produtos'] = produtos
        
    except Exception as e:
        print(f"Erro ao extrair dados do PDF: {e}")
    
    return dados