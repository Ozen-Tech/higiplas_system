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
        # --- 1. COLETA DE DADOS RELEVANTES ---
        print("[Insights] Coletando dados do sistema...")
        
        # a) Estoque atual
        produtos_atuais_db = crud_produto.get_produtos(db=db, empresa_id=current_user.empresa_id)
        
        # b) Histórico de Vendas
        historico_top_vendas_db = crud_historico.get_top_10_vendas(db)

        # c) Movimentações Recentes (últimos 30 dias)
        movimentacoes_recentes_db = crud_movimentacao.get_recent_movimentacoes(
            db=db, 
            empresa_id=current_user.empresa_id, 
            days=30
        )
        
        # Logs de verificação
        print(f" -> Encontrados {len(produtos_atuais_db)} produtos no estoque.")
        print(f" -> Encontrados {len(historico_top_vendas_db)} registros de top vendas históricas.")
        print(f" -> Encontrados {len(movimentacoes_recentes_db)} registros de movimentações recentes.")


        # --- 2. FORMATAÇÃO DOS DADOS PARA A IA ---
        print("[Insights] Formatando dados para o contexto da IA...")
        
        produtos_atuais_formatado = [
            {
                "nome": p.nome,
                "codigo": p.codigo,
                "estoque_atual": p.quantidade_em_estoque,
                "estoque_minimo": p.estoque_minimo
            } for p in produtos_atuais_db
        ]
        
        historico_top_vendas_formatado = [clean_sqlalchemy_object(h) for h in historico_top_vendas_db]
        
        movimentacoes_recentes_formatado = [
            {
                "data": mov.data_movimentacao.strftime('%Y-%m-%d'),
                "produto": mov.produto.nome if mov.produto else 'N/A',
                "tipo": mov.tipo_movimentacao,
                "quantidade": mov.quantidade,
                "usuario": mov.usuario.nome if mov.usuario else 'N/A'
            }
            for mov in movimentacoes_recentes_db
        ]

        # Agrupa tudo em um único dicionário de contexto
        system_context_data = {
            "estoque_atual_da_empresa": produtos_atuais_formatado,
            "resumo_historico_dos_produtos_mais_vendidos": historico_top_vendas_formatado,
            "log_de_movimentacoes_recentes_ultimos_30_dias": movimentacoes_recentes_formatado
        }
        
        system_data_json_string = json.dumps(system_context_data, indent=2, default=str)

        print("[Insights] Contexto JSON final será enviado para a IA (amostra):")
        print((system_data_json_string[:1000] + '...') if len(system_data_json_string) > 1000 else system_data_json_string)


        # --- 3. CHAMADA AO SERVIÇO DE IA ---
        print("[Insights] Enviando contexto para o serviço de IA...")
        answer = ai_service.generate_analysis_from_data(
            user_question=request.question,
            system_data=system_data_json_string
        )

        print("[Insights] Resposta da IA recebida com sucesso.")
        return {"answer": answer}

    except Exception as e:
        print(f"❌ Erro grave no endpoint /insights/ask: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro interno no servidor ao processar a análise de IA.")


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