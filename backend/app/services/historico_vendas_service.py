#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço para gerenciamento de histórico de vendas por vendedor-cliente-produto.
Utilizado para sugestões inteligentes e análise de KPIs.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import logging

from ..db import models

logger = logging.getLogger(__name__)


class HistoricoVendasService:
    """Serviço para gerenciar histórico de vendas por vendedor-cliente-produto."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def salvar_historico_venda(
        self,
        vendedor_id: int,
        cliente_id: int,
        produto_id: int,
        orcamento_id: int,
        empresa_id: int,
        quantidade: int,
        preco_unitario: float,
        valor_total: float,
        data_venda: Optional[datetime] = None
    ) -> models.HistoricoVendaCliente:
        """
        Salva um registro de histórico de venda.
        
        Args:
            vendedor_id: ID do vendedor
            cliente_id: ID do cliente
            produto_id: ID do produto
            orcamento_id: ID do orçamento
            empresa_id: ID da empresa
            quantidade: Quantidade vendida
            preco_unitario: Preço unitário vendido
            valor_total: Valor total da venda
            data_venda: Data da venda (opcional, usa now() se não fornecido)
        
        Returns:
            Registro de histórico criado
        """
        try:
            historico = models.HistoricoVendaCliente(
                vendedor_id=vendedor_id,
                cliente_id=cliente_id,
                produto_id=produto_id,
                orcamento_id=orcamento_id,
                empresa_id=empresa_id,
                quantidade_vendida=quantidade,
                preco_unitario_vendido=preco_unitario,
                valor_total=valor_total,
                data_venda=data_venda or datetime.now()
            )
            
            self.db.add(historico)
            self.db.flush()
            
            logger.info(
                f"Histórico de venda salvo: vendedor={vendedor_id}, cliente={cliente_id}, produto={produto_id}, orcamento={orcamento_id}"
            )
            
            return historico
            
        except Exception as e:
            logger.error(f"Erro ao salvar histórico de venda: {str(e)}", exc_info=True)
            raise
    
    def obter_ultimo_preco(
        self,
        vendedor_id: int,
        cliente_id: int,
        produto_id: int
    ) -> Optional[float]:
        """
        Retorna o último preço vendido para vendedor-cliente-produto.
        
        Args:
            vendedor_id: ID do vendedor
            cliente_id: ID do cliente
            produto_id: ID do produto
        
        Returns:
            Último preço unitário vendido ou None se não houver histórico
        """
        try:
            historico = self.db.query(models.HistoricoVendaCliente).filter(
                models.HistoricoVendaCliente.vendedor_id == vendedor_id,
                models.HistoricoVendaCliente.cliente_id == cliente_id,
                models.HistoricoVendaCliente.produto_id == produto_id
            ).order_by(desc(models.HistoricoVendaCliente.data_venda)).first()
            
            if historico:
                return historico.preco_unitario_vendido
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter último preço: {str(e)}", exc_info=True)
            return None
    
    def obter_media_quantidade(
        self,
        vendedor_id: int,
        cliente_id: int,
        produto_id: int,
        limite: int = 5
    ) -> Optional[float]:
        """
        Calcula a média dos últimos N pedidos (padrão: 5).
        Se houver menos de N pedidos, retorna a quantidade do último pedido.
        
        Args:
            vendedor_id: ID do vendedor
            cliente_id: ID do cliente
            produto_id: ID do produto
            limite: Número de pedidos para calcular média (padrão: 5)
        
        Returns:
            Média de quantidade ou quantidade do último pedido se < limite
        """
        try:
            historicos = self.db.query(models.HistoricoVendaCliente).filter(
                models.HistoricoVendaCliente.vendedor_id == vendedor_id,
                models.HistoricoVendaCliente.cliente_id == cliente_id,
                models.HistoricoVendaCliente.produto_id == produto_id
            ).order_by(desc(models.HistoricoVendaCliente.data_venda)).limit(limite).all()
            
            if not historicos:
                return None
            
            # Se houver menos de 'limite' pedidos, retorna a quantidade do último
            if len(historicos) < limite:
                return float(historicos[0].quantidade_vendida)
            
            # Calcula média dos últimos N pedidos
            total_quantidade = sum(h.quantidade_vendida for h in historicos)
            media = total_quantidade / len(historicos)
            
            return round(media, 2)
            
        except Exception as e:
            logger.error(f"Erro ao calcular média de quantidade: {str(e)}", exc_info=True)
            return None
    
    def obter_historico_completo(
        self,
        cliente_id: Optional[int] = None,
        vendedor_id: Optional[int] = None,
        produto_id: Optional[int] = None,
        empresa_id: Optional[int] = None,
        limite: int = 100
    ) -> List[models.HistoricoVendaCliente]:
        """
        Retorna histórico completo com filtros opcionais.
        
        Args:
            cliente_id: Filtrar por cliente (opcional)
            vendedor_id: Filtrar por vendedor (opcional)
            produto_id: Filtrar por produto (opcional)
            empresa_id: Filtrar por empresa (opcional)
            limite: Limite de resultados (padrão: 100)
        
        Returns:
            Lista de registros de histórico
        """
        try:
            query = self.db.query(models.HistoricoVendaCliente)
            
            if cliente_id:
                query = query.filter(models.HistoricoVendaCliente.cliente_id == cliente_id)
            if vendedor_id:
                query = query.filter(models.HistoricoVendaCliente.vendedor_id == vendedor_id)
            if produto_id:
                query = query.filter(models.HistoricoVendaCliente.produto_id == produto_id)
            if empresa_id:
                query = query.filter(models.HistoricoVendaCliente.empresa_id == empresa_id)
            
            return query.order_by(desc(models.HistoricoVendaCliente.data_venda)).limit(limite).all()
            
        except Exception as e:
            logger.error(f"Erro ao obter histórico completo: {str(e)}", exc_info=True)
            return []
    
    def obter_sugestoes_cliente(
        self,
        cliente_id: int,
        vendedor_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retorna sugestões de preço e quantidade para todos os produtos já vendidos ao cliente.
        
        Args:
            cliente_id: ID do cliente
            vendedor_id: ID do vendedor (opcional, se fornecido filtra por vendedor)
        
        Returns:
            Lista de dicionários com sugestões: {produto_id, ultimo_preco, quantidade_sugerida, historico_disponivel}
        """
        try:
            query = self.db.query(
                models.HistoricoVendaCliente.produto_id,
                func.max(models.HistoricoVendaCliente.data_venda).label('ultima_venda')
            ).filter(
                models.HistoricoVendaCliente.cliente_id == cliente_id
            )
            
            if vendedor_id:
                query = query.filter(models.HistoricoVendaCliente.vendedor_id == vendedor_id)
            
            produtos_vendidos = query.group_by(models.HistoricoVendaCliente.produto_id).all()
            
            sugestoes = []
            for produto_vendido in produtos_vendidos:
                produto_id = produto_vendido.produto_id
                
                # Obter último preço
                filtro = {
                    'cliente_id': cliente_id,
                    'produto_id': produto_id
                }
                if vendedor_id:
                    filtro['vendedor_id'] = vendedor_id
                
                ultimo_historico = self.db.query(models.HistoricoVendaCliente).filter_by(**filtro).order_by(
                    desc(models.HistoricoVendaCliente.data_venda)
                ).first()
                
                if ultimo_historico:
                    ultimo_preco = ultimo_historico.preco_unitario_vendido
                    
                    # Calcular média de quantidade
                    quantidade_sugerida = self.obter_media_quantidade(
                        vendedor_id=ultimo_historico.vendedor_id,
                        cliente_id=cliente_id,
                        produto_id=produto_id
                    )
                    
                    sugestoes.append({
                        'produto_id': produto_id,
                        'ultimo_preco': ultimo_preco,
                        'quantidade_sugerida': quantidade_sugerida or ultimo_historico.quantidade_vendida,
                        'historico_disponivel': True
                    })
            
            return sugestoes
            
        except Exception as e:
            logger.error(f"Erro ao obter sugestões do cliente: {str(e)}", exc_info=True)
            return []

