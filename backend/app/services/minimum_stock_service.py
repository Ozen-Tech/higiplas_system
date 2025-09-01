#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço para cálculo e atualização automática de estoque mínimo
baseado em dados históricos de vendas.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import logging

from ..db import models
from ..db.connection import get_db

logger = logging.getLogger(__name__)

class MinimumStockService:
    """Serviço para cálculo de estoque mínimo baseado em histórico de vendas."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_minimum_stock_from_movements(
        self, 
        empresa_id: int,
        days_analysis: int = 90,
        safety_margin: float = 1.5
    ) -> List[Dict[str, Any]]:
        """
        Calcula estoque mínimo baseado nas movimentações de saída (vendas) do banco.
        
        Args:
            empresa_id: ID da empresa
            days_analysis: Período de análise em dias (padrão 90 dias)
            safety_margin: Margem de segurança (padrão 1.5 = 50% a mais)
        
        Returns:
            Lista com recomendações de estoque mínimo
        """
        # Data limite para análise
        data_limite = datetime.now() - timedelta(days=days_analysis)
        
        # Query para buscar movimentações de saída por produto
        query = text("""
            SELECT 
                p.id as produto_id,
                p.nome as produto_nome,
                p.codigo,
                p.categoria,
                p.estoque_minimo as estoque_minimo_atual,
                p.quantidade_em_estoque,
                p.preco_venda,
                COALESCE(SUM(m.quantidade), 0) as total_vendido,
                COUNT(m.id) as numero_vendas,
                COALESCE(AVG(m.quantidade), 0) as media_por_venda,
                COALESCE(MAX(m.quantidade), 0) as maior_venda,
                COALESCE(STDDEV(m.quantidade), 0) as desvio_padrao
            FROM produtos p
            LEFT JOIN movimentacoes_estoque m ON p.id = m.produto_id 
                AND m.tipo_movimentacao = 'SAIDA'
                AND m.data_movimentacao >= :data_limite
            WHERE p.empresa_id = :empresa_id
            GROUP BY p.id, p.nome, p.codigo, p.categoria, p.estoque_minimo, 
                     p.quantidade_em_estoque, p.preco_venda
            ORDER BY total_vendido DESC
        """)
        
        result = self.db.execute(query, {
            'empresa_id': empresa_id,
            'data_limite': data_limite
        })
        
        recommendations = []
        semanas_periodo = days_analysis / 7  # Converter dias para semanas
        
        for row in result:
            # Calcular demanda semanal média
            demanda_semanal_media = row.total_vendido / semanas_periodo if semanas_periodo > 0 else 0
            
            # Calcular estoque mínimo com margem de segurança
            estoque_minimo_sugerido = max(1, int(demanda_semanal_media * safety_margin))
            
            # Ajustar baseado na variabilidade (desvio padrão)
            if row.desvio_padrao and row.media_por_venda > 0:
                coef_variacao = row.desvio_padrao / row.media_por_venda
                if coef_variacao > 0.5:  # Alta variabilidade
                    estoque_minimo_sugerido = int(estoque_minimo_sugerido * 1.3)
                elif coef_variacao > 0.3:  # Média variabilidade
                    estoque_minimo_sugerido = int(estoque_minimo_sugerido * 1.2)
            
            # Garantir que não seja menor que a maior venda individual
            if row.maior_venda > estoque_minimo_sugerido:
                estoque_minimo_sugerido = int(row.maior_venda)
            
            # Classificar demanda
            classificacao = self._classify_demand(demanda_semanal_media, row.numero_vendas)
            
            # Status do estoque atual
            status_estoque = self._get_stock_status(
                row.quantidade_em_estoque or 0,
                estoque_minimo_sugerido
            )
            
            recommendation = {
                'produto_id': row.produto_id,
                'produto_nome': row.produto_nome,
                'codigo': row.codigo,
                'categoria': row.categoria,
                'estoque_minimo_atual': row.estoque_minimo_atual or 0,
                'estoque_minimo_sugerido': estoque_minimo_sugerido,
                'quantidade_atual': row.quantidade_em_estoque or 0,
                'demanda_semanal_media': round(demanda_semanal_media, 2),
                'total_vendido_periodo': float(row.total_vendido),
                'numero_vendas': row.numero_vendas,
                'media_por_venda': round(float(row.media_por_venda), 2),
                'maior_venda': float(row.maior_venda),
                'classificacao_demanda': classificacao,
                'status_estoque': status_estoque,
                'necessita_atualizacao': estoque_minimo_sugerido != (row.estoque_minimo_atual or 0),
                'valor_estoque_minimo': round(estoque_minimo_sugerido * (row.preco_venda or 0), 2)
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _classify_demand(self, demanda_semanal: float, numero_vendas: int) -> str:
        """Classifica a demanda do produto."""
        if demanda_semanal >= 50 and numero_vendas >= 10:
            return "ALTA"
        elif demanda_semanal >= 20 and numero_vendas >= 5:
            return "MÉDIA"
        elif demanda_semanal >= 5 and numero_vendas >= 2:
            return "BAIXA"
        else:
            return "MUITO_BAIXA"
    
    def _get_stock_status(self, quantidade_atual: int, estoque_minimo: int) -> str:
        """Determina o status do estoque atual."""
        if quantidade_atual <= 0:
            return "SEM_ESTOQUE"
        elif quantidade_atual < estoque_minimo:
            return "ABAIXO_MINIMO"
        elif quantidade_atual < estoque_minimo * 1.5:
            return "BAIXO"
        else:
            return "ADEQUADO"
    
    def update_minimum_stock_in_database(
        self, 
        recommendations: List[Dict[str, Any]],
        update_all: bool = False,
        min_sales_threshold: int = 2
    ) -> Dict[str, int]:
        """
        Atualiza o estoque mínimo no banco de dados.
        
        Args:
            recommendations: Lista de recomendações
            update_all: Se True, atualiza todos os produtos. Se False, apenas produtos com vendas
            min_sales_threshold: Número mínimo de vendas para atualizar
        
        Returns:
            Dicionário com estatísticas da atualização
        """
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        try:
            for rec in recommendations:
                # Filtrar produtos com poucas vendas se não for update_all
                if not update_all and rec['numero_vendas'] < min_sales_threshold:
                    skipped_count += 1
                    continue
                
                # Buscar produto no banco
                produto = self.db.query(models.Produto).filter(
                    models.Produto.id == rec['produto_id']
                ).first()
                
                if produto:
                    # Atualizar estoque mínimo
                    produto.estoque_minimo = rec['estoque_minimo_sugerido']
                    updated_count += 1
                else:
                    error_count += 1
                    logger.warning(f"Produto ID {rec['produto_id']} não encontrado")
            
            # Commit das alterações
            self.db.commit()
            
            logger.info(f"Estoque mínimo atualizado: {updated_count} produtos")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar estoque mínimo: {e}")
            error_count += len(recommendations) - updated_count - skipped_count
        
        return {
            'updated': updated_count,
            'skipped': skipped_count,
            'errors': error_count,
            'total_processed': len(recommendations)
        }
    
    def get_critical_stock_products(self, empresa_id: int) -> List[Dict[str, Any]]:
        """
        Retorna produtos com estoque crítico (sem estoque ou abaixo do mínimo).
        """
        query = text("""
            SELECT 
                id as produto_id,
                nome as produto_nome,
                codigo,
                categoria,
                quantidade_em_estoque,
                estoque_minimo,
                preco_venda,
                CASE 
                    WHEN quantidade_em_estoque <= 0 THEN 'SEM_ESTOQUE'
                    WHEN quantidade_em_estoque < estoque_minimo THEN 'ABAIXO_MINIMO'
                    ELSE 'ADEQUADO'
                END as status_estoque
            FROM produtos 
            WHERE empresa_id = :empresa_id
                AND (quantidade_em_estoque <= 0 OR quantidade_em_estoque < estoque_minimo)
            ORDER BY 
                CASE 
                    WHEN quantidade_em_estoque <= 0 THEN 1
                    WHEN quantidade_em_estoque < estoque_minimo THEN 2
                    ELSE 3
                END,
                quantidade_em_estoque ASC
        """)
        
        result = self.db.execute(query, {'empresa_id': empresa_id})
        
        critical_products = []
        for row in result:
            critical_products.append({
                'produto_id': row.produto_id,
                'produto_nome': row.produto_nome,
                'codigo': row.codigo,
                'categoria': row.categoria,
                'quantidade_atual': row.quantidade_em_estoque or 0,
                'estoque_minimo': row.estoque_minimo or 0,
                'status_estoque': row.status_estoque,
                'valor_unitario': row.preco_venda or 0,
                'deficit': max(0, (row.estoque_minimo or 0) - (row.quantidade_em_estoque or 0))
            })
        
        return critical_products
    
    def generate_stock_report(self, empresa_id: int) -> Dict[str, Any]:
        """
        Gera relatório completo de estoque com recomendações.
        """
        # Calcular recomendações
        recommendations = self.calculate_minimum_stock_from_movements(empresa_id)
        
        # Produtos críticos
        critical_products = self.get_critical_stock_products(empresa_id)
        
        # Estatísticas gerais
        total_produtos = len(recommendations)
        produtos_com_vendas = len([r for r in recommendations if r['numero_vendas'] > 0])
        produtos_precisam_atualizacao = len([r for r in recommendations if r['necessita_atualizacao']])
        valor_total_estoque_minimo = sum(r['valor_estoque_minimo'] for r in recommendations)
        
        # Classificação por demanda
        demanda_stats = defaultdict(int)
        for rec in recommendations:
            demanda_stats[rec['classificacao_demanda']] += 1
        
        return {
            'resumo': {
                'total_produtos': total_produtos,
                'produtos_com_vendas': produtos_com_vendas,
                'produtos_precisam_atualizacao': produtos_precisam_atualizacao,
                'produtos_criticos': len(critical_products),
                'valor_total_estoque_minimo': valor_total_estoque_minimo
            },
            'classificacao_demanda': dict(demanda_stats),
            'recomendacoes': recommendations[:50],  # Top 50
            'produtos_criticos': critical_products[:20],  # Top 20 críticos
            'data_analise': datetime.now().isoformat()
        }

# Função utilitária para usar o serviço
def calculate_and_update_minimum_stock(
    db: Session, 
    empresa_id: int, 
    update_database: bool = False,
    days_analysis: int = 90
) -> Dict[str, Any]:
    """
    Função utilitária para calcular e opcionalmente atualizar estoque mínimo.
    """
    service = MinimumStockService(db)
    
    # Gerar relatório completo
    report = service.generate_stock_report(empresa_id)
    
    # Atualizar banco se solicitado
    if update_database:
        update_stats = service.update_minimum_stock_in_database(
            report['recomendacoes'],
            update_all=False,
            min_sales_threshold=2
        )
        report['update_stats'] = update_stats
    
    return report