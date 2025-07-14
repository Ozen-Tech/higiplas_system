# /backend/app/routers/insights.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import traceback

# Importações dos módulos do seu projeto
from app.db.connection import get_db
from app.db import models
from app.dependencies import get_current_user
from app.services import ai_service
from app.crud import produto as crud_produto
from app.crud import venda_historica as crud_historico

router = APIRouter(prefix="/insights", tags=["Inteligência Artificial"])

class QuestionRequest(BaseModel):
    question: str

def clean_sqlalchemy_object(obj):
    """Remove o estado interno do SQLAlchemy para uma serialização JSON limpa."""
    if not hasattr(obj, '__dict__'):
        return obj
    clean = obj.__dict__.copy()
    clean.pop('_sa_instance_state', None)
    return clean

@router.post("/ask")
def ask_ai_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Recebe uma pergunta, coleta dados atuais e históricos, e os envia para a IA.
    """
    print("\n--- [Insights] ROTA /insights/ask ACIONADA ---")
    try:
        # --- 1. Coleta de Dados Relevantes ---
        print("[Insights] Coletando dados do estoque atual...")
        produtos_atuais_db = crud_produto.get_produtos(db=db, empresa_id=current_user.empresa_id)
        
        print("[Insights] Coletando dados históricos de vendas...")
        historico_top_vendas_db = crud_historico.get_top_10_vendas(db)
        
        # --- Câmera de Segurança 1: Verificar se os dados foram encontrados ---
        print(f" -> Encontrados {len(produtos_atuais_db)} produtos no estoque.")
        print(f" -> Encontrados {len(historico_top_vendas_db)} registros de top vendas históricas.")
        if historico_top_vendas_db:
             # Mostra uma amostra para garantir que os dados estão corretos
            print(f" -> Amostra de histórico: {historico_top_vendas_db[0].descricao}")


        # --- 2. Formatação dos Dados para a IA ---
        print("[Insights] Formatando dados para o contexto da IA...")
        
        produtos_atuais = [
            {
                "nome": p.nome,
                "estoque_atual": p.quantidade_em_estoque,
                "estoque_minimo": p.estoque_minimo
            } for p in produtos_atuais_db
        ]
        
        # Limpando os objetos do SQLAlchemy antes de enviar
        historico_top_vendas = [clean_sqlalchemy_object(h) for h in historico_top_vendas_db]
        
        system_context_data = {
            "estoque_atual_da_empresa": produtos_atuais,
            "resumo_historico_dos_produtos_mais_vendidos": historico_top_vendas,
        }
        
        system_data_json_string = json.dumps(system_context_data, indent=2, default=str)

        # --- Câmera de Segurança 2: Verificar o JSON final ---
        print("[Insights] Contexto JSON final que será enviado para a IA:")
        print(system_data_json_string)


        # --- 3. Chamada ao Serviço de IA ---
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