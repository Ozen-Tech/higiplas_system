# /backend/app/crud/orcamento.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..db import models
from ..schemas import orcamento as schemas_orcamento

def create_orcamento(db: Session, orcamento: schemas_orcamento.OrcamentoCreate, usuario_id: int, empresa_id: int):
    # Transação: Ou tudo funciona, ou nada é salvo.
    try:
        # 1. Cria o registro principal do orçamento
        db_orcamento = models.Orcamento(
            nome_cliente=orcamento.nome_cliente,
            data_validade=orcamento.data_validade,
            usuario_id=usuario_id,
        )
        db.add(db_orcamento)
        db.flush() # Usa flush para obter o ID do orçamento antes do commit final

        # 2. Itera sobre os itens, verifica o estoque e cria os registros de item
        for item_in in orcamento.itens:
            produto = db.query(models.Produto).filter(
                models.Produto.id == item_in.produto_id,
                models.Produto.empresa_id == empresa_id
            ).first()
            
            # Validação Crítica de Estoque
            if not produto:
                raise HTTPException(status_code=404, detail=f"Produto com ID {item_in.produto_id} não encontrado.")
            if produto.quantidade_em_estoque < item_in.quantidade:
                raise HTTPException(status_code=400, detail=f"Estoque insuficiente para '{produto.nome}'. Disponível: {produto.quantidade_em_estoque}, Solicitado: {item_in.quantidade}")
            
            db_item = models.OrcamentoItem(
                orcamento_id=db_orcamento.id,
                produto_id=item_in.produto_id,
                quantidade=item_in.quantidade,
                preco_unitario_congelado=produto.preco_venda # "Congela" o preço
            )
            db.add(db_item)

        db.commit()
        db.refresh(db_orcamento)
        usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
        if usuario:
            usuario.xp += 10 # 10 XP por orçamento criado
            if usuario.xp >= (usuario.level * 100):
                usuario.level += 1
                usuario.xp = 0
            db.commit()
        
        return db_orcamento
        
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno ao criar orçamento: {e}")

def get_orcamentos_by_user(db: Session, usuario_id: int):
    """Busca todos os orçamentos criados por um usuário específico."""
    return db.query(models.Orcamento).filter(
        models.Orcamento.usuario_id == usuario_id
    ).order_by(
        models.Orcamento.data_criacao.desc()
    ).all()

def get_orcamento_by_id(db: Session, orcamento_id: int, usuario_id: int):
    """Busca um único orçamento pelo ID, garantindo que pertence ao usuário."""
    return db.query(models.Orcamento).filter(
        models.Orcamento.id == orcamento_id,
        models.Orcamento.usuario_id == usuario_id
    ).first()