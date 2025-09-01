# /backend/app/routers/invoice_processing.py
import json
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.db.connection import get_db
from app.db import models
from app.dependencies import get_current_user
from app.services import ai_service
from app.utils.product_matcher import find_product_by_code_or_name

router = APIRouter(prefix="/invoices", tags=["Processamento de Notas Fiscais"])

def fuzzy_match_product(db: Session, description: str, empresa_id: int, codigo: str = None):
    """Tenta encontrar um produto no DB com base no código ou descrição da nota."""
    # Usar a nova função que busca por código primeiro, depois por nome
    produto, metodo_busca, score = find_product_by_code_or_name(
        db, codigo, description, empresa_id, threshold=0.5
    )
    
    if produto and metodo_busca == 'nome':
        print(f"DEBUG: Produto encontrado por nome na NF-e: {description} → {produto.nome} (score: {score:.2f})")
    
    return produto


@router.post("/parse-and-match", summary="Extrai produtos de uma NF-e e os associa ao estoque")
async def parse_invoice_and_match_products(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem (JPEG, PNG).")
        
    image_bytes = await file.read()
    
    try:
        # 1. Extrair o texto estruturado usando IA
        extracted_text = ai_service.extract_products_from_invoice_image(image_bytes)
        # Limpa a resposta da IA para garantir que seja um JSON válido
        cleaned_json_text = extracted_text.strip().replace("```json", "").replace("```", "")
        parsed_products = json.loads(cleaned_json_text)

        # 2. Associar produtos
        matched_products = []
        unmatched_products = []

        for item in parsed_products:
            descricao = item.get("descricao")
            quantidade = item.get("quantidade")
            codigo = item.get("codigo")  # Extrair código se disponível
            
            if not descricao or not quantidade:
                continue

            matched_product = fuzzy_match_product(db, descricao, current_user.empresa_id, codigo)

            if matched_product:
                matched_products.append({
                    "produto_id": matched_product.id,
                    "nome_db": matched_product.nome,
                    "descricao_nf": descricao,
                    "quantidade": quantidade,
                    "estoque_atual": matched_product.quantidade_em_estoque,
                    "preco_venda": matched_product.preco_venda
                })
            else:
                unmatched_products.append({
                    "descricao_nf": descricao,
                    "quantidade": quantidade
                })

        return {
            "matched": matched_products,
            "unmatched": unmatched_products
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="A IA retornou um formato inválido. Tente novamente.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento da IA: {str(e)}")