# /backend/app/routers/insights.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import traceback # Útil para depurar erros

# Importações dos módulos do seu projeto
from app.db.connection import get_db
from app.db import models
from app.dependencies import get_current_user
from app.services import ai_service
from app.crud import produto as crud_produto
from app.crud import venda_historica as crud_historico # Importa o novo CRUD

router = APIRouter(prefix="/insights", tags=["Inteligência Artificial"])

class QuestionRequest(BaseModel):
    question: str

def format_data_for_ai(data_object):
    """
    Função auxiliar para limpar o estado do SQLAlchemy de um objeto antes de serializar.
    """
    if hasattr(data_object, '__dict__'):
        # Clona o dicionário para não modificar o objeto original
        clean_dict = data_object.__dict__.copy()
        clean_dict.pop('_sa_instance_state', None)
        return clean_dict
    return data_object


@router.post("/ask")
def ask_ai_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Recebe uma pergunta do usuário, coleta dados do sistema (estoque atual e
    histórico de vendas) e os envia para a IA para análise.
    """
    try:
        # 1. Coleta de Dados Relevantes
        print("[Insights] Coletando dados atuais e históricos...")
        
        # Dados do estoque atual (otimizado para enviar apenas o necessário)
        produtos_atuais_db = crud_produto.get_produtos(db=db, empresa_id=current_user.empresa_id)
        produtos_atuais = [
            {
                "nome": p.nome,
                "estoque_atual": p.quantidade_em_estoque,
                "estoque_minimo": p.estoque_minimo
            }
            for p in produtos_atuais_db
        ]

        # Dados históricos (usando a função do novo CRUD)
        historico_top_vendas_db = crud_historico.get_top_10_vendas(db)
        historico_top_vendas = [format_data_for_ai(h) for h in historico_top_vendas_db]
        
        historico_top_lucro_db = crud_historico.get_top_10_lucro(db)
        historico_top_lucro = [format_data_for_ai(h) for h in historico_top_lucro_db]

        # 2. Formatação dos dados em um único objeto de contexto para a IA
        system_context_data = {
            "estoque_atual": produtos_atuais,
            "resumo_historico_mais_vendidos": historico_top_vendas,
            "resumo_historico_mais_lucrativos": historico_top_lucro,
        }

        # Converte tudo para uma string JSON formatada
        system_data_json_string = json.dumps(system_context_data, indent=2, default=str)

        print("[Insights] Enviando contexto para a IA...")
        # 3. Chamada ao Serviço de IA
        answer = ai_service.generate_analysis_from_data(
            user_question=request.question,
            system_data=system_data_json_string
        )

        return {"answer": answer}

    except Exception as e:
        print(f"❌ Erro no endpoint /insights/ask: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno no servidor ao processar a análise de IA.")