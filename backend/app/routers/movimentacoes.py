# backend/app/routers/movimentacoes.py

# Adicionamos 'Body' às importações do FastAPI
from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
from ..db import models
import json
import os
import tempfile
import pdfplumber
import re
from datetime import datetime
from app.utils.pdf_extractor_melhorado import extrair_produtos_inteligente_entrada_melhorado

from ..crud import movimentacao_estoque as crud_movimentacao
from ..schemas import movimentacao_estoque as schemas_movimentacao
from ..schemas import produto as schemas_produto
from ..schemas import usuario as schemas_usuario
from ..db.connection import get_db
from app.dependencies import get_current_user, get_current_operador, get_admin_user
import logging
# Serviço de similaridade importado dinamicamente quando necessário

logger = logging.getLogger(__name__)

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
    "/historico-geral",
    response_model=Dict[str, Any],
    summary="Lista o histórico geral de movimentações",
    description="Retorna todas as movimentações de estoque da empresa, com filtros opcionais por tipo e termo de busca."
)
def read_historico_geral(
    tipo: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    try:
        # Buscar todas as movimentações da empresa
        query = db.query(models.MovimentacaoEstoque).join(
            models.Produto
        ).filter(
            models.Produto.empresa_id == current_user.empresa_id
        )
        
        # Aplicar filtro por tipo se fornecido
        if tipo and tipo != "TODOS":
            query = query.filter(models.MovimentacaoEstoque.tipo_movimentacao == tipo)
        
        # Aplicar filtro de busca se fornecido
        if search:
            query = query.filter(
                models.Produto.nome.ilike(f"%{search}%") |
                models.MovimentacaoEstoque.observacao.ilike(f"%{search}%")
            )
        
        # Ordenar por data mais recente
        movimentacoes = query.order_by(models.MovimentacaoEstoque.data_movimentacao.desc()).all()
        
        # Calcular estatísticas
        total_entradas = sum(m.quantidade for m in movimentacoes if m.tipo_movimentacao == "ENTRADA")
        total_saidas = sum(m.quantidade for m in movimentacoes if m.tipo_movimentacao == "SAIDA")
        
        # Formatar resposta
        movimentacoes_formatadas = []
        for mov in movimentacoes:
            produto = db.query(models.Produto).filter(models.Produto.id == mov.produto_id).first()
            usuario = db.query(models.Usuario).filter(models.Usuario.id == mov.usuario_id).first()
            
            movimentacoes_formatadas.append({
                "id": mov.id,
                "produto_id": mov.produto_id,
                "produto_nome": produto.nome if produto else "Produto não encontrado",
                "produto_codigo": produto.codigo if produto else "",
                "tipo_movimentacao": mov.tipo_movimentacao,
                "quantidade": mov.quantidade,
                "quantidade_antes": mov.quantidade_antes,
                "quantidade_depois": mov.quantidade_depois,
                "origem": mov.origem,
                "estoque_atual": produto.quantidade_em_estoque if produto else 0,
                "data_movimentacao": mov.data_movimentacao.isoformat(),
                "observacao": mov.observacao,
                "usuario_nome": usuario.nome if usuario else "Usuário não encontrado"
            })
        
        return {
            "movimentacoes": movimentacoes_formatadas,
            "estatisticas": {
                "total_movimentacoes": len(movimentacoes),
                "total_entradas": total_entradas,
                "total_saidas": total_saidas,
                "saldo_liquido": total_entradas - total_saidas
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar histórico geral: {str(e)}"
        )

@router.get(
    "/buscar-produtos-similares",
    response_model=List[Dict[str, Any]],
    summary="Busca produtos similares por termo de pesquisa",
    description="Busca produtos similares no sistema baseado em um termo de pesquisa. Útil para associar produtos da NF com produtos do sistema."
)
async def buscar_produtos_similares(
    termo: str,
    empresa_id: int = None,
    limit: int = 20,
    min_similarity: int = 20,  # Reduzido de 30 para 20 para encontrar mais resultados
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Busca produtos similares por termo de pesquisa"""
    
    if not termo or len(termo.strip()) < 2:
        return []
    
    # Usar empresa_id do usuário se não fornecido
    if empresa_id is None:
        empresa_id = current_user.empresa_id
    
    # Inicializar serviço de similaridade
    from ..services.product_similarity import product_similarity_service
    similarity_service = product_similarity_service
    
    # Buscar produtos similares com threshold mais baixo para buscas manuais
    produtos_similares = similarity_service.find_similar_products(
        search_name=termo.strip(),
        db=db,
        empresa_id=empresa_id,
        limit=limit,
        min_similarity=min_similarity
    )
    
    # Mapear incluindo estoque_atual
    similares_mapeados = []
    for p in produtos_similares:
        prod_db = db.query(models.Produto).filter(
            models.Produto.id == p['id'],
            models.Produto.empresa_id == empresa_id
        ).first()
        similares_mapeados.append({
            'produto_id': p['id'],
            'nome': p['nome'],
            'codigo': p['codigo'],
            'estoque_atual': getattr(prod_db, 'quantidade_em_estoque', 0) if prod_db else 0,
            'score_similaridade': p['similarity_score'],
            'categoria': p.get('categoria', ''),
            'unidade_medida': p.get('unidade_medida', ''),
            'preco_venda': p.get('preco_venda', 0)
        })
    
    return similares_mapeados

@router.post(
    "/preview-pdf",
    response_model=Dict[str, Any],
    summary="Visualiza dados extraídos do PDF",
    description="Extrai dados de um PDF de nota fiscal para visualização e confirmação antes do processamento. Identifica empresa, reconhece/cria cliente automaticamente."
)
async def preview_pdf_movimentacao(
    arquivo: UploadFile = File(..., description="Arquivo PDF da nota fiscal"),
    tipo_movimentacao: str = Form(..., description="Tipo de movimentação: ENTRADA ou SAIDA"),
    vendedor_id: Optional[int] = Form(None, description="ID do vendedor (opcional, para NF de saída)"),
    orcamento_id: Optional[int] = Form(None, description="ID do orçamento relacionado (opcional)"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Extrai dados do PDF para visualização antes do processamento usando o novo serviço integrado."""
    
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
        
        # Usar novo serviço de processamento de NF
        from ..services.nf_processor_service import NFProcessorService
        nf_service = NFProcessorService(db)
        
        # Processar NF usando o serviço integrado
        resultado = nf_service.processar_nf_pdf(
            caminho_pdf=temp_file_path,
            tipo_movimentacao=tipo_movimentacao,
            vendedor_id=vendedor_id,
            orcamento_id=orcamento_id,
            usuario_id=current_user.id,
            empresa_id_override=None,  # Deixar o serviço identificar automaticamente
            nome_arquivo_original=arquivo.filename  # Passar nome original para detecção
        )
        
        # Limpar arquivo temporário
        os.unlink(temp_file_path)
        
        # Buscar lista de vendedores para seleção (se NF de saída)
        vendedores_disponiveis = []
        if tipo_movimentacao == 'SAIDA':
            vendedores = db.query(models.Usuario).filter(
                models.Usuario.empresa_id == resultado['empresa_id'],
                models.Usuario.perfil.ilike('%VENDEDOR%'),
                models.Usuario.is_active == True
            ).all()
            vendedores_disponiveis = [
                {
                    'id': v.id,
                    'nome': v.nome,
                    'email': v.email
                }
                for v in vendedores
            ]
        
        # Buscar lista de orçamentos recentes do cliente (se cliente identificado)
        orcamentos_disponiveis = []
        if tipo_movimentacao == 'SAIDA' and resultado.get('cliente_id'):
            orcamentos = db.query(models.Orcamento).filter(
                models.Orcamento.cliente_id == resultado['cliente_id'],
                models.Orcamento.status.in_(['RASCUNHO', 'ENVIADO', 'APROVADO'])
            ).order_by(models.Orcamento.data_criacao.desc()).limit(10).all()
            orcamentos_disponiveis = [
                {
                    'id': o.id,
                    'numero': f"#{o.id}",
                    'data_criacao': o.data_criacao.isoformat() if o.data_criacao else None,
                    'status': o.status
                }
                for o in orcamentos
            ]
        
        # Formatar resposta
        return {
            'sucesso': True,
            'arquivo': arquivo.filename,
            'tipo_movimentacao': resultado['tipo_movimentacao'],
            'empresa_id': resultado['empresa_id'],
            'nota_fiscal': resultado.get('nota_fiscal'),
            'data_emissao': resultado.get('data_emissao'),
            'cliente_id': resultado.get('cliente_id'),
            'cliente': resultado.get('cliente'),
            'cnpj_cliente': resultado.get('cnpj_cliente'),
            'vendedor_id': resultado.get('vendedor_id'),
            'orcamento_id': resultado.get('orcamento_id'),
            'is_delta_plastico': resultado.get('is_delta_plastico', False),
            'valor_total': resultado.get('valor_total'),
            'produtos_encontrados': resultado['produtos_encontrados'],
            'produtos_nao_encontrados': resultado['produtos_nao_encontrados'],
            'produtos': resultado['produtos'],
            'total_produtos_pdf': resultado['total_produtos'],
            'produtos_validos': len(resultado['produtos_encontrados']),
            'vendedores_disponiveis': vendedores_disponiveis,
            'orcamentos_disponiveis': orcamentos_disponiveis
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
    "/associar-produto-similar",
    response_model=Dict[str, Any],
    summary="Associa um produto similar do sistema a um produto do PDF",
    description="Permite associar um produto existente no sistema a um produto não encontrado do PDF."
)
async def associar_produto_similar(
    dados: Dict[str, Any] = Body(..., example={
        "codigo_pdf": "297",
        "produto_id_sistema": 15,
        "quantidade": 1.0,
        "tipo_movimentacao": "ENTRADA"
    }),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Associa um produto do sistema a um produto do PDF para processamento posterior."""
    
    try:
        codigo_pdf = dados.get('codigo_pdf')
        produto_id_sistema = dados.get('produto_id_sistema')
        quantidade = dados.get('quantidade', 0)
        tipo_movimentacao = dados.get('tipo_movimentacao')
        
        if not all([codigo_pdf, produto_id_sistema, quantidade, tipo_movimentacao]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Todos os campos são obrigatórios: codigo_pdf, produto_id_sistema, quantidade, tipo_movimentacao"
            )
        
        # Verificar se o produto existe
        produto = db.query(models.Produto).filter(
            models.Produto.id == produto_id_sistema,
            models.Produto.empresa_id == current_user.empresa_id
        ).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        # Verificar se há estoque suficiente para saída
        if tipo_movimentacao == 'SAIDA' and produto.quantidade_em_estoque < quantidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente para o produto {produto.nome}. Estoque atual: {produto.quantidade_em_estoque}, Quantidade solicitada: {quantidade}"
            )
        
        # Calcular estoque após movimentação (apenas para visualização)
        if tipo_movimentacao == 'ENTRADA':
            estoque_apos_movimentacao = produto.quantidade_em_estoque + quantidade
        else:  # SAIDA
            estoque_apos_movimentacao = produto.quantidade_em_estoque - quantidade
        
        # Retornar apenas a associação, SEM criar a movimentação
        return {
            'sucesso': True,
            'mensagem': f'Produto {produto.nome} associado com sucesso. Confirme para processar a movimentação.',
            'produto': {
                'id': produto.id,
                'nome': produto.nome,
                'codigo': produto.codigo,
                'estoque_atual': produto.quantidade_em_estoque,
                'estoque_apos_movimentacao': estoque_apos_movimentacao,
                'quantidade_movimentada': quantidade,
                'tipo_movimentacao': tipo_movimentacao,
                'codigo_pdf': codigo_pdf
            }
        }
        
    except HTTPException as he:
        raise
    except Exception as e:
        print(f"DEBUG: Erro ao associar produto similar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao associar produto: {str(e)}"
        )

@router.post(
    "/confirmar-movimentacoes",
    response_model=Dict[str, Any],
    summary="Confirma e processa movimentações de estoque",
    description="Processa as movimentações de estoque após confirmação do usuário. Usa o novo serviço integrado de processamento de NF."
)
async def confirmar_movimentacoes(
    dados: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Processa as movimentações após confirmação do usuário usando o novo serviço integrado."""
    
    try:
        # Validar dados obrigatórios
        produtos_confirmados = dados.get('produtos_confirmados', [])
        tipo_movimentacao = dados.get('tipo_movimentacao')
        nota_fiscal = dados.get('nota_fiscal')
        arquivo = dados.get('arquivo')  # Nome do arquivo original
        empresa_id = dados.get('empresa_id', current_user.empresa_id)
        
        if not produtos_confirmados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum produto foi confirmado para processamento"
            )
        
        # 🛡️ PROTEÇÃO CONTRA DUPLICATAS - Verificar se esta NF já foi processada
        if nota_fiscal and arquivo:
            # Verificar se há movimentações recentes (últimos 30 minutos) com a mesma NF
            from datetime import timedelta
            limite_tempo = datetime.now() - timedelta(minutes=30)
            
            # Buscar movimentações recentes que mencionam esta NF na observação
            movimentacoes_recentes = db.query(models.MovimentacaoEstoque).join(
                models.Produto
            ).filter(
                models.Produto.empresa_id == empresa_id,
                models.MovimentacaoEstoque.tipo_movimentacao == tipo_movimentacao,
                models.MovimentacaoEstoque.observacao.like(f'%NF {nota_fiscal}%'),
                models.MovimentacaoEstoque.data_movimentacao >= limite_tempo
            ).all()
            
            if movimentacoes_recentes and len(movimentacoes_recentes) >= len(produtos_confirmados):
                ultima_mov = movimentacoes_recentes[0]
                logger.warning(f"⚠️ Tentativa de processar NF duplicada: {nota_fiscal} (já processada em {ultima_mov.data_movimentacao})")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"⚠️ DUPLICATA DETECTADA! A Nota Fiscal {nota_fiscal} já foi processada recentemente em {ultima_mov.data_movimentacao.strftime('%d/%m/%Y às %H:%M')}. Para evitar duplicatas no estoque, não é possível processar novamente."
                )
        
        logger.info(f"✅ Processando NF {nota_fiscal} - {len(produtos_confirmados)} produtos - Tipo: {tipo_movimentacao}")
        
        # Preparar dados para o novo serviço
        dados_confirmacao = {
            'nota_fiscal': nota_fiscal,
            'tipo_movimentacao': tipo_movimentacao,
            'empresa_id': empresa_id,
            'cliente_id': dados.get('cliente_id'),
            'vendedor_id': dados.get('vendedor_id'),
            'orcamento_id': dados.get('orcamento_id'),
            'produtos_confirmados': produtos_confirmados
        }
        
        # Usar novo serviço de processamento
        from ..services.nf_processor_service import NFProcessorService
        nf_service = NFProcessorService(db)
        
        resultado = nf_service.confirmar_processamento(
            dados_confirmacao=dados_confirmacao,
            usuario_id=current_user.id
        )
        
        # Processar códigos sincronizados se houver (mantendo compatibilidade)
        codigos_sincronizados = []
        for produto_data in produtos_confirmados:
            codigo_nf = (produto_data.get('codigo_nf') or "").strip()
            produto_id = produto_data.get('produto_id')
            
            if codigo_nf and produto_id:
                produto = db.query(models.Produto).filter(
                    models.Produto.id == produto_id,
                    models.Produto.empresa_id == empresa_id
                ).first()
                
                if produto and produto.codigo == codigo_nf:
                    codigos_sincronizados.append({
                        'produto_id': produto.id,
                        'produto_nome': produto.nome,
                        'codigo_novo': produto.codigo
                    })
        
        return {
            'sucesso': True,
            'mensagem': f'Processamento concluído com sucesso! {resultado["movimentacoes_criadas"]} movimentações registradas.',
            'movimentacoes_criadas': resultado['movimentacoes_criadas'],
            'historicos_vendas': resultado.get('historicos_vendas', 0),
            'detalhes': resultado['detalhes'],
            'codigos_sincronizados': codigos_sincronizados
        }
        
        movimentacoes_criadas = []
        produtos_atualizados = []
        codigos_sincronizados = []
        
        for produto_data in produtos_confirmados:
            produto_id = produto_data.get('produto_id')
            quantidade = produto_data.get('quantidade', 0)
            codigo_nf = (produto_data.get('codigo_nf') or "").strip()
            descricao_nf = produto_data.get('descricao_nf')
            
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
            estoque_atual = produto.quantidade_em_estoque or 0
            quantidade_antes = estoque_atual
            if tipo_movimentacao == 'ENTRADA':
                nova_quantidade = estoque_atual + quantidade
            else:  # SAIDA
                nova_quantidade = estoque_atual - quantidade
                if nova_quantidade < 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Estoque insuficiente para o produto {produto.nome}. Estoque atual: {estoque_atual}, Quantidade solicitada: {quantidade}"
                    )

            codigo_atualizado = False
            codigo_anterior = produto.codigo
            if codigo_nf:
                codigo_normalizado = codigo_nf.strip()
                codigo_conflict = db.query(models.Produto).filter(
                    models.Produto.empresa_id == current_user.empresa_id,
                    func.lower(models.Produto.codigo) == codigo_normalizado.lower(),
                    models.Produto.id != produto.id
                ).first()

                if codigo_conflict:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"O código {codigo_nf} já está vinculado ao produto {codigo_conflict.nome}. Ajuste a associação antes de confirmar."
                    )

                if (produto.codigo or "").strip() != codigo_normalizado.strip():
                    produto.codigo = codigo_normalizado.strip()
                    codigo_atualizado = True
                    codigos_sincronizados.append({
                        'produto_id': produto.id,
                        'produto_nome': produto.nome,
                        'codigo_anterior': codigo_anterior,
                        'codigo_novo': produto.codigo
                    })

            # Criar movimentação
            observacao_base = f"Importação automática - NF: {nota_fiscal}"
            if codigo_atualizado:
                origem_codigo = codigo_anterior or "sem código"
                observacao_base += f" | Código sincronizado ({origem_codigo} -> {produto.codigo})"
            if descricao_nf:
                observacao_base += f" | Produto NF: {descricao_nf}"

            movimentacao = models.MovimentacaoEstoque(
                produto_id=produto.id,
                tipo_movimentacao=tipo_movimentacao,
                quantidade=quantidade,
                quantidade_antes=quantidade_antes,
                quantidade_depois=nova_quantidade,
                origem='COMPRA' if tipo_movimentacao == 'ENTRADA' else 'VENDA',
                observacao=observacao_base,
                usuario_id=current_user.id
            )

            if codigo_atualizado:
                movimentacao.dados_antes_edicao = json.dumps({'codigo': codigo_anterior})
                movimentacao.dados_depois_edicao = json.dumps({'codigo': produto.codigo})

            db.add(movimentacao)

            # Atualizar estoque do produto
            produto.quantidade_em_estoque = nova_quantidade

            movimentacoes_criadas.append({
                'produto_id': produto.id,
                'produto_nome': produto.nome,
                'tipo': tipo_movimentacao,
                'quantidade': quantidade,
                'estoque_anterior': quantidade_antes,
                'estoque_novo': nova_quantidade,
                'codigo_sincronizado': produto.codigo if codigo_atualizado else None
            })

            produtos_atualizados.append(produto.nome)
        
        db.commit()
        
        return {
            'sucesso': True,
            'mensagem': f'Processamento concluído com sucesso! {len(movimentacoes_criadas)} movimentações registradas.',
            'movimentacoes_criadas': len(movimentacoes_criadas),
            'produtos_atualizados': produtos_atualizados,
            'detalhes': movimentacoes_criadas,
            'codigos_sincronizados': codigos_sincronizados
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
    "/processar-pdf-entrada",
    response_model=Dict[str, Any],
    summary="Processa PDF de nota fiscal de entrada",
    description="Extrai dados de um PDF de nota fiscal de entrada e registra as movimentações de estoque automaticamente."
)
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
        
        print(f"DEBUG: Arquivo salvo temporariamente em {temp_file_path}")
        
        # Extrair dados do PDF de entrada
        print(f"DEBUG: Iniciando extração de dados do PDF de entrada")
        dados_extraidos = extrair_dados_pdf_entrada(temp_file_path)
        print(f"DEBUG: Dados extraídos: {dados_extraidos}")
        
        # Limpar arquivo temporário
        os.unlink(temp_file_path)
        
        if not dados_extraidos or not dados_extraidos.get('produtos'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não foi possível extrair dados válidos do PDF de entrada"
            )
        
        # Processar movimentações de entrada
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
            
            # Criar movimentação de entrada
            observacao = f"Entrada automática - NF {dados_extraidos.get('nota_fiscal', 'N/A')} - Fornecedor: {dados_extraidos.get('fornecedor', 'N/A')}"
            
            movimentacao_data = schemas_movimentacao.MovimentacaoEstoqueCreate(
                produto_id=produto.id,
                tipo_movimentacao='ENTRADA',
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
                    'estoque_anterior': produto_atualizado.quantidade_em_estoque - quantidade,
                    'estoque_atual': produto_atualizado.quantidade_em_estoque
                })
            except Exception as e:
                produtos_nao_encontrados.append({
                    'codigo': codigo,
                    'descricao': produto_data.get('descricao', 'N/A'),
                    'erro': str(e)
                })
        
        return {
            'sucesso': True,
            'mensagem': f"PDF de entrada processado com sucesso! {len(movimentacoes_criadas)} movimentações criadas.",
            'arquivo': arquivo.filename,
            'tipo': 'ENTRADA',
            'tipo_movimentacao': 'ENTRADA',
            'nota_fiscal': dados_extraidos.get('nota_fiscal'),
            'data_emissao': dados_extraidos.get('data_emissao'),
            'fornecedor': dados_extraidos.get('fornecedor'),
            'cnpj_fornecedor': dados_extraidos.get('cnpj_fornecedor'),
            'movimentacoes_criadas': len(movimentacoes_criadas),
            'produtos_atualizados': [f"{item['codigo']} - {item['nome']}" for item in movimentacoes_criadas],
            'detalhes': {
                'produtos_processados': movimentacoes_criadas,
                'produtos_nao_encontrados': produtos_nao_encontrados,
                'total_produtos_pdf': len(dados_extraidos['produtos'])
            }
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
            detail=f"Erro ao processar PDF de entrada: {str(e)}"
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

    # Inicializar serviço de similaridade
    from ..services.product_similarity import product_similarity_service
    similarity_service = product_similarity_service

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
        if tipo_movimentacao == 'ENTRADA':
            dados_extraidos = extrair_dados_pdf_entrada(temp_file_path)
        else:
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
            descricao = produto_data.get('descricao', '')
            
            if not codigo or quantidade <= 0:
                continue
            
            # Buscar produto pelo código
            produto = db.query(models.Produto).filter(
                models.Produto.codigo == str(codigo),
                models.Produto.empresa_id == current_user.empresa_id
            ).first()
            
            if not produto:
                # Buscar produtos similares por nome para auxiliar associação posterior
                produtos_similares = similarity_service.find_similar_products(
                    search_name=descricao,
                    db=db,
                    empresa_id=current_user.empresa_id,
                    limit=5,
                    min_similarity=30
                ) if descricao else []
                # Mapear incluindo estoque_atual e renomear score para score_similaridade
                similares_mapeados = []
                for p in produtos_similares:
                    prod_db = db.query(models.Produto).filter(
                        models.Produto.id == p['id'],
                        models.Produto.empresa_id == current_user.empresa_id
                    ).first()
                    similares_mapeados.append({
                        'produto_id': p['id'],
                        'nome': p['nome'],
                        'codigo': p['codigo'],
                        'estoque_atual': getattr(prod_db, 'quantidade_em_estoque', 0) if prod_db else 0,
                        'score_similaridade': p['similarity_score'],
                        'categoria': p.get('categoria', ''),
                        'unidade_medida': p.get('unidade_medida', ''),
                        'preco_venda': p.get('preco_venda', 0)
                    })
                produtos_nao_encontrados.append({
                    'codigo': codigo,
                    'descricao': descricao or 'N/A',
                    'produtos_similares': similares_mapeados
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
                
                # Se for SAÍDA (venda), salvar preço no histórico
                if tipo_movimentacao == 'SAIDA' and produto_data.get('valor_unitario'):
                    valor_unitario = produto_data.get('valor_unitario')
                    valor_total = produto_data.get('valor_total', valor_unitario * quantidade)
                    
                    # Buscar cliente se houver CNPJ na NF
                    cliente_id = None
                    if dados_extraidos.get('cnpj_cliente'):
                        cliente = db.query(models.Cliente).filter(
                            models.Cliente.cnpj == dados_extraidos.get('cnpj_cliente'),
                            models.Cliente.empresa_id == current_user.empresa_id
                        ).first()
                        if cliente:
                            cliente_id = cliente.id
                    
                    # Criar registro de histórico de preço
                    historico_preco = models.HistoricoPrecoProduto(
                        produto_id=produto.id,
                        preco_unitario=valor_unitario,
                        quantidade=quantidade,
                        valor_total=valor_total,
                        nota_fiscal=dados_extraidos.get('nota_fiscal'),
                        empresa_id=current_user.empresa_id,
                        cliente_id=cliente_id
                    )
                    db.add(historico_preco)
                    db.commit()
                
                movimentacoes_criadas.append({
                    'produto_id': produto.id,
                    'codigo': codigo,
                    'nome': produto.nome,
                    'quantidade': quantidade,
                    'estoque_anterior': produto_atualizado.quantidade_em_estoque - (quantidade if tipo_movimentacao == 'ENTRADA' else -quantidade),
                    'estoque_atual': produto_atualizado.quantidade_em_estoque
                })
            except Exception as e:
                produtos_nao_encontrados.append({
                    'codigo': codigo,
                    'descricao': produto_data.get('descricao', 'N/A'),
                    'erro': str(e)
                })
        
        return {
            'sucesso': True,
            'mensagem': f'PDF processado com sucesso! {len(movimentacoes_criadas)} movimentações criadas.',
            'movimentacoes_criadas': len(movimentacoes_criadas),
            'produtos_atualizados': [f"{item['codigo']} - {item['nome']}" for item in movimentacoes_criadas],
            'tipo_movimentacao': tipo_movimentacao,
            'detalhes': {
                'arquivo': arquivo.filename,
                'nota_fiscal': dados_extraidos.get('nota_fiscal'),
                'data_emissao': dados_extraidos.get('data_emissao'),
                'cliente': dados_extraidos.get('cliente'),
                'produtos_processados': movimentacoes_criadas,
                'produtos_nao_encontrados': produtos_nao_encontrados,
                'total_produtos_pdf': len(dados_extraidos['produtos'])
            }
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


# ==================== ENDPOINTS DE PROCESSAMENTO DE XML (NF-e) ====================

@router.post(
    "/preview-xml",
    response_model=Dict[str, Any],
    summary="Visualiza dados extraídos do XML de NF-e",
    description="Extrai dados de um XML de nota fiscal eletrônica para visualização e confirmação antes do processamento. Identifica empresa, reconhece/cria cliente automaticamente."
)
async def preview_xml_movimentacao(
    arquivo: UploadFile = File(..., description="Arquivo XML da nota fiscal eletrônica"),
    tipo_movimentacao: Optional[str] = Form(None, description="Tipo de movimentação: ENTRADA ou SAIDA (opcional, auto-detecta)"),
    vendedor_id: Optional[int] = Form(None, description="ID do vendedor (opcional, para NF de saída)"),
    orcamento_id: Optional[int] = Form(None, description="ID do orçamento relacionado (opcional)"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Extrai dados do XML de NF-e para visualização antes do processamento."""
    
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
    
    if tipo_movimentacao and tipo_movimentacao not in ['ENTRADA', 'SAIDA']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de movimentação deve ser ENTRADA ou SAIDA"
        )
    
    try:
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as temp_file:
            content = await arquivo.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Processar XML
        from ..services.nf_xml_processor_service import NFXMLProcessorService
        xml_service = NFXMLProcessorService(db)
        
        resultado = xml_service.processar_nf_xml(
            caminho_xml=temp_file_path,
            tipo_movimentacao=tipo_movimentacao,
            empresa_id_override=current_user.empresa_id
        )
        
        # Limpar arquivo temporário
        os.unlink(temp_file_path)
        
        return {
            'sucesso': True,
            'tipo_movimentacao': resultado['tipo_movimentacao'],
            'empresa_id': resultado['empresa_id'],
            'nota_fiscal': resultado['nota_fiscal'],
            'chave_acesso': resultado.get('chave_acesso'),
            'data_emissao': resultado['data_emissao'],
            'cliente_id': resultado.get('cliente_id'),
            'cliente': resultado.get('cliente'),
            'cnpj_cliente': resultado.get('cnpj_cliente'),
            'cnpj_emitente': resultado.get('cnpj_emitente'),
            'nome_emitente': resultado.get('nome_emitente'),
            'valor_total': resultado.get('valor_total'),
            'produtos': resultado['produtos'],
            'produtos_encontrados': resultado['produtos_encontrados'],
            'produtos_nao_encontrados': resultado['produtos_nao_encontrados'],
            'total_produtos': resultado['total_produtos']
        }
        
    except Exception as e:
        import traceback
        logger.error(f"Erro ao processar XML: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar XML: {str(e)}"
        )


@router.post(
    "/processar-xml",
    response_model=Dict[str, Any],
    summary="Processa XML de NF-e e registra movimentações",
    description="Processa um XML de nota fiscal eletrônica e registra as movimentações de estoque automaticamente."
)
async def processar_xml_movimentacao(
    arquivo: UploadFile = File(..., description="Arquivo XML da nota fiscal eletrônica"),
    tipo_movimentacao: Optional[str] = Form(None, description="Tipo de movimentação: ENTRADA ou SAIDA (opcional, auto-detecta)"),
    vendedor_id: Optional[int] = Form(None, description="ID do vendedor (opcional, para NF de saída)"),
    orcamento_id: Optional[int] = Form(None, description="ID do orçamento relacionado (opcional)"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Processa XML de NF-e e registra movimentações automaticamente."""
    
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
    
    if tipo_movimentacao and tipo_movimentacao not in ['ENTRADA', 'SAIDA']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de movimentação deve ser ENTRADA ou SAIDA"
        )
    
    try:
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as temp_file:
            content = await arquivo.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Processar XML
        from ..services.nf_xml_processor_service import NFXMLProcessorService
        xml_service = NFXMLProcessorService(db)
        
        resultado_preview = xml_service.processar_nf_xml(
            caminho_xml=temp_file_path,
            tipo_movimentacao=tipo_movimentacao,
            empresa_id_override=current_user.empresa_id
        )
        
        # Preparar dados para confirmação
        produtos_confirmados = []
        for produto in resultado_preview['produtos']:
            if produto.get('encontrado') and produto.get('produto_id'):
                produtos_confirmados.append({
                    'produto_id': produto['produto_id'],
                    'quantidade': produto['quantidade'],
                    'valor_unitario': produto.get('valor_unitario', 0),
                    'valor_total': produto.get('valor_total', 0),
                    'codigo_nf': produto.get('codigo', ''),
                    'descricao_nf': produto.get('descricao', '')
                })
        
        if not produtos_confirmados:
            os.unlink(temp_file_path)
            return {
                'sucesso': False,
                'mensagem': 'Nenhum produto encontrado no sistema para processar.',
                'produtos_nao_encontrados': resultado_preview['produtos_nao_encontrados']
            }
        
        # Confirmar processamento usando o serviço existente
        from ..services.nf_processor_service import NFProcessorService
        nf_service = NFProcessorService(db)
        
        dados_confirmacao = {
            'nota_fiscal': resultado_preview['nota_fiscal'],
            'tipo_movimentacao': resultado_preview['tipo_movimentacao'],
            'empresa_id': resultado_preview['empresa_id'],
            'cliente_id': resultado_preview.get('cliente_id'),
            'cnpj_cliente': resultado_preview.get('cnpj_cliente'),
            'cliente': resultado_preview.get('cliente'),
            'vendedor_id': vendedor_id,
            'orcamento_id': orcamento_id,
            'produtos_confirmados': produtos_confirmados
        }
        
        resultado = nf_service.confirmar_processamento(
            dados_confirmacao=dados_confirmacao,
            usuario_id=current_user.id
        )
        
        # Limpar arquivo temporário
        os.unlink(temp_file_path)
        
        return {
            'sucesso': True,
            'mensagem': f'XML processado com sucesso! {resultado["movimentacoes_criadas"]} movimentações criadas.',
            'movimentacoes_criadas': resultado['movimentacoes_criadas'],
            'historicos_vendas': resultado.get('historicos_vendas', 0),
            'tipo_movimentacao': resultado_preview['tipo_movimentacao'],
            'nota_fiscal': resultado_preview['nota_fiscal'],
            'chave_acesso': resultado_preview.get('chave_acesso'),
            'data_emissao': resultado_preview['data_emissao'],
            'cliente': resultado_preview.get('cliente'),
            'cnpj_cliente': resultado_preview.get('cnpj_cliente'),
            'detalhes': {
                'arquivo': arquivo.filename,
                'produtos_processados': len(produtos_confirmados),
                'produtos_nao_encontrados': len(resultado_preview['produtos_nao_encontrados']),
                'total_produtos_xml': resultado_preview['total_produtos']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Erro ao processar XML: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar XML: {str(e)}"
        )


# ==================== ENDPOINTS DE MOVIMENTAÇÕES PENDENTES ====================
# IMPORTANTE: Estas rotas devem estar ANTES da rota /{produto_id} para evitar conflito

@router.post(
    "/pendentes",
    response_model=schemas_movimentacao.MovimentacaoEstoqueResponse,
    summary="Cria uma movimentação pendente",
    description="Registra uma movimentação pendente de aprovação. O estoque NÃO é alterado até que seja confirmada por um administrador."
)
def create_pending_movimentacao(
    movimentacao: schemas_movimentacao.MovimentacaoEstoquePendenteCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_operador)
):
    """Cria uma movimentação pendente para aprovação (apenas OPERADOR)."""
    try:
        movimentacao_criada = crud_movimentacao.create_pending_movimentacao(
            db=db,
            movimentacao=movimentacao,
            usuario_id=current_user.id,
            empresa_id=current_user.empresa_id
        )
        
        # Carregar relacionamentos para resposta
        db.refresh(movimentacao_criada)
        return schemas_movimentacao.MovimentacaoEstoqueResponse.model_validate(movimentacao_criada)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar movimentação pendente: {str(e)}"
        )

@router.get(
    "/pendentes",
    response_model=List[schemas_movimentacao.MovimentacaoEstoqueResponse],
    summary="Lista movimentações pendentes do usuário",
    description="Retorna todas as movimentações pendentes, confirmadas e rejeitadas do usuário logado."
)
def get_pending_movimentacoes_by_user(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_operador)
):
    """Lista movimentações pendentes do usuário (apenas OPERADOR)."""
    try:
        movimentacoes = crud_movimentacao.get_pending_movimentacoes_by_user(
            db=db,
            usuario_id=current_user.id,
            empresa_id=current_user.empresa_id,
            status_filter=status
        )
        return [schemas_movimentacao.MovimentacaoEstoqueResponse.model_validate(m) for m in movimentacoes]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar movimentações: {str(e)}"
        )

@router.get(
    "/pendentes/admin",
    response_model=List[schemas_movimentacao.MovimentacaoEstoqueResponse],
    summary="Lista todas as movimentações pendentes da empresa",
    description="Retorna todas as movimentações pendentes da empresa para aprovação (apenas ADMIN/GESTOR)."
)
def get_pending_movimentacoes_admin(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_admin_user)
):
    """Lista todas as movimentações pendentes da empresa (apenas ADMIN/GESTOR)."""
    try:
        movimentacoes = crud_movimentacao.get_pending_movimentacoes(
            db=db,
            empresa_id=current_user.empresa_id,
            status_filter=status
        )
        return [schemas_movimentacao.MovimentacaoEstoqueResponse.model_validate(m) for m in movimentacoes]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar movimentações: {str(e)}"
        )

@router.post(
    "/pendentes/{movimentacao_id}/confirmar",
    response_model=schemas_produto.Produto,
    summary="Confirma uma movimentação pendente",
    description="Confirma e aplica uma movimentação pendente ao estoque (apenas ADMIN/GESTOR)."
)
def confirm_movimentacao(
    movimentacao_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_admin_user)
):
    """Confirma uma movimentação pendente e aplica ao estoque."""
    try:
        produto = crud_movimentacao.confirm_movimentacao(
            db=db,
            movimentacao_id=movimentacao_id,
            aprovado_por_id=current_user.id,
            empresa_id=current_user.empresa_id
        )
        return produto
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao confirmar movimentação: {str(e)}"
        )

@router.patch(
    "/pendentes/{movimentacao_id}/editar",
    response_model=schemas_movimentacao.MovimentacaoEstoqueResponse,
    summary="Edita uma movimentação pendente (sem confirmar)",
    description="Edita uma movimentação pendente sem aplicar ao estoque (apenas ADMIN/GESTOR)."
)
def edit_pending_movimentacao(
    movimentacao_id: int,
    edicao: schemas_movimentacao.MovimentacaoEstoqueEdicao,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_admin_user)
):
    """Edita uma movimentação pendente sem confirmar (não altera o estoque)."""
    try:
        movimentacao = crud_movimentacao.edit_pending_movimentacao(
            db=db,
            movimentacao_id=movimentacao_id,
            empresa_id=current_user.empresa_id,
            edicao=edicao
        )
        db.refresh(movimentacao)
        return schemas_movimentacao.MovimentacaoEstoqueResponse.model_validate(movimentacao)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao editar movimentação: {str(e)}"
        )

@router.put(
    "/pendentes/{movimentacao_id}/editar-e-confirmar",
    response_model=schemas_produto.Produto,
    summary="Edita e confirma uma movimentação pendente",
    description="Edita uma movimentação pendente e confirma aplicando ao estoque (apenas ADMIN/GESTOR)."
)
def edit_and_confirm_movimentacao(
    movimentacao_id: int,
    edicao: schemas_movimentacao.MovimentacaoEstoqueEdicao,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_admin_user)
):
    """Edita uma movimentação pendente e confirma aplicando ao estoque."""
    try:
        produto = crud_movimentacao.edit_movimentacao(
            db=db,
            movimentacao_id=movimentacao_id,
            aprovado_por_id=current_user.id,
            empresa_id=current_user.empresa_id,
            edicao=edicao
        )
        return produto
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao editar e confirmar movimentação: {str(e)}"
        )

@router.post(
    "/pendentes/{movimentacao_id}/rejeitar",
    response_model=schemas_movimentacao.MovimentacaoEstoqueResponse,
    summary="Rejeita uma movimentação pendente",
    description="Rejeita uma movimentação pendente sem alterar o estoque (apenas ADMIN/GESTOR)."
)
def reject_movimentacao(
    movimentacao_id: int,
    dados: schemas_movimentacao.MovimentacaoEstoqueAprovacao = Body(...),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_admin_user)
):
    """Rejeita uma movimentação pendente sem alterar o estoque."""
    try:
        if not dados.motivo_rejeicao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Motivo da rejeição é obrigatório."
            )
        
        movimentacao = crud_movimentacao.reject_movimentacao(
            db=db,
            movimentacao_id=movimentacao_id,
            aprovado_por_id=current_user.id,
            motivo_rejeicao=dados.motivo_rejeicao,
            empresa_id=current_user.empresa_id
        )
        
        db.refresh(movimentacao)
        return schemas_movimentacao.MovimentacaoEstoqueResponse.model_validate(movimentacao)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao rejeitar movimentação: {str(e)}"
        )

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
    """Lista movimentações de um produto específico."""
    return crud_movimentacao.get_movimentacoes_by_produto_id(
        db=db, 
        produto_id=produto_id, 
        empresa_id=current_user.empresa_id
    )

def extrair_dados_pdf_entrada(caminho_pdf: str) -> Dict[str, Any]:
    """Extrai dados estruturados de um PDF de nota fiscal de ENTRADA."""
    
    print(f"DEBUG: Iniciando extração de dados de ENTRADA do arquivo: {caminho_pdf}")
    
    dados = {
        'nota_fiscal': None,
        'data_emissao': None,
        'fornecedor': None,  # Para entrada, é fornecedor ao invés de cliente
        'cnpj_fornecedor': None,
        'valor_total': None,
        'produtos': []
    }
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_completo = ""
            for page in pdf.pages:
                texto_completo += page.extract_text() or ""
        
        print(f"DEBUG: Texto extraído ({len(texto_completo)} caracteres)")
        
        # Salvar amostra do texto para debug
        try:
            with open('/tmp/debug_texto_pdf_entrada.txt', 'w', encoding='utf-8') as f:
                f.write(f"ARQUIVO ENTRADA: {caminho_pdf}\n")
                f.write(f"TAMANHO: {len(texto_completo)} caracteres\n")
                f.write("=" * 50 + "\n")
                f.write(texto_completo[:3000])  # Primeiros 3000 caracteres
                f.write("\n" + "=" * 50 + "\n")
                f.write("LINHAS COMPLETAS:\n")
                linhas = texto_completo.split('\n')
                for i, linha in enumerate(linhas[:100]):  # Primeiras 100 linhas
                    f.write(f"{i+1:3d}: {linha}\n")
            print("DEBUG: Texto de entrada salvo em /tmp/debug_texto_pdf_entrada.txt")
        except Exception as e:
            print(f"DEBUG: Erro ao salvar texto de entrada: {e}")
        
        # Extração inteligente e abrangente de dados
        dados = extrair_dados_inteligente_entrada(texto_completo, dados)
        
    except Exception as e:
        print(f"DEBUG: Erro ao processar PDF de entrada: {e}")
    
    return dados

def extrair_dados_inteligente_entrada(texto_completo: str, dados: Dict[str, Any]) -> Dict[str, Any]:
    """Extração inteligente de dados para PDFs de entrada - Formato GIRASSOL."""
    
    print(f"DEBUG: Iniciando extração inteligente para entrada - Formato GIRASSOL")
    
    # Padrões específicos para GIRASSOL - Número da nota fiscal
    padroes_nf = [
        r'NOTA FISCAL ELETRÔNICA[\s\S]*?Nº\s*(\d+)',
        r'NÚMERO[:\s]+(\d+)',
        r'NF[\s-]*e?[:\s]*(\d+)',
        r'N[úu]mero[:\s]+(\d+)',
        r'Nota[:\s]+(\d+)',
        r'(\d{6,})(?=\s|$)'  # Padrão para números longos como 125215
    ]
    
    for padrao in padroes_nf:
        nf_match = re.search(padrao, texto_completo, re.IGNORECASE)
        if nf_match:
            dados['nota_fiscal'] = nf_match.group(1)
            print(f"DEBUG: Nota fiscal encontrada: {dados['nota_fiscal']}")
            break
    
    # Padrões específicos para GIRASSOL - Data de emissão
    padroes_data = [
        r'DATA DE EMISSÃO[:\s]+(\d{2}/\d{2}/\d{4})',
        r'Data de Emissão[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        r'Emissão[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        r'Data[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})'
    ]
    
    for padrao in padroes_data:
        data_match = re.search(padrao, texto_completo, re.IGNORECASE)
        if data_match:
            dados['data_emissao'] = data_match.group(1)
            print(f"DEBUG: Data de emissão encontrada: {dados['data_emissao']}")
            break
    
    # Padrões específicos para GIRASSOL - Fornecedor/remetente
    padroes_fornecedor = [
        r'RAZÃO SOCIAL[\s\n]+([A-Z][A-Z\s&.-]+?)(?=\s+CNPJ|\s+\d{2}\.\d{3})',
        r'Remetente[:\s]+([A-Z][A-Z\s&.-]+?)\s+\d{2}\.\d{3}\.\d{3}',
        r'Fornecedor[:\s]+([A-Z][A-Z\s&.-]+?)\s+\d{2}\.\d{3}\.\d{3}',
        r'Nome/Razão\s+Social\s+([A-Z][A-Z\s&.-]+?)\s+\d{2}\.\d{3}\.\d{3}',
        r'GIRASSOL[\s\S]*?([A-Z][A-Z\s&.-]{10,}?)(?=\s+CNPJ|\s+\d{2}\.\d{3})'
    ]
    
    for padrao in padroes_fornecedor:
        fornecedor_match = re.search(padrao, texto_completo, re.IGNORECASE)
        if fornecedor_match:
            dados['fornecedor'] = fornecedor_match.group(1).strip()
            print(f"DEBUG: Fornecedor encontrado: {dados['fornecedor']}")
            break
    
    # Extração de CNPJ - buscar todos e identificar o do remetente
    cnpj_matches = re.findall(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', texto_completo)
    if cnpj_matches:
        # Para entrada, o primeiro CNPJ geralmente é do remetente/fornecedor
        dados['cnpj_fornecedor'] = cnpj_matches[0]
        print(f"DEBUG: CNPJ fornecedor encontrado: {dados['cnpj_fornecedor']}")
    
    # Padrões específicos para GIRASSOL - Valor total
    padroes_valor = [
        r'VALOR TOTAL DA NOTA[\s\n]+([\d.,]+)',
        r'Valor\s+Total\s+da\s+Nota\s+Fiscal\s+([\d.,]+)',
        r'Total\s+Geral[:\s]+R?\$?\s*([\d.,]+)',
        r'Valor\s+Total[:\s]+R?\$?\s*([\d.,]+)',
        r'Total[:\s]+R?\$?\s*([\d.,]+)'
    ]
    
    for padrao in padroes_valor:
        valor_match = re.search(padrao, texto_completo, re.IGNORECASE)
        if valor_match:
            valor_str = valor_match.group(1).replace('.', '').replace(',', '.')
            try:
                dados['valor_total'] = float(valor_str)
                print(f"DEBUG: Valor total encontrado: {dados['valor_total']}")
                break
            except ValueError:
                continue
    
    # Extração inteligente de produtos
    dados['produtos'] = extrair_produtos_inteligente_entrada(texto_completo)
    
    return dados

def extrair_produtos_inteligente_entrada(texto_completo: str) -> List[Dict[str, Any]]:
    """Extração inteligente de produtos para PDFs de entrada - usando versão melhorada."""
    return extrair_produtos_inteligente_entrada_melhorado(texto_completo)

def extrair_dados_pdf(caminho_pdf: str) -> Dict[str, Any]:
    """Extrai dados estruturados de um PDF de nota fiscal de SAÍDA."""
    
    print(f"DEBUG: Iniciando extração de dados de SAÍDA do arquivo: {caminho_pdf}")
    
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
        
        # Salvar amostra do texto para debug
        try:
            with open('/tmp/debug_texto_pdf.txt', 'w', encoding='utf-8') as f:
                f.write(f"ARQUIVO: {caminho_pdf}\n")
                f.write(f"TAMANHO: {len(texto_completo)} caracteres\n")
                f.write("=" * 50 + "\n")
                f.write(texto_completo[:3000])  # Primeiros 3000 caracteres
                f.write("\n" + "=" * 50 + "\n")
                f.write("LINHAS COMPLETAS:\n")
                linhas = texto_completo.split('\n')
                for i, linha in enumerate(linhas[:100]):  # Primeiras 100 linhas
                    f.write(f"{i+1:3d}: {linha}\n")
            print("DEBUG: Texto salvo em /tmp/debug_texto_pdf.txt")
        except Exception as e:
            print(f"DEBUG: Erro ao salvar texto: {e}")
        
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


@router.delete(
    "/{movimentacao_id}/reverter",
    response_model=Dict[str, Any],
    summary="Reverte uma movimentação de estoque",
    description="Desfaz uma movimentação de estoque, restaurando o estoque original. Apenas usuários com permissão podem reverter movimentações."
)
async def reverter_movimentacao(
    movimentacao_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Reverte uma movimentação de estoque:
    - Se foi ENTRADA, faz SAÍDA da mesma quantidade
    - Se foi SAÍDA, faz ENTRADA da mesma quantidade
    - Marca a movimentação original como revertida
    - Cria nova movimentação de reversão
    """
    
    try:
        # Buscar a movimentação original
        movimentacao = db.query(models.MovimentacaoEstoque).filter(
            models.MovimentacaoEstoque.id == movimentacao_id
        ).first()
        
        if not movimentacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movimentação {movimentacao_id} não encontrada"
            )
        
        # Verificar se a movimentação já foi revertida
        if movimentacao.revertida:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Esta movimentação já foi revertida em {movimentacao.data_reversao.strftime('%d/%m/%Y às %H:%M')}"
            )
        
        # Verificar permissões (apenas admin ou o próprio usuário que criou)
        if current_user.perfil not in ['ADMIN', 'GERENTE'] and movimentacao.usuario_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para reverter esta movimentação"
            )
        
        # Buscar o produto
        produto = db.query(models.Produto).filter(
            models.Produto.id == movimentacao.produto_id
        ).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        # Determinar o tipo de reversão (inverso do original)
        tipo_reversao = 'SAIDA' if movimentacao.tipo_movimentacao == 'ENTRADA' else 'ENTRADA'
        
        # Salvar estado anterior
        estoque_antes = produto.estoque_atual
        
        # Aplicar reversão no estoque
        if tipo_reversao == 'ENTRADA':
            produto.estoque_atual += movimentacao.quantidade
        else:
            produto.estoque_atual -= movimentacao.quantidade
        
        estoque_depois = produto.estoque_atual
        
        # Criar movimentação de reversão
        movimentacao_reversao = models.MovimentacaoEstoque(
            produto_id=produto.id,
            tipo_movimentacao=tipo_reversao,
            quantidade=movimentacao.quantidade,
            observacao=f"🔄 REVERSÃO da movimentação #{movimentacao_id} | Original: {movimentacao.observacao or 'Sem observação'}",
            origem='CORRECAO_MANUAL',
            quantidade_antes=estoque_antes,
            quantidade_depois=estoque_depois,
            usuario_id=current_user.id,
            reversao_de_id=movimentacao_id,
            status='CONFIRMADO'
        )
        
        # Marcar movimentação original como revertida
        movimentacao.revertida = True
        movimentacao.data_reversao = datetime.now()
        movimentacao.revertida_por_id = current_user.id
        
        # Salvar tudo
        db.add(movimentacao_reversao)
        db.commit()
        db.refresh(produto)
        db.refresh(movimentacao_reversao)
        
        logger.info(f"✅ Movimentação #{movimentacao_id} revertida com sucesso por {current_user.email}")
        
        return {
            'sucesso': True,
            'mensagem': f'Movimentação revertida com sucesso! Estoque restaurado de {estoque_antes} para {estoque_depois}.',
            'movimentacao_original_id': movimentacao_id,
            'movimentacao_reversao_id': movimentacao_reversao.id,
            'produto_id': produto.id,
            'produto_nome': produto.nome,
            'estoque_anterior': estoque_antes,
            'estoque_atual': estoque_depois,
            'quantidade_revertida': movimentacao.quantidade,
            'tipo_original': movimentacao.tipo_movimentacao,
            'tipo_reversao': tipo_reversao
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao reverter movimentação {movimentacao_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao reverter movimentação: {str(e)}"
        )