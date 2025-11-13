#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço para cálculo de KPIs de clientes.
Utilizado para análise de comportamento, previsão de demanda e estratégias de crescimento.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
import logging

from ..db import models

logger = logging.getLogger(__name__)


class ClienteKPIService:
    """Serviço para calcular KPIs de clientes."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calcular_ticket_medio(
        self,
        cliente_id: int,
        dias_periodo: int = 90
    ) -> Optional[float]:
        """
        Calcula o ticket médio (valor médio por pedido) do cliente.
        
        Args:
            cliente_id: ID do cliente
            dias_periodo: Período em dias para análise (padrão: 90 dias)
        
        Returns:
            Ticket médio ou None se não houver histórico
        """
        try:
            data_limite = datetime.now() - timedelta(days=dias_periodo)
            
            # Agrupar por orcamento_id para calcular ticket médio
            resultados = self.db.query(
                models.HistoricoVendaCliente.orcamento_id,
                func.sum(models.HistoricoVendaCliente.valor_total).label('valor_total_pedido')
            ).filter(
                models.HistoricoVendaCliente.cliente_id == cliente_id,
                models.HistoricoVendaCliente.data_venda >= data_limite
            ).group_by(
                models.HistoricoVendaCliente.orcamento_id
            ).all()
            
            if not resultados:
                return None
            
            total_valor = sum(r.valor_total_pedido for r in resultados)
            numero_pedidos = len(resultados)
            
            return round(total_valor / numero_pedidos, 2)
            
        except Exception as e:
            logger.error(f"Erro ao calcular ticket médio: {str(e)}", exc_info=True)
            return None
    
    def calcular_frequencia_compras(
        self,
        cliente_id: int,
        dias_periodo: int = 90
    ) -> Optional[float]:
        """
        Calcula a frequência média de compras (dias médios entre compras).
        
        Args:
            cliente_id: ID do cliente
            dias_periodo: Período em dias para análise (padrão: 90 dias)
        
        Returns:
            Dias médios entre compras ou None se não houver histórico suficiente
        """
        try:
            data_limite = datetime.now() - timedelta(days=dias_periodo)
            
            # Obter datas únicas de pedidos ordenadas
            datas_pedidos = self.db.query(
                func.date(models.HistoricoVendaCliente.data_venda).label('data_pedido')
            ).filter(
                models.HistoricoVendaCliente.cliente_id == cliente_id,
                models.HistoricoVendaCliente.data_venda >= data_limite
            ).distinct().order_by(
                desc('data_pedido')
            ).all()
            
            if len(datas_pedidos) < 2:
                return None
            
            # Calcular diferenças entre compras consecutivas
            diferencas = []
            for i in range(len(datas_pedidos) - 1):
                data_atual = datas_pedidos[i].data_pedido
                data_anterior = datas_pedidos[i + 1].data_pedido
                diferenca = (data_atual - data_anterior).days
                diferencas.append(diferenca)
            
            if not diferencas:
                return None
            
            return round(sum(diferencas) / len(diferencas), 1)
            
        except Exception as e:
            logger.error(f"Erro ao calcular frequência de compras: {str(e)}", exc_info=True)
            return None
    
    def produtos_mais_comprados(
        self,
        cliente_id: int,
        limite: int = 10,
        dias_periodo: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Retorna os produtos mais comprados pelo cliente.
        
        Args:
            cliente_id: ID do cliente
            limite: Número de produtos para retornar (padrão: 10)
            dias_periodo: Período em dias para análise (padrão: 90 dias)
        
        Returns:
            Lista de dicionários com informações dos produtos
        """
        try:
            data_limite = datetime.now() - timedelta(days=dias_periodo)
            
            resultados = self.db.query(
                models.HistoricoVendaCliente.produto_id,
                func.sum(models.HistoricoVendaCliente.quantidade_vendida).label('quantidade_total'),
                func.max(models.HistoricoVendaCliente.data_venda).label('ultima_compra'),
                func.count(models.HistoricoVendaCliente.orcamento_id.distinct()).label('numero_pedidos')
            ).filter(
                models.HistoricoVendaCliente.cliente_id == cliente_id,
                models.HistoricoVendaCliente.data_venda >= data_limite
            ).group_by(
                models.HistoricoVendaCliente.produto_id
            ).order_by(
                desc('quantidade_total')
            ).limit(limite).all()
            
            produtos = []
            for resultado in resultados:
                produto = self.db.query(models.Produto).filter(
                    models.Produto.id == resultado.produto_id
                ).first()
                
                if produto:
                    produtos.append({
                        'produto_id': resultado.produto_id,
                        'produto_nome': produto.nome,
                        'produto_codigo': produto.codigo,
                        'quantidade_total': int(resultado.quantidade_total),
                        'ultima_compra': resultado.ultima_compra.isoformat() if resultado.ultima_compra else None,
                        'numero_pedidos': resultado.numero_pedidos
                    })
            
            return produtos
            
        except Exception as e:
            logger.error(f"Erro ao obter produtos mais comprados: {str(e)}", exc_info=True)
            return []
    
    def previsao_demanda(
        self,
        cliente_id: int,
        produto_id: int,
        dias_futuros: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Previsão de demanda baseada em histórico sazonal.
        
        Args:
            cliente_id: ID do cliente
            produto_id: ID do produto
            dias_futuros: Período futuro para previsão (padrão: 30 dias)
        
        Returns:
            Dicionário com previsão: {quantidade_prevista, confianca, periodo}
        """
        try:
            # Analisar últimos 6 meses para detectar padrões
            data_limite = datetime.now() - timedelta(days=180)
            
            historicos = self.db.query(models.HistoricoVendaCliente).filter(
                models.HistoricoVendaCliente.cliente_id == cliente_id,
                models.HistoricoVendaCliente.produto_id == produto_id,
                models.HistoricoVendaCliente.data_venda >= data_limite
            ).order_by(desc(models.HistoricoVendaCliente.data_venda)).all()
            
            if not historicos:
                return None
            
            # Calcular média mensal
            quantidade_total = sum(h.quantidade_vendida for h in historicos)
            meses_analise = max(1, (datetime.now() - historicos[-1].data_venda).days / 30)
            media_mensal = quantidade_total / meses_analise
            
            # Previsão para o período futuro
            meses_futuros = dias_futuros / 30
            quantidade_prevista = round(media_mensal * meses_futuros, 0)
            
            # Calcular confiança baseada na quantidade de dados
            num_registros = len(historicos)
            if num_registros >= 10:
                confianca = "ALTA"
            elif num_registros >= 5:
                confianca = "MÉDIA"
            else:
                confianca = "BAIXA"
            
            return {
                'quantidade_prevista': int(quantidade_prevista),
                'confianca': confianca,
                'periodo_dias': dias_futuros,
                'media_mensal': round(media_mensal, 2),
                'registros_analisados': num_registros
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular previsão de demanda: {str(e)}", exc_info=True)
            return None
    
    def calcular_todos_kpis(
        self,
        cliente_id: int,
        dias_periodo: int = 90
    ) -> Dict[str, Any]:
        """
        Calcula todos os KPIs do cliente de uma vez.
        
        Args:
            cliente_id: ID do cliente
            dias_periodo: Período em dias para análise (padrão: 90 dias)
        
        Returns:
            Dicionário completo com todos os KPIs
        """
        try:
            data_limite = datetime.now() - timedelta(days=dias_periodo)
            
            # Estatísticas básicas
            total_vendido = self.db.query(
                func.sum(models.HistoricoVendaCliente.valor_total)
            ).filter(
                models.HistoricoVendaCliente.cliente_id == cliente_id,
                models.HistoricoVendaCliente.data_venda >= data_limite
            ).scalar() or 0
            
            numero_pedidos = self.db.query(
                func.count(func.distinct(models.HistoricoVendaCliente.orcamento_id))
            ).filter(
                models.HistoricoVendaCliente.cliente_id == cliente_id,
                models.HistoricoVendaCliente.data_venda >= data_limite
            ).scalar() or 0
            
            # Calcular KPIs
            ticket_medio = self.calcular_ticket_medio(cliente_id, dias_periodo)
            frequencia = self.calcular_frequencia_compras(cliente_id, dias_periodo)
            produtos_mais_comprados_list = self.produtos_mais_comprados(cliente_id, limite=10, dias_periodo=dias_periodo)
            
            return {
                'cliente_id': cliente_id,
                'periodo_dias': dias_periodo,
                'total_vendido': float(total_vendido),
                'numero_pedidos': numero_pedidos,
                'ticket_medio': ticket_medio,
                'frequencia_compras_dias': frequencia,
                'produtos_mais_comprados': produtos_mais_comprados_list,
                'data_calculo': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular todos os KPIs: {str(e)}", exc_info=True)
            return {
                'cliente_id': cliente_id,
                'erro': str(e)
            }

