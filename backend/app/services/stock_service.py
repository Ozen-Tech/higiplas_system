from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import Optional, Literal, List, Dict
from datetime import datetime
import json

from ..db import models
from ..core.logger import stock_operations_logger
from ..schemas.movimentacao_estoque import MotivoMovimentacao, StatusMovimentacao

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
        observacao: Optional[str] = None,
        apply_immediately: bool = True
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
                quantidade_depois=quantidade_depois,
                status='CONFIRMADO' if apply_immediately else 'PENDENTE'
            )
            
            db.add(movimentacao)
            
            if not apply_immediately:
                # Se não aplicar imediatamente, não altera o estoque
                db.commit()
                db.refresh(movimentacao)
                return produto
            
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
    
    @staticmethod
    def create_pending_movimentacao(
        db: Session,
        produto_id: int,
        quantidade: float,
        tipo_movimentacao: TipoMovimentacao,
        usuario_id: int,
        empresa_id: int,
        motivo_movimentacao: MotivoMovimentacao,
        observacao: Optional[str] = None,
        observacao_motivo: Optional[str] = None
    ) -> models.MovimentacaoEstoque:
        """Cria uma movimentação pendente sem alterar o estoque."""
        try:
            # Verificar se o produto existe e pertence à empresa
            produto = db.query(models.Produto).filter(
                models.Produto.id == produto_id,
                models.Produto.empresa_id == empresa_id
            ).first()
            
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produto não encontrado ou não pertence à sua empresa."
                )
            
            quantidade_antes = produto.quantidade_em_estoque
            
            movimentacao = models.MovimentacaoEstoque(
                produto_id=produto_id,
                tipo_movimentacao=tipo_movimentacao,
                quantidade=quantidade,
                observacao=observacao,
                usuario_id=usuario_id,
                quantidade_antes=quantidade_antes,
                quantidade_depois=quantidade_antes,  # Não altera ainda
                status='PENDENTE',
                motivo_movimentacao=motivo_movimentacao.value if isinstance(motivo_movimentacao, MotivoMovimentacao) else motivo_movimentacao
            )
            
            # Armazenar observação do motivo se fornecida
            movimentacao.observacao_motivo = observacao_motivo
            
            db.add(movimentacao)
            db.commit()
            db.refresh(movimentacao)
            
            stock_operations_logger.info(
                f"[createPendingMovimentacao] SUCCESS - movimentacao_id={movimentacao.id}, "
                f"produto_id={produto_id}, tipo={tipo_movimentacao}, quantidade={quantidade}, "
                f"usuario_id={usuario_id}, motivo={motivo_movimentacao}"
            )
            
            return movimentacao
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            stock_operations_logger.error(
                f"[createPendingMovimentacao] ERROR - produto_id={produto_id}, error={str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar movimentação pendente: {str(e)}"
            )
    
    @staticmethod
    def confirm_movimentacao(
        db: Session,
        movimentacao_id: int,
        aprovado_por_id: int,
        empresa_id: int
    ) -> models.Produto:
        """Confirma uma movimentação pendente e aplica ao estoque."""
        try:
            movimentacao = db.query(models.MovimentacaoEstoque).join(
                models.Produto
            ).filter(
                models.MovimentacaoEstoque.id == movimentacao_id,
                models.Produto.empresa_id == empresa_id,
                models.MovimentacaoEstoque.status == 'PENDENTE'
            ).first()
            
            if not movimentacao:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Movimentação pendente não encontrada ou já foi processada."
                )
            
            produto = db.query(models.Produto).with_for_update().filter(
                models.Produto.id == movimentacao.produto_id,
                models.Produto.empresa_id == empresa_id
            ).first()
            
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produto não encontrado."
                )
            
            quantidade_antes = produto.quantidade_em_estoque
            
            # Aplicar movimentação ao estoque
            if movimentacao.tipo_movimentacao == 'SAIDA':
                if produto.quantidade_em_estoque < movimentacao.quantidade:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Estoque insuficiente. Disponível: {produto.quantidade_em_estoque}, Solicitado: {movimentacao.quantidade}"
                    )
                produto.quantidade_em_estoque -= movimentacao.quantidade
            else:
                produto.quantidade_em_estoque += movimentacao.quantidade
            
            quantidade_depois = produto.quantidade_em_estoque
            
            # Atualizar movimentação
            movimentacao.status = 'CONFIRMADO'
            movimentacao.aprovado_por_id = aprovado_por_id
            movimentacao.data_aprovacao = datetime.utcnow()
            movimentacao.quantidade_depois = quantidade_depois
            
            db.commit()
            db.refresh(produto)
            db.refresh(movimentacao)
            
            stock_operations_logger.info(
                f"[confirmMovimentacao] SUCCESS - movimentacao_id={movimentacao_id}, "
                f"aprovado_por_id={aprovado_por_id}, estoque_antes={quantidade_antes}, "
                f"estoque_depois={quantidade_depois}"
            )
            
            return produto
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            stock_operations_logger.error(
                f"[confirmMovimentacao] ERROR - movimentacao_id={movimentacao_id}, error={str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao confirmar movimentação: {str(e)}"
            )
    
    @staticmethod
    def reject_movimentacao(
        db: Session,
        movimentacao_id: int,
        aprovado_por_id: int,
        motivo_rejeicao: str,
        empresa_id: int
    ) -> models.MovimentacaoEstoque:
        """Rejeita uma movimentação pendente sem alterar o estoque."""
        try:
            movimentacao = db.query(models.MovimentacaoEstoque).join(
                models.Produto
            ).filter(
                models.MovimentacaoEstoque.id == movimentacao_id,
                models.Produto.empresa_id == empresa_id,
                models.MovimentacaoEstoque.status == 'PENDENTE'
            ).first()
            
            if not movimentacao:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Movimentação pendente não encontrada ou já foi processada."
                )
            
            movimentacao.status = 'REJEITADO'
            movimentacao.aprovado_por_id = aprovado_por_id
            movimentacao.data_aprovacao = datetime.utcnow()
            movimentacao.motivo_rejeicao = motivo_rejeicao
            
            db.commit()
            db.refresh(movimentacao)
            
            stock_operations_logger.info(
                f"[rejectMovimentacao] SUCCESS - movimentacao_id={movimentacao_id}, "
                f"aprovado_por_id={aprovado_por_id}, motivo={motivo_rejeicao}"
            )
            
            return movimentacao
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            stock_operations_logger.error(
                f"[rejectMovimentacao] ERROR - movimentacao_id={movimentacao_id}, error={str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao rejeitar movimentação: {str(e)}"
            )
    
    @staticmethod
    def edit_and_confirm_movimentacao(
        db: Session,
        movimentacao_id: int,
        aprovado_por_id: int,
        empresa_id: int,
        produto_id: Optional[int] = None,
        quantidade: Optional[float] = None,
        tipo_movimentacao: Optional[TipoMovimentacao] = None,
        motivo_movimentacao: Optional[MotivoMovimentacao] = None,
        observacao: Optional[str] = None,
        observacao_motivo: Optional[str] = None
    ) -> models.Produto:
        """Edita uma movimentação pendente e confirma aplicando ao estoque."""
        try:
            movimentacao = db.query(models.MovimentacaoEstoque).join(
                models.Produto
            ).filter(
                models.MovimentacaoEstoque.id == movimentacao_id,
                models.Produto.empresa_id == empresa_id,
                models.MovimentacaoEstoque.status == 'PENDENTE'
            ).first()
            
            if not movimentacao:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Movimentação pendente não encontrada ou já foi processada."
                )
            
            # Salvar dados antes da edição para auditoria
            dados_antes = {
                'produto_id': movimentacao.produto_id,
                'quantidade': movimentacao.quantidade,
                'tipo_movimentacao': movimentacao.tipo_movimentacao,
                'motivo_movimentacao': movimentacao.motivo_movimentacao,
                'observacao': movimentacao.observacao
            }
            movimentacao.dados_antes_edicao = json.dumps(dados_antes)
            
            # Aplicar edições
            produto_id_final = produto_id if produto_id is not None else movimentacao.produto_id
            quantidade_final = quantidade if quantidade is not None else movimentacao.quantidade
            tipo_final = tipo_movimentacao if tipo_movimentacao is not None else movimentacao.tipo_movimentacao
            motivo_final = motivo_movimentacao.value if motivo_movimentacao else movimentacao.motivo_movimentacao
            
            # Verificar se produto foi alterado
            if produto_id_final != movimentacao.produto_id:
                novo_produto = db.query(models.Produto).filter(
                    models.Produto.id == produto_id_final,
                    models.Produto.empresa_id == empresa_id
                ).first()
                if not novo_produto:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Novo produto não encontrado."
                    )
            
            produto = db.query(models.Produto).with_for_update().filter(
                models.Produto.id == produto_id_final,
                models.Produto.empresa_id == empresa_id
            ).first()
            
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produto não encontrado."
                )
            
            quantidade_antes = produto.quantidade_em_estoque
            
            # Aplicar movimentação ao estoque
            if tipo_final == 'SAIDA':
                if produto.quantidade_em_estoque < quantidade_final:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Estoque insuficiente. Disponível: {produto.quantidade_em_estoque}, Solicitado: {quantidade_final}"
                    )
                produto.quantidade_em_estoque -= quantidade_final
            else:
                produto.quantidade_em_estoque += quantidade_final
            
            quantidade_depois = produto.quantidade_em_estoque
            
            # Atualizar movimentação
            movimentacao.produto_id = produto_id_final
            movimentacao.quantidade = quantidade_final
            movimentacao.tipo_movimentacao = tipo_final
            movimentacao.motivo_movimentacao = motivo_final
            if observacao is not None:
                movimentacao.observacao = observacao
            movimentacao.observacao_motivo = observacao_motivo
            
            movimentacao.status = 'CONFIRMADO'
            movimentacao.aprovado_por_id = aprovado_por_id
            movimentacao.data_aprovacao = datetime.utcnow()
            movimentacao.quantidade_antes = quantidade_antes
            movimentacao.quantidade_depois = quantidade_depois
            
            # Salvar dados depois da edição
            dados_depois = {
                'produto_id': movimentacao.produto_id,
                'quantidade': movimentacao.quantidade,
                'tipo_movimentacao': movimentacao.tipo_movimentacao,
                'motivo_movimentacao': movimentacao.motivo_movimentacao,
                'observacao': movimentacao.observacao
            }
            movimentacao.dados_depois_edicao = json.dumps(dados_depois)
            
            db.commit()
            db.refresh(produto)
            db.refresh(movimentacao)
            
            stock_operations_logger.info(
                f"[editAndConfirmMovimentacao] SUCCESS - movimentacao_id={movimentacao_id}, "
                f"aprovado_por_id={aprovado_por_id}, estoque_antes={quantidade_antes}, "
                f"estoque_depois={quantidade_depois}"
            )
            
            return produto
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            stock_operations_logger.error(
                f"[editAndConfirmMovimentacao] ERROR - movimentacao_id={movimentacao_id}, error={str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao editar e confirmar movimentação: {str(e)}"
            )
