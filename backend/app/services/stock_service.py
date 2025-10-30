from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import Optional, Literal, List, Dict
from datetime import datetime

from ..db import models
from ..core.logger import stock_operations_logger

OrigemMovimentacao = Literal['VENDA', 'DEVOLUCAO', 'CORRECAO_MANUAL', 'COMPRA', 'AJUSTE', 'OUTRO']
TipoMovimentacao = Literal['ENTRADA', 'SAIDA']

class StockService:
    
    @staticmethod
    def update_stock_transactionally(
        db: Session,
        produto_id: int,
        quantidade: float,
        tipo_movimentacao: TipoMovimentacao,
        usuario_id: int,
        empresa_id: int,
        origem: Optional[OrigemMovimentacao] = None,
        observacao: Optional[str] = None
    ) -> models.Produto:
        try:
            produto = db.query(models.Produto).with_for_update().filter(
                models.Produto.id == produto_id,
                models.Produto.empresa_id == empresa_id
            ).first()
            
            if not produto:
                stock_operations_logger.error(
                    f"[updateStock] FAILED - produto_id={produto_id} not found for empresa_id={empresa_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produto não encontrado ou não pertence à sua empresa."
                )
            
            quantidade_antes = produto.quantidade_em_estoque
            
            if tipo_movimentacao == 'SAIDA':
                if produto.quantidade_em_estoque < quantidade:
                    stock_operations_logger.warning(
                        f"[updateStock] INSUFFICIENT_STOCK - produto_id={produto_id}, "
                        f"requested={quantidade}, available={produto.quantidade_em_estoque}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Estoque insuficiente. Disponível: {produto.quantidade_em_estoque}, Solicitado: {quantidade}"
                    )
                produto.quantidade_em_estoque -= quantidade
            else:
                produto.quantidade_em_estoque += quantidade
            
            quantidade_depois = produto.quantidade_em_estoque
            
            movimentacao = models.MovimentacaoEstoque(
                produto_id=produto_id,
                tipo_movimentacao=tipo_movimentacao,
                quantidade=quantidade,
                observacao=observacao,
                usuario_id=usuario_id,
                origem=origem,
                quantidade_antes=quantidade_antes,
                quantidade_depois=quantidade_depois
            )
            
            db.add(movimentacao)
            db.commit()
            db.refresh(produto)
            
            stock_operations_logger.info(
                f"[updateStock] SUCCESS - produto_id={produto_id}, tipo={tipo_movimentacao}, "
                f"quantidade={quantidade}, origem={origem}, usuario_id={usuario_id}, "
                f"estoque_antes={quantidade_antes}, estoque_depois={quantidade_depois}"
            )
            
            return produto
            
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            stock_operations_logger.error(
                f"[updateStock] DATABASE_ERROR - produto_id={produto_id}, error={str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar estoque: {str(e)}"
            )
        except Exception as e:
            db.rollback()
            stock_operations_logger.error(
                f"[updateStock] UNEXPECTED_ERROR - produto_id={produto_id}, error={str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro inesperado ao atualizar estoque: {str(e)}"
            )
    
    @staticmethod
    def bulk_update_stock(
        db: Session,
        updates: List[Dict],
        usuario_id: int,
        empresa_id: int
    ) -> List[models.Produto]:
        produtos_atualizados = []
        
        try:
            for update in updates:
                produto = StockService.update_stock_transactionally(
                    db=db,
                    produto_id=update['produto_id'],
                    quantidade=update['quantidade'],
                    tipo_movimentacao=update['tipo_movimentacao'],
                    usuario_id=usuario_id,
                    empresa_id=empresa_id,
                    origem=update.get('origem'),
                    observacao=update.get('observacao')
                )
                produtos_atualizados.append(produto)
            
            stock_operations_logger.info(
                f"[bulkUpdateStock] SUCCESS - updated {len(produtos_atualizados)} products, usuario_id={usuario_id}"
            )
            
            return produtos_atualizados
            
        except Exception as e:
            db.rollback()
            stock_operations_logger.error(
                f"[bulkUpdateStock] FAILED - usuario_id={usuario_id}, error={str(e)}"
            )
            raise
    
    @staticmethod
    def get_stock_history(
        db: Session,
        produto_id: int,
        empresa_id: int,
        limit: int = 50
    ) -> List[models.MovimentacaoEstoque]:
        produto = db.query(models.Produto).filter(
            models.Produto.id == produto_id,
            models.Produto.empresa_id == empresa_id
        ).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        return db.query(models.MovimentacaoEstoque).filter(
            models.MovimentacaoEstoque.produto_id == produto_id
        ).order_by(
            models.MovimentacaoEstoque.data_movimentacao.desc()
        ).limit(limit).all()
