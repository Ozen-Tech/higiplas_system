#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço para cálculo de KPIs de compras.
Focado em gestão de estoque, reposição e eficiência de compras.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, case
import logging

from ..db import models

logger = logging.getLogger(__name__)


class ComprasKPIService:
    """Serviço para calcular KPIs de compras."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calcular_giro_estoque(
        self,
        produto_id: int,
        empresa_id: int,
        periodo_meses: int = 12
    ) -> Optional[Dict[str, Any]]:
        """
        Calcula o giro de estoque (rotatividade) de um produto.
        
        Args:
            produto_id: ID do produto
            empresa_id: ID da empresa
            periodo_meses: Período de análise em meses (padrão: 12)
        
        Returns:
            Dicionário com giro mensal, anual e dias de giro
        """
        try:
            data_limite = datetime.now() - timedelta(days=periodo_meses * 30)
            
            # Calcular vendas no período
            total_vendido = self.db.query(
                func.sum(models.HistoricoVendaCliente.quantidade_vendida)
            ).filter(
                models.HistoricoVendaCliente.produto_id == produto_id,
                models.HistoricoVendaCliente.empresa_id == empresa_id,
                models.HistoricoVendaCliente.data_venda >= data_limite
            ).scalar() or 0
            
            # Obter estoque atual
            produto = self.db.query(models.Produto).filter(
                models.Produto.id == produto_id,
                models.Produto.empresa_id == empresa_id
            ).first()
            
            if not produto:
                return None
            
            estoque_atual = produto.quantidade_em_estoque
            
            if estoque_atual == 0:
                return {
                    'produto_id': produto_id,
                    'produto_nome': produto.nome,
                    'giro_mensal': 0,
                    'giro_anual': 0,
                    'dias_giro': 0,
                    'estoque_atual': 0,
                    'total_vendido_periodo': total_vendido
                }
            
            # Calcular giro
            meses_analise = periodo_meses
            giro_mensal = total_vendido / meses_analise / estoque_atual if estoque_atual > 0 else 0
            giro_anual = giro_mensal * 12
            
            # Dias de giro (quanto tempo o estoque atual dura)
            demanda_media_diaria = total_vendido / (periodo_meses * 30) if periodo_meses > 0 else 0
            dias_giro = estoque_atual / demanda_media_diaria if demanda_media_diaria > 0 else 0
            
            return {
                'produto_id': produto_id,
                'produto_nome': produto.nome,
                'giro_mensal': round(giro_mensal, 2),
                'giro_anual': round(giro_anual, 2),
                'dias_giro': round(dias_giro, 1),
                'estoque_atual': estoque_atual,
                'total_vendido_periodo': total_vendido
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular giro de estoque: {str(e)}", exc_info=True)
            return None
    
    def calcular_dias_cobertura(
        self,
        produto_id: int,
        empresa_id: int,
        dias_analise: int = 90
    ) -> Optional[Dict[str, Any]]:
        """
        Calcula dias de cobertura de estoque disponível.
        
        Args:
            produto_id: ID do produto
            empresa_id: ID da empresa
            dias_analise: Período de análise em dias (padrão: 90)
        
        Returns:
            Dicionário com dias de cobertura e demanda média
        """
        try:
            data_limite = datetime.now() - timedelta(days=dias_analise)
            
            # Calcular demanda média diária
            total_vendido = self.db.query(
                func.sum(models.HistoricoVendaCliente.quantidade_vendida)
            ).filter(
                models.HistoricoVendaCliente.produto_id == produto_id,
                models.HistoricoVendaCliente.empresa_id == empresa_id,
                models.HistoricoVendaCliente.data_venda >= data_limite
            ).scalar() or 0
            
            demanda_media_diaria = total_vendido / dias_analise if dias_analise > 0 else 0
            
            # Obter estoque atual
            produto = self.db.query(models.Produto).filter(
                models.Produto.id == produto_id,
                models.Produto.empresa_id == empresa_id
            ).first()
            
            if not produto:
                return None
            
            estoque_atual = produto.quantidade_em_estoque
            
            # Calcular dias de cobertura
            dias_cobertura = estoque_atual / demanda_media_diaria if demanda_media_diaria > 0 else 0
            
            return {
                'produto_id': produto_id,
                'produto_nome': produto.nome,
                'dias_cobertura': round(dias_cobertura, 1),
                'demanda_media_diaria': round(demanda_media_diaria, 2),
                'estoque_atual': estoque_atual,
                'status': 'CRÍTICO' if dias_cobertura < 7 else 'BAIXO' if dias_cobertura < 14 else 'ADEQUADO'
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular dias de cobertura: {str(e)}", exc_info=True)
            return None
    
    def calcular_abc_curva(
        self,
        empresa_id: int,
        periodo_meses: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Classifica produtos pela curva ABC baseada em vendas.
        
        Args:
            empresa_id: ID da empresa
            periodo_meses: Período de análise em meses (padrão: 12)
        
        Returns:
            Lista de produtos classificados (A, B, C)
        """
        try:
            data_limite = datetime.now() - timedelta(days=periodo_meses * 30)
            
            # Calcular vendas por produto
            vendas_produtos = self.db.query(
                models.HistoricoVendaCliente.produto_id,
                func.sum(models.HistoricoVendaCliente.valor_total).label('valor_total_vendas')
            ).filter(
                models.HistoricoVendaCliente.empresa_id == empresa_id,
                models.HistoricoVendaCliente.data_venda >= data_limite
            ).group_by(
                models.HistoricoVendaCliente.produto_id
            ).order_by(desc('valor_total_vendas')).all()
            
            if not vendas_produtos:
                return []
            
            # Calcular totais
            total_vendas = sum(v.valor_total_vendas for v in vendas_produtos)
            
            # Calcular percentuais acumulados e classificar
            produtos_classificados = []
            acumulado = 0
            
            for venda in vendas_produtos:
                produto = self.db.query(models.Produto).filter(
                    models.Produto.id == venda.produto_id
                ).first()
                
                if not produto:
                    continue
                
                percentual_vendas = (venda.valor_total_vendas / total_vendas) * 100
                acumulado += percentual_vendas
                
                # Calcular percentual de estoque
                estoque_valor = produto.quantidade_em_estoque * (produto.preco_venda or 0)
                total_estoque_valor = self.db.query(
                    func.sum(models.Produto.quantidade_em_estoque * models.Produto.preco_venda)
                ).filter(
                    models.Produto.empresa_id == empresa_id
                ).scalar() or 1
                
                percentual_estoque = (estoque_valor / total_estoque_valor) * 100 if total_estoque_valor > 0 else 0
                
                # Classificação ABC
                if acumulado <= 80:
                    classificacao = 'A'
                elif acumulado <= 95:
                    classificacao = 'B'
                else:
                    classificacao = 'C'
                
                produtos_classificados.append({
                    'produto_id': produto.id,
                    'produto_nome': produto.nome,
                    'produto_codigo': produto.codigo,
                    'classificacao': classificacao,
                    'percentual_vendas': round(percentual_vendas, 2),
                    'percentual_estoque': round(percentual_estoque, 2),
                    'valor_total_vendas': float(venda.valor_total_vendas),
                    'percentual_acumulado': round(acumulado, 2)
                })
            
            return produtos_classificados
            
        except Exception as e:
            logger.error(f"Erro ao calcular curva ABC: {str(e)}", exc_info=True)
            return []
    
    def calcular_turnover_fornecedor(
        self,
        fornecedor_id: int,
        empresa_id: int,
        periodo_meses: int = 12
    ) -> Optional[Dict[str, Any]]:
        """
        Calcula rotatividade de compras por fornecedor.
        
        Args:
            fornecedor_id: ID do fornecedor
            empresa_id: ID da empresa
            periodo_meses: Período de análise em meses (padrão: 12)
        
        Returns:
            Dicionário com estatísticas do fornecedor
        """
        try:
            data_limite = datetime.now() - timedelta(days=periodo_meses * 30)
            
            # Obter produtos do fornecedor
            produtos_fornecedor = self.db.query(models.Produto).filter(
                models.Produto.fornecedor_id == fornecedor_id,
                models.Produto.empresa_id == empresa_id
            ).all()
            
            if not produtos_fornecedor:
                return None
            
            produto_ids = [p.id for p in produtos_fornecedor]
            
            # Calcular total de compras (entradas de estoque)
            total_entradas = self.db.query(
                func.sum(models.MovimentacaoEstoque.quantidade)
            ).filter(
                models.MovimentacaoEstoque.produto_id.in_(produto_ids),
                models.MovimentacaoEstoque.tipo_movimentacao == 'ENTRADA',
                models.MovimentacaoEstoque.origem == 'COMPRA',
                models.MovimentacaoEstoque.data_movimentacao >= data_limite
            ).scalar() or 0
            
            # Calcular número de ordens de compra
            numero_ordens = self.db.query(models.OrdemDeCompra).filter(
                models.OrdemDeCompra.fornecedor_id == fornecedor_id,
                models.OrdemDeCompra.data_criacao >= data_limite
            ).count()
            
            fornecedor = self.db.query(models.Fornecedor).filter(
                models.Fornecedor.id == fornecedor_id
            ).first()
            
            return {
                'fornecedor_id': fornecedor_id,
                'fornecedor_nome': fornecedor.nome if fornecedor else 'N/A',
                'total_entradas': total_entradas,
                'numero_ordens': numero_ordens,
                'media_por_ordem': round(total_entradas / numero_ordens, 2) if numero_ordens > 0 else 0,
                'produtos_fornecidos': len(produtos_fornecedor)
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular turnover de fornecedor: {str(e)}", exc_info=True)
            return None
    
    def calcular_previsao_compras(
        self,
        produto_id: int,
        empresa_id: int,
        dias_futuros: int = 30,
        lead_time_dias: int = 7
    ) -> Optional[Dict[str, Any]]:
        """
        Previsão de necessidade de compra baseada em demanda histórica.
        
        Args:
            produto_id: ID do produto
            empresa_id: ID da empresa
            dias_futuros: Período futuro para previsão (padrão: 30 dias)
            lead_time_dias: Lead time em dias (padrão: 7 dias)
        
        Returns:
            Dicionário com previsão de compra
        """
        try:
            # Calcular demanda média diária (últimos 90 dias)
            data_limite = datetime.now() - timedelta(days=90)
            
            total_vendido = self.db.query(
                func.sum(models.HistoricoVendaCliente.quantidade_vendida)
            ).filter(
                models.HistoricoVendaCliente.produto_id == produto_id,
                models.HistoricoVendaCliente.empresa_id == empresa_id,
                models.HistoricoVendaCliente.data_venda >= data_limite
            ).scalar() or 0
            
            demanda_media_diaria = total_vendido / 90 if total_vendido > 0 else 0
            
            # Obter estoque atual
            produto = self.db.query(models.Produto).filter(
                models.Produto.id == produto_id,
                models.Produto.empresa_id == empresa_id
            ).first()
            
            if not produto:
                return None
            
            estoque_atual = produto.quantidade_em_estoque
            
            # Calcular necessidade
            demanda_periodo = demanda_media_diaria * dias_futuros
            necessidade_bruta = demanda_periodo - estoque_atual
            
            # Adicionar margem de segurança e lead time
            necessidade_com_lead = necessidade_bruta + (demanda_media_diaria * lead_time_dias)
            quantidade_necessaria = max(0, int(necessidade_com_lead * 1.2))  # 20% de margem
            
            # Calcular custo estimado
            custo_estimado = quantidade_necessaria * (produto.preco_custo or 0)
            
            # Determinar urgência
            dias_cobertura = estoque_atual / demanda_media_diaria if demanda_media_diaria > 0 else 0
            if dias_cobertura < lead_time_dias:
                urgencia = 'CRÍTICA'
            elif dias_cobertura < (lead_time_dias + 7):
                urgencia = 'ALTA'
            elif dias_cobertura < (lead_time_dias + 14):
                urgencia = 'MÉDIA'
            else:
                urgencia = 'BAIXA'
            
            return {
                'produto_id': produto_id,
                'produto_nome': produto.nome,
                'quantidade_necessaria': quantidade_necessaria,
                'urgencia': urgencia,
                'custo_estimado': round(custo_estimado, 2),
                'dias_cobertura_atual': round(dias_cobertura, 1),
                'demanda_media_diaria': round(demanda_media_diaria, 2)
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular previsão de compras: {str(e)}", exc_info=True)
            return None
    
    def calcular_custo_estoque_parado(
        self,
        empresa_id: int,
        dias_sem_movimento: int = 90
    ) -> Dict[str, Any]:
        """
        Calcula custo de produtos parados (sem movimento).
        
        Args:
            empresa_id: ID da empresa
            dias_sem_movimento: Dias sem movimento para considerar parado (padrão: 90)
        
        Returns:
            Dicionário com produtos parados e custo total
        """
        try:
            data_limite = datetime.now() - timedelta(days=dias_sem_movimento)
            
            # Obter todos os produtos da empresa
            produtos = self.db.query(models.Produto).filter(
                models.Produto.empresa_id == empresa_id,
                models.Produto.quantidade_em_estoque > 0
            ).all()
            
            produtos_parados = []
            custo_total_parado = 0
            
            for produto in produtos:
                # Verificar última movimentação
                ultima_movimentacao = self.db.query(models.MovimentacaoEstoque).filter(
                    models.MovimentacaoEstoque.produto_id == produto.id
                ).order_by(desc(models.MovimentacaoEstoque.data_movimentacao)).first()
                
                if not ultima_movimentacao or ultima_movimentacao.data_movimentacao < data_limite:
                    custo_produto_parado = produto.quantidade_em_estoque * (produto.preco_custo or 0)
                    custo_total_parado += custo_produto_parado
                    
                    produtos_parados.append({
                        'produto_id': produto.id,
                        'produto_nome': produto.nome,
                        'produto_codigo': produto.codigo,
                        'quantidade_estoque': produto.quantidade_em_estoque,
                        'custo_total': round(custo_produto_parado, 2),
                        'ultima_movimentacao': ultima_movimentacao.data_movimentacao.isoformat() if ultima_movimentacao else None
                    })
            
            return {
                'total_produtos_parados': len(produtos_parados),
                'custo_total_parado': round(custo_total_parado, 2),
                'produtos_parados': produtos_parados[:20]  # Limitar a 20 para não sobrecarregar
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular custo de estoque parado: {str(e)}", exc_info=True)
            return {
                'total_produtos_parados': 0,
                'custo_total_parado': 0,
                'produtos_parados': []
            }
    
    def calcular_eficiencia_compras(
        self,
        empresa_id: int,
        periodo_meses: int = 6
    ) -> Dict[str, Any]:
        """
        Calcula taxa de acerto nas compras (produtos comprados vs produtos vendidos).
        
        Args:
            empresa_id: ID da empresa
            periodo_meses: Período de análise em meses (padrão: 6)
        
        Returns:
            Dicionário com métricas de eficiência
        """
        try:
            data_limite = datetime.now() - timedelta(days=periodo_meses * 30)
            
            # Calcular produtos comprados (entradas) - filtrar por produtos da empresa
            produto_ids_empresa = [
                p.id for p in self.db.query(models.Produto.id).filter(
                    models.Produto.empresa_id == empresa_id
                ).all()
            ]
            
            produtos_comprados = self.db.query(
                func.count(func.distinct(models.MovimentacaoEstoque.produto_id))
            ).filter(
                models.MovimentacaoEstoque.tipo_movimentacao == 'ENTRADA',
                models.MovimentacaoEstoque.origem == 'COMPRA',
                models.MovimentacaoEstoque.produto_id.in_(produto_ids_empresa),
                models.MovimentacaoEstoque.data_movimentacao >= data_limite
            ).scalar() or 0
            
            # Calcular produtos vendidos
            produtos_vendidos = self.db.query(
                func.count(func.distinct(models.HistoricoVendaCliente.produto_id))
            ).filter(
                models.HistoricoVendaCliente.empresa_id == empresa_id,
                models.HistoricoVendaCliente.data_venda >= data_limite
            ).scalar() or 0
            
            # Calcular taxa de acerto
            taxa_acerto = (produtos_vendidos / produtos_comprados * 100) if produtos_comprados > 0 else 0
            
            return {
                'produtos_comprados': produtos_comprados,
                'produtos_vendidos': produtos_vendidos,
                'taxa_acerto_percentual': round(taxa_acerto, 2),
                'periodo_meses': periodo_meses
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular eficiência de compras: {str(e)}", exc_info=True)
            return {
                'produtos_comprados': 0,
                'produtos_vendidos': 0,
                'taxa_acerto_percentual': 0,
                'periodo_meses': periodo_meses
            }
    
    def calcular_todos_kpis(
        self,
        empresa_id: int,
        periodo_meses: int = 12
    ) -> Dict[str, Any]:
        """
        Calcula todos os KPIs de compras de uma vez.
        
        Args:
            empresa_id: ID da empresa
            periodo_meses: Período de análise em meses (padrão: 12)
        
        Returns:
            Dicionário completo com todos os KPIs
        """
        try:
            # Curva ABC
            abc_curva = self.calcular_abc_curva(empresa_id, periodo_meses)
            
            # Eficiência de compras
            eficiencia = self.calcular_eficiencia_compras(empresa_id, periodo_meses // 2)
            
            # Custo de estoque parado
            estoque_parado = self.calcular_custo_estoque_parado(empresa_id)
            
            return {
                'empresa_id': empresa_id,
                'periodo_meses': periodo_meses,
                'data_calculo': datetime.now().isoformat(),
                'abc_curva': abc_curva,
                'eficiencia_compras': eficiencia,
                'estoque_parado': estoque_parado
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular todos os KPIs: {str(e)}", exc_info=True)
            return {
                'empresa_id': empresa_id,
                'erro': str(e)
            }

