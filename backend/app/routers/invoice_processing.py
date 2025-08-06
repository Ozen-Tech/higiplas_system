# /backend/app/routers/invoice_processing.py
import json
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.connection import get_db
from app.db import models
from app.dependencies import get_current_user
from app.services import ai_service

router = APIRouter(prefix="/invoices", tags=["Processamento de Notas Fiscais"])

def fuzzy_match_product(db: Session, description: str, empresa_id: int):
    """Tenta encontrar um produto no DB com base na descrição da nota."""
    # Tenta uma correspondência exata primeiro
    exact_match = db.query(models.Produto).filter(
        models.Produto.empresa_id == empresa_id,
        func.lower(models.Produto.nome) == func.lower(description)
    ).first()
    if exact_match:
        return exact_match

    # Se falhar, tenta uma correspondência parcial (`ilike`)
    # Dividimos a descrição em palavras para uma busca mais flexível
    words = description.split()
    query_filters = [models.Produto.nome.ilike(f"%{word}%") for word in words]
    
    partial_match = db.query(models.Produto).filter(
        models.Produto.empresa_id == empresa_id,
        or_(*query_filters)
    ).first()

    return partial_match


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
            
            if not descricao or not quantidade:
                continue

            matched_product = fuzzy_match_product(db, descricao, current_user.empresa_id)

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