from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
from app.db.connection import get_db
from app.crud import produto as crud_produto
from app.dependencies import get_current_user
from app.services import ai_service
from app.db import models

router = APIRouter(prefix="/insights", tags=["Inteligência Artificial"])

class QuestionRequest(BaseModel):
     question: str

@router.post("/ask")
def ask_ai_question(
     request: QuestionRequest,
     db: Session = Depends(get_db),
     current_user: models.Usuario = Depends(get_current_user)
 ):
     # 1. Coletar todos os dados de produtos para dar contexto à IA
     produtos = crud_produto.get_produtos(db=db, empresa_id=current_user.empresa_id)
     
     # 2. Formatar os dados em um JSON legível
     # Nós podemos adicionar mais dados aqui no futuro (movimentações, etc)
     data_for_ai = {
         "visao_geral_produtos": [p.__dict__ for p in produtos]
     }
     # Limpar metadados do SQLAlchemy que não são úteis para a IA
     for p_dict in data_for_ai["visao_geral_produtos"]:
         p_dict.pop('_sa_instance_state', None)
     
     system_data_json = json.dumps(data_for_ai, default=str, indent=2)

     # 3. Chamar o serviço de IA com a pergunta do usuário e os dados coletados
     answer = ai_service.generate_analysis_from_data(
         user_question=request.question,
         system_data=system_data_json
     )
     
     return {"answer": answer, "question": request.question}
     