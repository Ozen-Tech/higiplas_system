# /backend/app/routers/insights.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import traceback
# Importações dos módulos da aplicação
from app.db.connection import get_db
from app.db import models
from app.dependencies import get_current_user
from app.services import ai_service
from app.crud import produto as crud_produto
from app.crud import movimentacao_estoque as crud_movimentacao 
from app.crud import venda_historica as crud_historico

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