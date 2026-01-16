"""
Serviço de análise de padrões de compra por cliente.
Analisa histórico de vendas para identificar padrões e tendências.
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from app.db import models

logger = logging.getLogger(__name__)


class ClienteAnalyticsService:
    """Serviço para análise de padrões de compra por cliente."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analisar_padroes_cliente(
        self,
        cliente_id: int,
        empresa_id: int,
        dias_analise: int = 90
    ) -> Dict[str, Any]:
        """
        Analisa padrões de compra de um cliente específico.
        
        Args:
            cliente_id: ID do cliente
            empresa_id: ID da empresa
            dias_analise: Período de análise em dias
            
        Returns:
            Dicionário com análise de padrões
        """
        data_limite = datetime.now() - timedelta(days=dias_analise)
        
        # Buscar histórico de vendas do cliente
        vendas = self.db.query(models.HistoricoVendaCliente).filter(
            models.HistoricoVendaCliente.cliente_id == cliente_id,
            models.HistoricoVendaCliente.empresa_id == empresa_id,
            models.HistoricoVendaCliente.data_venda >= data_limite
        ).order_by(models.HistoricoVendaCliente.data_venda.desc()).all()
        
        if not vendas:
            return {
                'cliente_id': cliente_id,
                'total_vendas': 0,
                'total_valor': 0,
                'produtos_mais_comprados': [],
                'frequencia_compra_dias': None,
                'tendencia': 'SEM_DADOS',
                'padroes': {}
            }
        
        # Agrupar por produto
        produtos_vendas = defaultdict(lambda: {
            'total_quantidade': 0,
            'total_valor': 0,
            'num_vendas': 0,
            'datas': []
        })
        
        total_valor = 0
        datas_compras = []
        
        for venda in vendas:
            produto_id = venda.produto_id
            produtos_vendas[produto_id]['total_quantidade'] += venda.quantidade_vendida
            produtos_vendas[produto_id]['total_valor'] += venda.valor_total
            produtos_vendas[produto_id]['num_vendas'] += 1
            produtos_vendas[produto_id]['datas'].append(venda.data_venda)
            
            total_valor += venda.valor_total
            datas_compras.append(venda.data_venda)
        
        # Produtos mais comprados
        produtos_mais_comprados = []
        for produto_id, dados in sorted(
            produtos_vendas.items(),
            key=lambda x: x[1]['total_valor'],
            reverse=True
        )[:10]:  # Top 10
            produto = self.db.query(models.Produto).filter(
                models.Produto.id == produto_id
            ).first()
            
            if produto:
                produtos_mais_comprados.append({
                    'produto_id': produto_id,
                    'produto_nome': produto.nome,
                    'codigo': produto.codigo,
                    'total_quantidade': dados['total_quantidade'],
                    'total_valor': dados['total_valor'],
                    'num_vendas': dados['num_vendas'],
                    'frequencia_media_dias': self._calcular_frequencia_media(dados['datas'])
                })
        
        # Calcular frequência média de compra
        frequencia_compra_dias = self._calcular_frequencia_media(datas_compras)
        
        # Calcular tendência (crescimento/redução)
        tendencia = self._calcular_tendencia(datas_compras, len(vendas))
        
        # Identificar padrões
        padroes = {
            'produtos_frequentes': len([p for p in produtos_mais_comprados if p['num_vendas'] >= 3]),
            'valor_medio_compra': total_valor / len(set(v.data_venda.date() for v in vendas)) if vendas else 0,
            'frequencia_compra': frequencia_compra_dias,
            'sazonalidade': self._detectar_sazonalidade(datas_compras)
        }
        
        return {
            'cliente_id': cliente_id,
            'total_vendas': len(vendas),
            'total_valor': total_valor,
            'produtos_mais_comprados': produtos_mais_comprados,
            'frequencia_compra_dias': frequencia_compra_dias,
            'tendencia': tendencia,
            'padroes': padroes,
            'periodo_analise_dias': dias_analise
        }
    
    def analisar_padroes_produto_por_cliente(
        self,
        produto_id: int,
        empresa_id: int,
        dias_analise: int = 90
    ) -> Dict[str, Any]:
        """
        Analisa quais clientes compram um produto específico e com que frequência.
        
        Args:
            produto_id: ID do produto
            empresa_id: ID da empresa
            dias_analise: Período de análise em dias
            
        Returns:
            Dicionário com análise por cliente
        """
        data_limite = datetime.now() - timedelta(days=dias_analise)
        
        # Buscar histórico de vendas do produto
        vendas = self.db.query(models.HistoricoVendaCliente).filter(
            models.HistoricoVendaCliente.produto_id == produto_id,
            models.HistoricoVendaCliente.empresa_id == empresa_id,
            models.HistoricoVendaCliente.data_venda >= data_limite
        ).order_by(models.HistoricoVendaCliente.data_venda.desc()).all()
        
        # Agrupar por cliente
        clientes_vendas = defaultdict(lambda: {
            'total_quantidade': 0,
            'total_valor': 0,
            'num_vendas': 0,
            'datas': []
        })
        
        for venda in vendas:
            cliente_id = venda.cliente_id
            clientes_vendas[cliente_id]['total_quantidade'] += venda.quantidade_vendida
            clientes_vendas[cliente_id]['total_valor'] += venda.valor_total
            clientes_vendas[cliente_id]['num_vendas'] += 1
            clientes_vendas[cliente_id]['datas'].append(venda.data_venda)
        
        # Criar lista de clientes que compram o produto
        clientes_produto = []
        for cliente_id, dados in sorted(
            clientes_vendas.items(),
            key=lambda x: x[1]['total_valor'],
            reverse=True
        ):
            cliente = self.db.query(models.Cliente).filter(
                models.Cliente.id == cliente_id
            ).first()
            
            if cliente:
                frequencia = self._calcular_frequencia_media(dados['datas'])
                ultima_compra = max(dados['datas']) if dados['datas'] else None
                dias_ultima_compra = (datetime.now() - ultima_compra).days if ultima_compra else None
                
                clientes_produto.append({
                    'cliente_id': cliente_id,
                    'cliente_nome': cliente.razao_social,
                    'cnpj': cliente.cnpj,
                    'total_quantidade': dados['total_quantidade'],
                    'total_valor': dados['total_valor'],
                    'num_vendas': dados['num_vendas'],
                    'frequencia_media_dias': frequencia,
                    'ultima_compra': ultima_compra.isoformat() if ultima_compra else None,
                    'dias_ultima_compra': dias_ultima_compra,
                    'tendencia': self._calcular_tendencia_cliente_produto(dados['datas'])
                })
        
        # Estatísticas gerais
        total_vendido = sum(v.quantidade_vendida for v in vendas)
        total_valor = sum(v.valor_total for v in vendas)
        clientes_unicos = len(clientes_vendas)
        
        return {
            'produto_id': produto_id,
            'total_vendido': total_vendido,
            'total_valor': total_valor,
            'clientes_unicos': clientes_unicos,
            'clientes': clientes_produto,
            'periodo_analise_dias': dias_analise
        }
    
    def _calcular_frequencia_media(self, datas: List[datetime]) -> Optional[float]:
        """Calcula frequência média de compra em dias."""
        if len(datas) < 2:
            return None
        
        datas_ordenadas = sorted(set(v.date() for v in datas))
        if len(datas_ordenadas) < 2:
            return None
        
        intervalos = []
        for i in range(len(datas_ordenadas) - 1):
            intervalo = (datas_ordenadas[i+1] - datas_ordenadas[i]).days
            intervalos.append(intervalo)
        
        return sum(intervalos) / len(intervalos) if intervalos else None
    
    def _calcular_tendencia(self, datas: List[datetime], num_vendas: int) -> str:
        """Calcula tendência de compra (crescimento/redução/estável)."""
        if num_vendas < 4:
            return 'POUCOS_DADOS'
        
        # Dividir em duas metades e comparar
        datas_ordenadas = sorted(set(v.date() for v in datas))
        meio = len(datas_ordenadas) // 2
        
        primeira_metade = datas_ordenadas[:meio]
        segunda_metade = datas_ordenadas[meio:]
        
        # Contar compras por período (mais simples: comparar frequência)
        freq_1 = len(primeira_metade) / max(1, (datas_ordenadas[meio-1] - datas_ordenadas[0]).days)
        freq_2 = len(segunda_metade) / max(1, (datas_ordenadas[-1] - datas_ordenadas[meio]).days)
        
        if freq_2 > freq_1 * 1.2:
            return 'CRESCIMENTO'
        elif freq_2 < freq_1 * 0.8:
            return 'REDUCAO'
        else:
            return 'ESTAVEL'
    
    def _calcular_tendencia_cliente_produto(self, datas: List[datetime]) -> str:
        """Calcula tendência específica para um cliente-produto."""
        return self._calcular_tendencia(datas, len(datas))
    
    def _detectar_sazonalidade(self, datas: List[datetime]) -> Optional[str]:
        """Detecta padrão de sazonalidade básico (se houver dados suficientes)."""
        if len(datas) < 6:
            return None
        
        # Agrupar por mês
        meses = defaultdict(int)
        for data in datas:
            mes = data.month
            meses[mes] += 1
        
        # Verificar se há concentração em alguns meses
        mes_max = max(meses.items(), key=lambda x: x[1])
        total = sum(meses.values())
        
        if mes_max[1] / total > 0.4:  # Mais de 40% em um mês
            nomes_meses = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                          'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            return f"Concentração em {nomes_meses[mes_max[0]]}"
        
        return None
