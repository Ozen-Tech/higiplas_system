#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Router para endpoints de cálculo e gestão de estoque mínimo.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..db.connection import get_db
from ..services.minimum_stock_service import MinimumStockService, calculate_and_update_minimum_stock
from ..dependencies import get_current_user
from ..db import models

router = APIRouter(
    prefix="/minimum-stock",
    tags=["Estoque Mínimo"]
)


@router.get("/calculate/{empresa_id}", response_model=Dict[str, Any])
def calculate_minimum_stock(
    empresa_id: int,
    days_analysis: int = Query(90, description="Período de análise em dias", ge=30, le=365),
    safety_margin: float = Query(1.5, description="Margem de segurança", ge=1.0, le=3.0),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Calcula recomendações de estoque mínimo baseado no histórico de vendas.
    
    - **empresa_id**: ID da empresa
    - **days_analysis**: Período de análise em dias (30-365)
    - **safety_margin**: Margem de segurança (1.0-3.0)
    """
    try:
        service = MinimumStockService(db)
        recommendations = service.calculate_minimum_stock_from_movements(
            empresa_id=empresa_id,
            days_analysis=days_analysis,
            safety_margin=safety_margin
        )
        
        # Estatísticas resumidas
        total_produtos = len(recommendations)
        produtos_com_vendas = len([r for r in recommendations if r['numero_vendas'] > 0])
        produtos_precisam_atualizacao = len([r for r in recommendations if r['necessita_atualizacao']])
        valor_total = sum(r['valor_estoque_minimo'] for r in recommendations)
        
        return {
            "success": True,
            "message": f"Análise concluída para {total_produtos} produtos",
            "resumo": {
                "total_produtos": total_produtos,
                "produtos_com_vendas": produtos_com_vendas,
                "produtos_precisam_atualizacao": produtos_precisam_atualizacao,
                "valor_total_estoque_minimo": round(valor_total, 2),
                "periodo_analise_dias": days_analysis,
                "margem_seguranca": safety_margin
            },
            "recomendacoes": recommendations[:100],  # Limitar a 100 para performance
            "data_calculo": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular estoque mínimo: {str(e)}"
        )

@router.post("/update/{empresa_id}")
def update_minimum_stock(
    empresa_id: int,
    update_all: bool = Query(False, description="Atualizar todos os produtos ou apenas com vendas"),
    min_sales_threshold: int = Query(2, description="Número mínimo de vendas para atualizar", ge=1),
    days_analysis: int = Query(90, description="Período de análise em dias", ge=30, le=365),
    safety_margin: float = Query(1.5, description="Margem de segurança", ge=1.0, le=3.0),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Calcula e atualiza o estoque mínimo no banco de dados.
    
    - **empresa_id**: ID da empresa
    - **update_all**: Se True, atualiza todos os produtos
    - **min_sales_threshold**: Número mínimo de vendas para considerar
    - **days_analysis**: Período de análise em dias
    - **safety_margin**: Margem de segurança
    """
    try:
        service = MinimumStockService(db)
        
        # Calcular recomendações
        recommendations = service.calculate_minimum_stock_from_movements(
            empresa_id=empresa_id,
            days_analysis=days_analysis,
            safety_margin=safety_margin
        )
        
        # Atualizar banco de dados
        update_stats = service.update_minimum_stock_in_database(
            recommendations=recommendations,
            update_all=update_all,
            min_sales_threshold=min_sales_threshold
        )
        
        return {
            "success": True,
            "message": f"Estoque mínimo atualizado para {update_stats['updated']} produtos",
            "estatisticas": update_stats,
            "parametros": {
                "empresa_id": empresa_id,
                "update_all": update_all,
                "min_sales_threshold": min_sales_threshold,
                "days_analysis": days_analysis,
                "safety_margin": safety_margin
            },
            "data_atualizacao": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar estoque mínimo: {str(e)}"
        )

@router.get("/critical/{empresa_id}")
def get_critical_stock_products(
    empresa_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna produtos com estoque crítico (sem estoque ou abaixo do mínimo).
    """
    try:
        service = MinimumStockService(db)
        critical_products = service.get_critical_stock_products(empresa_id)
        
        # Estatísticas
        sem_estoque = len([p for p in critical_products if p['status_estoque'] == 'SEM_ESTOQUE'])
        abaixo_minimo = len([p for p in critical_products if p['status_estoque'] == 'ABAIXO_MINIMO'])
        
        return {
            "success": True,
            "message": f"Encontrados {len(critical_products)} produtos com estoque crítico",
            "resumo": {
                "total_criticos": len(critical_products),
                "sem_estoque": sem_estoque,
                "abaixo_minimo": abaixo_minimo
            },
            "produtos_criticos": critical_products,
            "data_consulta": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar produtos críticos: {str(e)}"
        )

@router.get("/report/{empresa_id}")
def generate_stock_report(
    empresa_id: int,
    days_analysis: int = Query(90, description="Período de análise em dias", ge=30, le=365),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Gera relatório completo de estoque com recomendações e produtos críticos.
    """
    try:
        report = calculate_and_update_minimum_stock(
            db=db,
            empresa_id=empresa_id,
            update_database=False,
            days_analysis=days_analysis
        )
        
        return {
            "success": True,
            "message": "Relatório de estoque gerado com sucesso",
            "relatorio": report
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )

@router.get("/analytics/{empresa_id}")
def get_stock_analytics(
    empresa_id: int,
    days_analysis: int = Query(90, description="Período de análise em dias", ge=30, le=365),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Retorna analytics detalhados sobre padrões de demanda e estoque.
    """
    try:
        service = MinimumStockService(db)
        recommendations = service.calculate_minimum_stock_from_movements(
            empresa_id=empresa_id,
            days_analysis=days_analysis
        )
        
        # Analytics por categoria
        category_analytics = {}
        for rec in recommendations:
            categoria = rec['categoria'] or 'Sem Categoria'
            if categoria not in category_analytics:
                category_analytics[categoria] = {
                    'produtos': 0,
                    'demanda_total': 0,
                    'valor_estoque_minimo': 0,
                    'produtos_alta_demanda': 0
                }
            
            category_analytics[categoria]['produtos'] += 1
            category_analytics[categoria]['demanda_total'] += rec['demanda_semanal_media']
            category_analytics[categoria]['valor_estoque_minimo'] += rec['valor_estoque_minimo']
            
            if rec['classificacao_demanda'] == 'ALTA':
                category_analytics[categoria]['produtos_alta_demanda'] += 1
        
        # Top produtos por demanda
        top_demanda = sorted(
            recommendations,
            key=lambda x: x['demanda_semanal_media'],
            reverse=True
        )[:10]
        
        # Produtos com maior variabilidade
        produtos_variaveis = [
            rec for rec in recommendations 
            if rec['numero_vendas'] >= 5 and rec['demanda_semanal_media'] > 0
        ]
        
        return {
            "success": True,
            "message": "Analytics gerados com sucesso",
            "analytics": {
                "periodo_analise": days_analysis,
                "total_produtos_analisados": len(recommendations),
                "analytics_por_categoria": category_analytics,
                "top_produtos_demanda": top_demanda,
                "produtos_com_vendas_regulares": len(produtos_variaveis),
                "data_analise": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar analytics: {str(e)}"
        )