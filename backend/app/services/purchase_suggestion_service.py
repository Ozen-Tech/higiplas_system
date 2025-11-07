#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço para cálculo de sugestões de compra baseado em análise de demanda histórica.
Utiliza movimentações de saída (vendas) para calcular estoque mínimo e quantidades de compra.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import logging

from ..db import models

logger = logging.getLogger(__name__)


class PurchaseSuggestionService:
    """Serviço para cálculo de sugestões de compra baseado em demanda real."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_daily_demand(
        self,
        produto_id: int,
        days_analysis: int = 90
    ) -> Dict[str, Any]:
        """
        Calcula a demanda média diária de um produto baseado em movimentações de saída.
        
        Args:
            produto_id: ID do produto
            days_analysis: Período de análise em dias (padrão 90 dias)
        
        Returns:
            Dict com estatísticas de demanda
        """
        data_limite = datetime.now() - timedelta(days=days_analysis)
        
        # Busca movimentações de saída do produto
        saidas = self.db.query(models.MovimentacaoEstoque).filter(
            models.MovimentacaoEstoque.produto_id == produto_id,
            models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
            models.MovimentacaoEstoque.data_movimentacao >= data_limite
        ).all()
        
        if not saidas:
            return {
                'total_vendido': 0,
                'numero_vendas': 0,
                'demanda_media_diaria': 0,
                'demanda_maxima_diaria': 0,
                'dias_com_vendas': 0,
                'tem_historico_suficiente': False
            }
        
        # Calcula estatísticas
        total_vendido = sum(saida.quantidade for saida in saidas)
        numero_vendas = len(saidas)
        demanda_media_diaria = total_vendido / days_analysis
        
        # Agrupa vendas por dia para calcular variabilidade
        vendas_por_dia = {}
        for saida in saidas:
            data_str = saida.data_movimentacao.date().isoformat()
            if data_str not in vendas_por_dia:
                vendas_por_dia[data_str] = 0
            vendas_por_dia[data_str] += saida.quantidade
        
        demanda_maxima_diaria = max(vendas_por_dia.values()) if vendas_por_dia else 0
        dias_com_vendas = len(vendas_por_dia)
        
        # Valida histórico suficiente (mínimo 2 vendas)
        tem_historico_suficiente = numero_vendas >= 2
        
        return {
            'total_vendido': total_vendido,
            'numero_vendas': numero_vendas,
            'demanda_media_diaria': round(demanda_media_diaria, 2),
            'demanda_maxima_diaria': demanda_maxima_diaria,
            'dias_com_vendas': dias_com_vendas,
            'tem_historico_suficiente': tem_historico_suficiente
        }
    
    def calculate_minimum_stock(
        self,
        demanda_media_diaria: float,
        lead_time_days: int = 7,
        safety_margin: float = 1.2
    ) -> int:
        """
        Calcula estoque mínimo baseado em demanda e lead time.
        
        Args:
            demanda_media_diaria: Demanda média diária do produto
            lead_time_days: Tempo de reposição em dias (padrão 7 dias)
            safety_margin: Margem de segurança (padrão 1.2 = 20%)
        
        Returns:
            Estoque mínimo calculado
        """
        if demanda_media_diaria <= 0:
            return 0
        
        # Fórmula: (Demanda média diária × Lead time) × Margem de segurança
        estoque_minimo = (demanda_media_diaria * lead_time_days) * safety_margin
        
        # Garantir valor mínimo de 1
        return max(1, int(estoque_minimo))
    
    def calculate_purchase_quantity(
        self,
        demanda_media_diaria: float,
        estoque_atual: int,
        estoque_minimo_calculado: int,
        coverage_days: int = 14,
        additional_safety_margin: float = 1.15
    ) -> int:
        """
        Calcula quantidade de compra sugerida para 14 dias de cobertura + margem.
        
        Args:
            demanda_media_diaria: Demanda média diária do produto
            estoque_atual: Estoque atual do produto
            estoque_minimo_calculado: Estoque mínimo calculado
            coverage_days: Dias de cobertura desejados (padrão 14 dias)
            additional_safety_margin: Margem de segurança adicional (padrão 1.15 = 15%)
        
        Returns:
            Quantidade sugerida de compra
        """
        if demanda_media_diaria <= 0:
            return 0
        
        # Quantidade necessária para 14 dias com margem de segurança
        quantidade_necessaria_14_dias = (demanda_media_diaria * coverage_days) * additional_safety_margin
        
        # Estoque ideal = estoque mínimo + quantidade para 14 dias
        estoque_ideal = estoque_minimo_calculado + int(quantidade_necessaria_14_dias)
        
        # Quantidade a comprar = Estoque ideal - Estoque atual
        quantidade_sugerida = estoque_ideal - estoque_atual
        
        # Garantir que seja sempre positiva e suficiente
        quantidade_sugerida = max(0, int(quantidade_sugerida))
        
        # Garantir quantidade mínima suficiente para repor até o mínimo + 14 dias
        if estoque_atual < estoque_minimo_calculado:
            deficit_minimo = estoque_minimo_calculado - estoque_atual
            quantidade_para_14_dias = int((demanda_media_diaria * coverage_days) * additional_safety_margin)
            quantidade_sugerida = max(quantidade_sugerida, deficit_minimo + quantidade_para_14_dias)
        
        return quantidade_sugerida
    
    def get_purchase_suggestions(
        self,
        empresa_id: int,
        days_analysis: int = 90,
        lead_time_days: int = 7,
        coverage_days: int = 14,
        min_sales_threshold: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Retorna lista de produtos que precisam de compra com quantidades sugeridas.
        
        Args:
            empresa_id: ID da empresa
            days_analysis: Período de análise em dias (padrão 90 dias)
            lead_time_days: Lead time em dias (padrão 7 dias)
            coverage_days: Dias de cobertura para compra (padrão 14 dias)
            min_sales_threshold: Número mínimo de vendas para considerar histórico suficiente
        
        Returns:
            Lista de sugestões de compra
        """
        data_limite = datetime.now() - timedelta(days=days_analysis)
        
        # Query para buscar produtos com movimentações de saída
        query = text("""
            SELECT 
                p.id as produto_id,
                p.nome as produto_nome,
                p.codigo,
                p.categoria,
                p.estoque_minimo as estoque_minimo_atual,
                p.quantidade_em_estoque,
                p.preco_custo,
                p.preco_venda,
                p.fornecedor_id,
                COALESCE(SUM(m.quantidade), 0) as total_vendido,
                COUNT(m.id) as numero_vendas
            FROM produtos p
            LEFT JOIN movimentacoes_estoque m ON p.id = m.produto_id 
                AND m.tipo_movimentacao = 'SAIDA'
                AND m.data_movimentacao >= :data_limite
            WHERE p.empresa_id = :empresa_id
            GROUP BY p.id, p.nome, p.codigo, p.categoria, p.estoque_minimo, 
                     p.quantidade_em_estoque, p.preco_custo, p.preco_venda, p.fornecedor_id
            HAVING COUNT(m.id) >= :min_sales_threshold
            ORDER BY 
                CASE 
                    WHEN p.quantidade_em_estoque <= 0 THEN 1
                    WHEN p.quantidade_em_estoque < p.estoque_minimo THEN 2
                    ELSE 3
                END,
                p.quantidade_em_estoque ASC
        """)
        
        result = self.db.execute(query, {
            'empresa_id': empresa_id,
            'data_limite': data_limite,
            'min_sales_threshold': min_sales_threshold
        })
        
        suggestions = []
        
        for row in result:
            produto_id = row.produto_id
            estoque_atual = row.quantidade_em_estoque or 0
            
            # Calcula demanda
            demanda_info = self.calculate_daily_demand(produto_id, days_analysis)
            
            if not demanda_info['tem_historico_suficiente']:
                continue
            
            demanda_media_diaria = demanda_info['demanda_media_diaria']
            
            # Calcula estoque mínimo
            estoque_minimo_calculado = self.calculate_minimum_stock(
                demanda_media_diaria,
                lead_time_days,
                safety_margin=1.2
            )
            
            # Verifica se precisa de compra (estoque atual < estoque mínimo)
            if estoque_atual >= estoque_minimo_calculado:
                continue
            
            # Calcula quantidade de compra sugerida
            quantidade_sugerida = self.calculate_purchase_quantity(
                demanda_media_diaria,
                estoque_atual,
                estoque_minimo_calculado,
                coverage_days,
                additional_safety_margin=1.15
            )
            
            if quantidade_sugerida <= 0:
                continue
            
            # Calcula dias de cobertura atual
            dias_cobertura_atual = estoque_atual / demanda_media_diaria if demanda_media_diaria > 0 else 0
            
            # Determina status
            if estoque_atual <= 0:
                status = 'CRÍTICO'
            elif dias_cobertura_atual < lead_time_days:
                status = 'CRÍTICO'
            elif dias_cobertura_atual < (lead_time_days * 2):
                status = 'BAIXO'
            else:
                status = 'ADEQUADO'
            
            # Busca fornecedor se existir
            fornecedor_nome = None
            if row.fornecedor_id:
                fornecedor = self.db.query(models.Fornecedor).filter(
                    models.Fornecedor.id == row.fornecedor_id
                ).first()
                if fornecedor:
                    fornecedor_nome = fornecedor.nome
            
            suggestion = {
                'produto_id': produto_id,
                'produto_nome': row.produto_nome,
                'codigo': row.codigo,
                'categoria': row.categoria,
                'estoque_atual': estoque_atual,
                'estoque_minimo_atual': row.estoque_minimo_atual or 0,
                'estoque_minimo_calculado': estoque_minimo_calculado,
                'demanda_media_diaria': demanda_media_diaria,
                'demanda_maxima_diaria': demanda_info['demanda_maxima_diaria'],
                'total_vendido_periodo': demanda_info['total_vendido'],
                'numero_vendas': demanda_info['numero_vendas'],
                'dias_com_vendas': demanda_info['dias_com_vendas'],
                'dias_cobertura_atual': round(dias_cobertura_atual, 1),
                'quantidade_sugerida': quantidade_sugerida,
                'status': status,
                'tem_historico_suficiente': True,
                'fornecedor_id': row.fornecedor_id,
                'fornecedor_nome': fornecedor_nome,
                'preco_custo': row.preco_custo,
                'preco_venda': row.preco_venda,
                'valor_estimado_compra': round(quantidade_sugerida * (row.preco_custo or 0), 2),
                'periodo_analise_dias': days_analysis,
                'lead_time_dias': lead_time_days,
                'coverage_days': coverage_days
            }
            
            suggestions.append(suggestion)
        
        # Ordena por prioridade (CRÍTICO primeiro, depois por dias de cobertura)
        suggestions.sort(key=lambda x: (
            0 if x['status'] == 'CRÍTICO' else 1 if x['status'] == 'BAIXO' else 2,
            x['dias_cobertura_atual']
        ))
        
        return suggestions
    
    def get_product_analysis(
        self,
        produto_id: int,
        empresa_id: int,
        days_analysis: int = 90,
        lead_time_days: int = 7,
        coverage_days: int = 14
    ) -> Dict[str, Any]:
        """
        Retorna análise completa de um produto específico.
        
        Args:
            produto_id: ID do produto
            empresa_id: ID da empresa
            days_analysis: Período de análise em dias
            lead_time_days: Lead time em dias
            coverage_days: Dias de cobertura para compra
        
        Returns:
            Dict com análise completa do produto
        """
        # Verifica se produto existe e pertence à empresa
        produto = self.db.query(models.Produto).filter(
            models.Produto.id == produto_id,
            models.Produto.empresa_id == empresa_id
        ).first()
        
        if not produto:
            return {'erro': 'Produto não encontrado'}
        
        estoque_atual = produto.quantidade_em_estoque or 0
        
        # Calcula demanda
        demanda_info = self.calculate_daily_demand(produto_id, days_analysis)
        demanda_media_diaria = demanda_info['demanda_media_diaria']
        
        # Calcula estoque mínimo
        estoque_minimo_calculado = self.calculate_minimum_stock(
            demanda_media_diaria,
            lead_time_days,
            safety_margin=1.2
        ) if demanda_info['tem_historico_suficiente'] else (produto.estoque_minimo or 5)
        
        # Calcula quantidade de compra se necessário
        quantidade_sugerida = 0
        precisa_compra = False
        
        if demanda_info['tem_historico_suficiente'] and estoque_atual < estoque_minimo_calculado:
            precisa_compra = True
            quantidade_sugerida = self.calculate_purchase_quantity(
                demanda_media_diaria,
                estoque_atual,
                estoque_minimo_calculado,
                coverage_days,
                additional_safety_margin=1.15
            )
        
        # Calcula dias de cobertura
        dias_cobertura_atual = estoque_atual / demanda_media_diaria if demanda_media_diaria > 0 else float('inf')
        
        # Determina status
        if not demanda_info['tem_historico_suficiente']:
            status = 'SEM_HISTORICO'
        elif estoque_atual <= 0:
            status = 'CRÍTICO'
        elif dias_cobertura_atual < lead_time_days:
            status = 'CRÍTICO'
        elif dias_cobertura_atual < (lead_time_days * 2):
            status = 'BAIXO'
        elif estoque_atual < estoque_minimo_calculado:
            status = 'BAIXO'
        else:
            status = 'ADEQUADO'
        
        # Busca fornecedor
        fornecedor_nome = None
        if produto.fornecedor_id:
            fornecedor = self.db.query(models.Fornecedor).filter(
                models.Fornecedor.id == produto.fornecedor_id
            ).first()
            if fornecedor:
                fornecedor_nome = fornecedor.nome
        
        return {
            'produto_id': produto_id,
            'produto_nome': produto.nome,
            'codigo': produto.codigo,
            'categoria': produto.categoria,
            'estoque_atual': estoque_atual,
            'estoque_minimo_atual': produto.estoque_minimo or 0,
            'estoque_minimo_calculado': estoque_minimo_calculado,
            'demanda_media_diaria': demanda_media_diaria,
            'demanda_maxima_diaria': demanda_info['demanda_maxima_diaria'],
            'total_vendido_periodo': demanda_info['total_vendido'],
            'numero_vendas': demanda_info['numero_vendas'],
            'dias_com_vendas': demanda_info['dias_com_vendas'],
            'dias_cobertura_atual': round(dias_cobertura_atual, 1) if dias_cobertura_atual != float('inf') else 'Infinito',
            'quantidade_sugerida': quantidade_sugerida,
            'precisa_compra': precisa_compra,
            'status': status,
            'tem_historico_suficiente': demanda_info['tem_historico_suficiente'],
            'fornecedor_id': produto.fornecedor_id,
            'fornecedor_nome': fornecedor_nome,
            'preco_custo': produto.preco_custo,
            'preco_venda': produto.preco_venda,
            'valor_estimado_compra': round(quantidade_sugerida * (produto.preco_custo or 0), 2),
            'periodo_analise_dias': days_analysis,
            'lead_time_dias': lead_time_days,
            'coverage_days': coverage_days
        }

