from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Dict
from app.db import models
from app.db.connection import get_db
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/vendas-simples",
    tags=["Vendas Simples"]
)

class PedidoItem(BaseModel):
    produto_id: int
    quantidade: int

class PedidoCreate(BaseModel):
    itens: List[PedidoItem]

@router.get("/", response_model=List[Dict], summary="Listar produtos disponíveis")
def listar_produtos(db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    produtos = db.query(models.Produto).filter(
        models.Produto.empresa_id == current_user.empresa_id,
        models.Produto.quantidade_em_estoque > 0
    ).all()
    return [
        {
            "id": p.id,
            "nome": p.nome,
            "codigo": p.codigo,
            "estoque_atual": p.quantidade_em_estoque,
            "preco_venda": p.preco_venda
        } for p in produtos
    ]

@router.post("/", summary="Registrar pedido de venda simples")
def registrar_pedido(pedido: PedidoCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    movimentacoes_criadas = []

    for item in pedido.itens:
        produto = db.query(models.Produto).filter(
            models.Produto.id == item.produto_id,
            models.Produto.empresa_id == current_user.empresa_id
        ).first()

        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto {item.produto_id} não encontrado")
        
        if produto.quantidade_em_estoque < item.quantidade:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente para {produto.nome}. Estoque atual: {produto.quantidade_em_estoque}, solicitado: {item.quantidade}"
            )

        # Registrar saída
        produto.quantidade_em_estoque -= item.quantidade
        movimentacao = models.MovimentacaoEstoque(
            produto_id=produto.id,
            tipo_movimentacao="SAIDA",
            quantidade=item.quantidade,
            observacao="Venda realizada pelo vendedor",
            usuario_id=current_user.id
        )
        db.add(movimentacao)
        movimentacoes_criadas.append({
            "produto_id": produto.id,
            "nome": produto.nome,
            "quantidade_vendida": item.quantidade,
            "estoque_atual": produto.quantidade_em_estoque
        })
    
    db.commit()

    return {
        "sucesso": True,
        "mensagem": f"{len(movimentacoes_criadas)} itens vendidos com sucesso",
        "detalhes": movimentacoes_criadas
    }
