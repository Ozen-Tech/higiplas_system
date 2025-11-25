# /backend/app/routers/insights.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import traceback
from typing import List, Dict, Any, Optional
# Importações dos módulos da aplicação
from app.db.connection import get_db
from app.db import models
from app.dependencies import get_current_user
from app.services import ai_service
from ..crud import produto as crud_produto
from ..crud import movimentacao_estoque as crud_movimentacao 
from ..crud import venda_historica as crud_historico
from ..crud import analise_estoque as crud_analise
from ..crud import cliente_v2 as crud_cliente
from ..crud import orcamento as crud_orcamento
from ..crud import ordem_compra as crud_ordem_compra
from ..crud import fornecedor as crud_fornecedor
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, or_, desc

# Inicializa o router
router = APIRouter(prefix="/insights", tags=["Inteligência Artificial"])

# Define o corpo esperado para a requisição
class QuestionRequest(BaseModel):
    question: str

# Função auxiliar para limpar objetos SQLAlchemy antes da serialização
def clean_sqlalchemy_object(obj):
    if not hasattr(obj, '__dict__'):
        return obj
    clean = obj.__dict__.copy()
    clean.pop('_sa_instance_state', None)
    return clean


OBSERVACOES_VENDA_PADRAO = [
    "Venda Operador",
    "Venda realizada pelo vendedor",
    "Venda para"
]

OBSERVACOES_NF_PADRAO = [
    "Importação automática - NF",
    "Processamento automático - NF"
]


def _status_confirmado_expression():
    return or_(
        models.MovimentacaoEstoque.status == 'CONFIRMADO',
        models.MovimentacaoEstoque.status.is_(None)
    )


def _observacao_filter(patterns: List[str]):
    observacao_col = func.coalesce(models.MovimentacaoEstoque.observacao, "")
    return or_(*[observacao_col.ilike(f"{pattern}%") for pattern in patterns])


def _ensure_timezone(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

@router.post("/ask", summary="Faz uma pergunta para o assistente de IA")
def ask_ai_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Recebe uma pergunta do usuário, coleta dados relevantes do sistema
    (estoque atual, histórico de vendas e movimentações recentes)
    e envia para o modelo Gemini para obter uma análise.
    """
    print("\n--- [Insights] ROTA /insights/ask ACIONADA ---")
    try:
        # --- 1. COLETA COMPLETA DE DADOS DO SISTEMA ---
        print("[Insights] Coletando dados completos do sistema...")
        
        # a) Estoque atual com mais detalhes
        produtos_atuais_db = crud_produto.get_produtos(db=db, empresa_id=current_user.empresa_id)
        
        # b) Histórico de Vendas
        historico_top_vendas_db = crud_historico.get_top_10_vendas(db)
        
        now_utc = datetime.now(timezone.utc)

        # c) Movimentações Recentes (últimos 30 dias)
        movimentacoes_recentes_db = crud_movimentacao.get_recent_movimentacoes(
            db=db, 
            empresa_id=current_user.empresa_id, 
            days=30
        )

        status_confirmado_expr = _status_confirmado_expression()
        vendas_nf_expr = _observacao_filter(OBSERVACOES_NF_PADRAO)
        vendas_operador_expr = _observacao_filter(OBSERVACOES_VENDA_PADRAO)

        vendas_nf_resumo = db.query(
            models.MovimentacaoEstoque.produto_id,
            models.Produto.nome.label('produto_nome'),
            models.Produto.codigo.label('produto_codigo'),
            func.sum(models.MovimentacaoEstoque.quantidade).label('total_quantidade'),
            func.count(models.MovimentacaoEstoque.id).label('total_movimentacoes'),
            func.max(models.MovimentacaoEstoque.data_movimentacao).label('ultima_saida')
        ).join(
            models.Produto, models.MovimentacaoEstoque.produto_id == models.Produto.id
        ).filter(
            models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
            models.Produto.empresa_id == current_user.empresa_id,
            status_confirmado_expr,
            vendas_nf_expr
        ).group_by(
            models.MovimentacaoEstoque.produto_id,
            models.Produto.nome,
            models.Produto.codigo
        ).order_by(
            desc('total_quantidade')
        ).limit(100).all()

        vendas_operador_resumo = db.query(
            models.MovimentacaoEstoque.produto_id,
            models.Produto.nome.label('produto_nome'),
            models.Produto.codigo.label('produto_codigo'),
            func.sum(models.MovimentacaoEstoque.quantidade).label('total_quantidade'),
            func.count(models.MovimentacaoEstoque.id).label('total_movimentacoes'),
            func.max(models.MovimentacaoEstoque.data_movimentacao).label('ultima_saida')
        ).join(
            models.Produto, models.MovimentacaoEstoque.produto_id == models.Produto.id
        ).filter(
            models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
            models.Produto.empresa_id == current_user.empresa_id,
            status_confirmado_expr,
            vendas_operador_expr
        ).group_by(
            models.MovimentacaoEstoque.produto_id,
            models.Produto.nome,
            models.Produto.codigo
        ).order_by(
            desc('total_quantidade')
        ).limit(100).all()
        
        # d) Clientes (resumo)
        try:
            clientes_db = crud_cliente.get_clientes(
                db=db, 
                empresa_id=current_user.empresa_id, 
                limit=50
            )
        except Exception as e:
            print(f" -> Erro ao buscar clientes: {e}")
            clientes_db = []
        
        # e) Orçamentos recentes (últimos 30 dias)
        try:
            orcamentos_recentes_db = crud_orcamento.get_all_orcamentos(
                db=db, 
                empresa_id=current_user.empresa_id
            )
            # Filtrar últimos 30 dias
            data_limite = now_utc - timedelta(days=30)
            orcamentos_recentes_db = [
                o for o in orcamentos_recentes_db
                if _ensure_timezone(o.data_criacao) and _ensure_timezone(o.data_criacao) >= data_limite
            ][:50]  # Limitar a 50
        except Exception as e:
            print(f" -> Erro ao buscar orçamentos: {e}")
            orcamentos_recentes_db = []
        
        # f) Ordens de compra recentes
        try:
            ordens_compra_db = crud_ordem_compra.get_ordens_compra(
                db=db, 
                empresa_id=current_user.empresa_id
            )
            # Filtrar últimos 30 dias
            data_limite = now_utc - timedelta(days=30)
            ordens_compra_recentes = [
                oc for oc in ordens_compra_db
                if _ensure_timezone(oc.data_criacao) and _ensure_timezone(oc.data_criacao) >= data_limite
            ][:30]  # Limitar a 30
        except Exception as e:
            print(f" -> Erro ao buscar ordens de compra: {e}")
            ordens_compra_recentes = []
        
        # g) Fornecedores
        try:
            fornecedores_db = crud_fornecedor.get_fornecedores(
                db=db, 
                empresa_id=current_user.empresa_id
            )
        except Exception as e:
            print(f" -> Erro ao buscar fornecedores: {e}")
            fornecedores_db = []
        
        # h) Estatísticas gerais de movimentações
        try:
            total_entradas = db.query(func.sum(models.MovimentacaoEstoque.quantidade)).join(
                models.Produto
            ).filter(
                models.Produto.empresa_id == current_user.empresa_id,
                models.MovimentacaoEstoque.tipo_movimentacao == 'ENTRADA',
                models.MovimentacaoEstoque.data_movimentacao >= now_utc - timedelta(days=30)
            ).scalar() or 0
            
            total_saidas = db.query(func.sum(models.MovimentacaoEstoque.quantidade)).join(
                models.Produto
            ).filter(
                models.Produto.empresa_id == current_user.empresa_id,
                models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
                models.MovimentacaoEstoque.data_movimentacao >= now_utc - timedelta(days=30)
            ).scalar() or 0
        except Exception as e:
            print(f" -> Erro ao calcular estatísticas: {e}")
            total_entradas = 0
            total_saidas = 0
        
        # Logs de verificação
        print(f" -> Encontrados {len(produtos_atuais_db)} produtos no estoque.")
        print(f" -> Encontrados {len(historico_top_vendas_db)} registros de top vendas históricas.")
        print(f" -> Encontrados {len(movimentacoes_recentes_db)} registros de movimentações recentes.")
        print(f" -> Encontrados {len(clientes_db)} clientes.")
        print(f" -> Encontrados {len(orcamentos_recentes_db)} orçamentos recentes.")
        print(f" -> Encontrados {len(ordens_compra_recentes)} ordens de compra recentes.")
        print(f" -> Encontrados {len(fornecedores_db)} fornecedores.")


        # --- 2. FORMATAÇÃO DOS DADOS PARA A IA ---
        print("[Insights] Formatando dados para o contexto da IA...")
        
        # Limita a quantidade de dados para evitar exceder limites da API
        # Prioriza produtos com estoque baixo ou crítico
        produtos_ordenados = sorted(
            produtos_atuais_db,
            key=lambda p: (
                0 if p.quantidade_em_estoque <= (p.estoque_minimo or 0) else 1,  # Críticos primeiro
                -p.quantidade_em_estoque  # Menor estoque primeiro
            )
        )
        
        # Limita a 100 produtos (priorizando os críticos)
        produtos_limitados = produtos_ordenados[:100]
        
        # Formata produtos com mais detalhes
        produtos_atuais_formatado = [
            {
                "id": p.id,
                "nome": p.nome,
                "codigo": p.codigo,
                "categoria": p.categoria or "Sem categoria",
                "estoque_atual": p.quantidade_em_estoque,
                "estoque_minimo": p.estoque_minimo or 0,
                "preco_custo": float(p.preco_custo) if p.preco_custo else None,
                "preco_venda": float(p.preco_venda) if p.preco_venda else None,
                "unidade_medida": p.unidade_medida,
                "status_estoque": "CRÍTICO" if p.quantidade_em_estoque <= (p.estoque_minimo or 0) else "OK"
            } for p in produtos_limitados
        ]
        
        historico_top_vendas_formatado = [clean_sqlalchemy_object(h) for h in historico_top_vendas_db]
        
        # Limita movimentações recentes a 100 registros
        movimentacoes_limitadas = movimentacoes_recentes_db[:100]
        
        movimentacoes_recentes_formatado = [
            {
                "data": mov.data_movimentacao.strftime('%Y-%m-%d %H:%M'),
                "produto": mov.produto.nome if mov.produto else 'N/A',
                "produto_codigo": mov.produto.codigo if mov.produto else 'N/A',
                "tipo": mov.tipo_movimentacao,
                "quantidade": mov.quantidade,
                "usuario": mov.usuario.nome if mov.usuario else 'N/A',
                "observacao": mov.observacao or ""
            }
            for mov in movimentacoes_limitadas
        ]

        vendas_nf_formatado = [
            {
                "produto_id": registro.produto_id,
                "produto": registro.produto_nome,
                "codigo": registro.produto_codigo,
                "quantidade_total_saida_nf": float(registro.total_quantidade),
                "movimentacoes_registradas": int(registro.total_movimentacoes),
                "ultima_saida_nf": registro.ultima_saida.strftime('%Y-%m-%d %H:%M') if registro.ultima_saida else None
            }
            for registro in vendas_nf_resumo
        ]

        vendas_operador_formatado = [
            {
                "produto_id": registro.produto_id,
                "produto": registro.produto_nome,
                "codigo": registro.produto_codigo,
                "quantidade_total_vendida_operador": float(registro.total_quantidade),
                "movimentacoes_registradas": int(registro.total_movimentacoes),
                "ultima_saida_operador": registro.ultima_saida.strftime('%Y-%m-%d %H:%M') if registro.ultima_saida else None
            }
            for registro in vendas_operador_resumo
        ]
        
        # Formata clientes
        clientes_formatado = [
            {
                "id": c.id,
                "nome": c.razao_social or "Sem nome",
                "telefone": c.telefone or "N/A",
                "cidade": c.endereco.split(',')[-1].strip() if c.endereco and ',' in c.endereco else (c.endereco or "N/A"),
                "status_pagamento": c.status_pagamento or "N/A",
                "empresa_vinculada": c.empresa_vinculada or "N/A"
            } for c in clientes_db[:50]
        ]

        # Formata orçamentos recentes
        orcamentos_formatado = [
            {
                "id": o.id,
                "cliente": o.cliente.razao_social if o.cliente else "N/A",
                "status": o.status,
                "data_criacao": o.data_criacao.strftime('%Y-%m-%d') if o.data_criacao else "N/A",
                "total_itens": len(o.itens),
                "vendedor": o.usuario.nome if o.usuario else "N/A",
                "valor_total": sum(item.quantidade * item.preco_unitario_congelado for item in o.itens)
            } for o in orcamentos_recentes_db
        ]
        
        # Formata ordens de compra
        ordens_compra_formatado = [
            {
                "id": oc.id,
                "fornecedor": oc.fornecedor.nome if oc.fornecedor else "N/A",
                "status": oc.status,
                "data_criacao": oc.data_criacao.strftime('%Y-%m-%d') if oc.data_criacao else "N/A",
                "data_recebimento": oc.data_recebimento.strftime('%Y-%m-%d') if oc.data_recebimento else None,
                "total_itens": len(oc.itens),
                "valor_total": sum(item.quantidade_solicitada * item.custo_unitario_registrado for item in oc.itens)
            } for oc in ordens_compra_recentes
        ]
        
        # Formata fornecedores
        fornecedores_formatado = [
            {
                "id": f.id,
                "nome": f.nome,
                "email": f.contato_email or "N/A",
                "telefone": f.contato_telefone or "N/A"
            } for f in fornecedores_db
        ]
        
        print(f" -> Dados formatados: {len(produtos_atuais_formatado)} produtos, {len(movimentacoes_recentes_formatado)} movimentações, {len(clientes_formatado)} clientes, {len(orcamentos_formatado)} orçamentos, {len(ordens_compra_formatado)} ordens de compra")

        # Agrupa tudo em um único dicionário de contexto completo
        system_context_data = {
            "estoque_atual_da_empresa": produtos_atuais_formatado,
            "resumo_historico_dos_produtos_mais_vendidos": historico_top_vendas_formatado,
            "log_de_movimentacoes_recentes_ultimos_30_dias": movimentacoes_recentes_formatado,
            "resumo_vendas_nf_confirmadas": vendas_nf_formatado,
            "resumo_vendas_vendedores_confirmadas": vendas_operador_formatado,
            "clientes_cadastrados": clientes_formatado,
            "orcamentos_recentes_ultimos_30_dias": orcamentos_formatado,
            "ordens_de_compra_recentes_ultimos_30_dias": ordens_compra_formatado,
            "fornecedores_cadastrados": fornecedores_formatado,
            "estatisticas_gerais_ultimos_30_dias": {
                "total_entradas_estoque": float(total_entradas),
                "total_saidas_estoque": float(total_saidas),
                "saldo_movimentacoes": float(total_entradas - total_saidas),
                "total_produtos_cadastrados": len(produtos_atuais_db),
                "total_clientes": len(clientes_db),
                "total_fornecedores": len(fornecedores_db)
            }
        }
        
        system_data_json_string = json.dumps(system_context_data, indent=2, default=str)

        print("[Insights] Contexto JSON final será enviado para a IA (amostra):")
        print((system_data_json_string[:1000] + '...') if len(system_data_json_string) > 1000 else system_data_json_string)


        # --- 3. CHAMADA AO SERVIÇO DE IA ---
        print("[Insights] Enviando contexto para o serviço de IA...")
        try:
        answer = ai_service.generate_analysis_from_data(
            user_question=request.question,
            system_data=system_data_json_string
        )
        print("[Insights] Resposta da IA recebida com sucesso.")
        return {"answer": answer}
        except Exception as ai_error:
            error_message = str(ai_error)
            print(f"❌ Erro na chamada da IA: {error_message}")
            
            # Trata erros específicos da API
            if "RATE_LIMIT_EXCEEDED" in error_message:
                raise HTTPException(
                    status_code=429,
                    detail="Limite de requisições da API excedido. Por favor, aguarde alguns minutos antes de tentar novamente."
                )
            elif "API_PERMISSION_DENIED" in error_message:
                raise HTTPException(
                    status_code=403,
                    detail="Problema de permissão na API. Entre em contato com o administrador do sistema."
                )
            elif "API_INVALID_REQUEST" in error_message:
                raise HTTPException(
                    status_code=400,
                    detail="O contexto enviado é muito grande. Tente fazer uma pergunta mais específica."
                )
            else:
                # Re-levanta a exceção para ser capturada pelo handler geral
                raise

    except HTTPException:
        # Re-levanta HTTPExceptions (já tratadas acima)
        raise
    except Exception as e:
        print(f"❌ Erro grave no endpoint /insights/ask: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor ao processar a análise de IA: {str(e)}")


# Novos endpoints para análise assertiva de estoque

@router.get("/estoque-minimo/{produto_id}", summary="Calcula estoque mínimo baseado na demanda")
def calcular_estoque_minimo_produto(
    produto_id: int,
    dias_analise: int = 90,
    dias_lead_time: int = 7,
    margem_seguranca: float = 1.2,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Calcula o estoque mínimo ideal para um produto específico baseado no histórico de vendas.
    
    - **produto_id**: ID do produto
    - **dias_analise**: Período de análise em dias (padrão: 90)
    - **dias_lead_time**: Tempo de reposição em dias (padrão: 7)
    - **margem_seguranca**: Margem de segurança (padrão: 1.2 = 20%)
    """
    try:
        resultado = crud_analise.calcular_estoque_minimo_por_demanda(
            db=db,
            produto_id=produto_id,
            empresa_id=current_user.empresa_id,
            dias_analise=dias_analise,
            dias_lead_time=dias_lead_time,
            margem_seguranca=margem_seguranca
        )
        return resultado
    except Exception as e:
        print(f"❌ Erro ao calcular estoque mínimo: {e}")
        raise HTTPException(status_code=500, detail="Erro ao calcular estoque mínimo")


@router.get("/analise-completa", summary="Análise completa de todos os produtos")
def analise_completa_estoque(
    dias_analise: int = 90,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Gera uma análise completa de estoque para todos os produtos da empresa.
    Inclui estoque mínimo, produtos críticos, alta rotatividade e sem movimento.
    """
    try:
        resultado = crud_analise.gerar_relatorio_completo_estoque(
            db=db,
            empresa_id=current_user.empresa_id
        )
        return resultado
    except Exception as e:
        print(f"❌ Erro na análise completa: {e}")
        raise HTTPException(status_code=500, detail="Erro na análise completa de estoque")


@router.get("/produtos-criticos", summary="Lista produtos com estoque crítico")
def produtos_estoque_critico(
    dias_analise: int = 90,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna produtos com estoque em nível crítico baseado na análise de demanda.
    """
    try:
        analises = crud_analise.analisar_todos_produtos_estoque_minimo(
            db=db,
            empresa_id=current_user.empresa_id,
            dias_analise=dias_analise
        )
        
        # Filtra apenas produtos críticos e baixo estoque
        produtos_criticos = [
            produto for produto in analises 
            if produto.get('status_estoque') in ['CRÍTICO', 'BAIXO']
        ]
        
        return {
            "total_produtos_criticos": len(produtos_criticos),
            "produtos": produtos_criticos
        }
    except Exception as e:
        print(f"❌ Erro ao buscar produtos críticos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar produtos críticos")


@router.get("/alta-rotatividade", summary="Produtos com alta rotatividade")
def produtos_alta_rotatividade(
    dias: int = 30,
    limite: int = 10,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna os produtos com maior rotatividade (mais vendidos) no período.
    """
    try:
        resultado = crud_analise.obter_produtos_alta_rotatividade(
            db=db,
            empresa_id=current_user.empresa_id,
            dias=dias,
            limite=limite
        )
        return {
            "periodo_dias": dias,
            "total_produtos": len(resultado),
            "produtos": resultado
        }
    except Exception as e:
        print(f"❌ Erro ao buscar produtos de alta rotatividade: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar produtos de alta rotatividade")


@router.get("/sem-movimento", summary="Produtos sem movimento")
def produtos_sem_movimento(
    dias: int = 60,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna produtos sem movimento (vendas) no período especificado.
    Útil para identificar produtos parados que ocupam capital.
    """
    try:
        resultado = crud_analise.obter_produtos_sem_movimento(
            db=db,
            empresa_id=current_user.empresa_id,
            dias=dias
        )
        
        valor_total_parado = sum(produto['valor_estoque'] for produto in resultado)
        
        return {
            "periodo_dias": dias,
            "total_produtos_sem_movimento": len(resultado),
            "valor_total_parado": round(valor_total_parado, 2),
            "produtos": resultado
        }
    except Exception as e:
        print(f"❌ Erro ao buscar produtos sem movimento: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar produtos sem movimento")


@router.post("/sugerir-compras", summary="Sugere compras baseadas na análise")
def sugerir_compras(
    dias_analise: int = 90,
    dias_lead_time: int = 7,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Gera sugestões de compra baseadas na análise de demanda e estoque atual.
    """
    try:
        # Analisa todos os produtos
        analises = crud_analise.analisar_todos_produtos_estoque_minimo(
            db=db,
            empresa_id=current_user.empresa_id,
            dias_analise=dias_analise
        )
        
        sugestoes_compra = []
        
        for produto in analises:
            if produto.get('status_estoque') in ['CRÍTICO', 'BAIXO']:
                quantidade_sugerida = max(
                    produto.get('estoque_minimo_sugerido', 0) - produto.get('estoque_atual', 0),
                    0
                )
                
                if quantidade_sugerida > 0:
                    sugestoes_compra.append({
                        "produto_nome": produto.get('produto_nome'),
                        "produto_codigo": produto.get('produto_codigo'),
                        "estoque_atual": produto.get('estoque_atual'),
                        "estoque_minimo_sugerido": produto.get('estoque_minimo_sugerido'),
                        "quantidade_comprar": quantidade_sugerida,
                        "prioridade": "ALTA" if produto.get('status_estoque') == 'CRÍTICO' else "MÉDIA",
                        "demanda_media_diaria": produto.get('demanda_media_diaria'),
                        "dias_cobertura_atual": produto.get('dias_cobertura_atual')
                    })
        
        # Ordena por prioridade
        sugestoes_compra.sort(key=lambda x: 0 if x['prioridade'] == 'ALTA' else 1)
        
        return {
            "total_sugestoes": len(sugestoes_compra),
            "sugestoes_alta_prioridade": len([s for s in sugestoes_compra if s['prioridade'] == 'ALTA']),
            "sugestoes": sugestoes_compra
        }
        
    except Exception as e:
        print(f"❌ Erro ao gerar sugestões de compra: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar sugestões de compra")