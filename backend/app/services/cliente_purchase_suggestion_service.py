"""
Serviço de sugestões de compra baseado em padrões de compra dos clientes.
Analisa histórico de NF-e processadas para identificar padrões e sugerir compras.
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from ..db import models

logger = logging.getLogger(__name__)


class ClientePurchaseSuggestionService:
    """
    Serviço para sugerir compras baseadas no histórico de compras dos clientes.
    Lógica: Se cliente X sempre compra produto Y, sugere comprar mais produto Y.
    Usa apenas dados verificados de NF-e (HistoricoPrecoProduto com nota_fiscal).
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_purchase_suggestions_for_cliente(
        self,
        cliente_id: int,
        empresa_id: int,
        dias_analise: int = 90
    ) -> Dict[str, Any]:
        """
        Retorna sugestões de compra baseadas no histórico de um cliente específico.
        
        Args:
            cliente_id: ID do cliente
            empresa_id: ID da empresa
            dias_analise: Período de análise em dias
        
        Returns:
            Dict com sugestões de compra para aquele cliente
        """
        data_limite = datetime.now() - timedelta(days=dias_analise)
        
        # Buscar histórico de compras do cliente (apenas NF-e verificadas)
        historico = self.db.query(models.HistoricoPrecoProduto).filter(
            models.HistoricoPrecoProduto.cliente_id == cliente_id,
            models.HistoricoPrecoProduto.empresa_id == empresa_id,
            models.HistoricoPrecoProduto.data_venda >= data_limite,
            models.HistoricoPrecoProduto.nota_fiscal.isnot(None)  # Apenas NF-e verificadas
        ).order_by(models.HistoricoPrecoProduto.data_venda.desc()).all()
        
        if not historico:
            cliente = self.db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
            return {
                'cliente_id': cliente_id,
                'cliente_nome': cliente.razao_social if cliente else 'N/A',
                'cnpj': cliente.cnpj if cliente else None,
                'sugestoes': [],
                'mensagem': 'Cliente não possui histórico de compras no período',
                'periodo_analise_dias': dias_analise
            }
        
        # Agrupar por produto e calcular frequência
        produtos_comprados = defaultdict(lambda: {
            'total_quantidade': 0,
            'total_valor': 0,
            'num_compras': 0,
            'datas': [],
            'precos_unitarios': []
        })
        
        for compra in historico:
            produto_id = compra.produto_id
            produtos_comprados[produto_id]['total_quantidade'] += compra.quantidade
            produtos_comprados[produto_id]['total_valor'] += compra.valor_total
            produtos_comprados[produto_id]['num_compras'] += 1
            produtos_comprados[produto_id]['datas'].append(compra.data_venda)
            produtos_comprados[produto_id]['precos_unitarios'].append(compra.preco_unitario)
        
        # Criar sugestões
        sugestoes = []
        cliente = self.db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
        
        for produto_id, dados in produtos_comprados.items():
            produto = self.db.query(models.Produto).filter(
                models.Produto.id == produto_id,
                models.Produto.empresa_id == empresa_id
            ).first()
            
            if not produto:
                continue
            
            # Calcular frequência média de compra
            frequencia_dias = self._calcular_frequencia(dados['datas'])
            
            # Calcular quantidade média por compra
            quantidade_media = dados['total_quantidade'] / dados['num_compras'] if dados['num_compras'] > 0 else 0
            
            # Calcular preço médio pago pelo cliente
            preco_medio = sum(dados['precos_unitarios']) / len(dados['precos_unitarios']) if dados['precos_unitarios'] else produto.preco_venda or 0
            
            # Calcular quando foi a última compra
            ultima_compra = max(dados['datas']) if dados['datas'] else None
            dias_desde_ultima_compra = (datetime.now() - ultima_compra).days if ultima_compra else None
            
            # Sugerir quantidade baseada na frequência
            # Se cliente compra a cada 30 dias, sugerir quantidade para 30-37 dias (1 semana após)
            dias_proxima_compra_esperada = frequencia_dias or 30
            dias_ate_proxima_compra = dias_proxima_compra_esperada - (dias_desde_ultima_compra or 0)
            
            # Se falta menos de 1 semana para a próxima compra esperada, sugerir compra
            quantidade_sugerida = 0
            precisa_comprar = False
            
            if dias_ate_proxima_compra <= 7 and dias_ate_proxima_compra >= 0:
                # Está próximo da próxima compra esperada, sugerir compra
                quantidade_sugerida = int(quantidade_media * (7 / dias_proxima_compra_esperada))  # Quantidade para 1 semana
                precisa_comprar = True
            elif dias_desde_ultima_compra and dias_desde_ultima_compra > dias_proxima_compra_esperada:
                # Já passou o período esperado, sugerir compra urgente
                quantidade_sugerida = int(quantidade_media)
                precisa_comprar = True
            
            # Verificar estoque atual
            estoque_atual = produto.quantidade_em_estoque or 0
            
            # Determinar prioridade
            if precisa_comprar and estoque_atual < quantidade_media:
                prioridade = 'ALTA'
            elif precisa_comprar:
                prioridade = 'MEDIA'
            else:
                prioridade = 'BAIXA'
            
            sugestoes.append({
                'produto_id': produto_id,
                'produto_nome': produto.nome,
                'codigo': produto.codigo,
                'cliente_compra_frequente': True,
                'quantidade_media_compra': round(quantidade_media, 2),
                'frequencia_compras_dias': frequencia_dias,
                'ultima_compra': ultima_compra.isoformat() if ultima_compra else None,
                'dias_desde_ultima_compra': dias_desde_ultima_compra,
                'dias_ate_proxima_compra_esperada': dias_ate_proxima_compra if dias_ate_proxima_compra >= 0 else None,
                'num_compras_periodo': dados['num_compras'],
                'estoque_atual': estoque_atual,
                'quantidade_sugerida': quantidade_sugerida,
                'preco_custo': produto.preco_custo,
                'preco_medio_cliente': round(preco_medio, 2),
                'valor_estimado': quantidade_sugerida * (produto.preco_custo or 0),
                'prioridade': prioridade,
                'precisa_comprar': precisa_comprar
            })
        
        # Ordenar por prioridade e frequência
        sugestoes.sort(key=lambda x: (
            0 if x['prioridade'] == 'ALTA' else 1 if x['prioridade'] == 'MEDIA' else 2,
            -x['num_compras_periodo']
        ))
        
        return {
            'cliente_id': cliente_id,
            'cliente_nome': cliente.razao_social if cliente else 'N/A',
            'cnpj': cliente.cnpj if cliente else None,
            'periodo_analise_dias': dias_analise,
            'total_produtos_unicos': len(sugestoes),
            'sugestoes': sugestoes
        }
    
    def get_client_purchase_history(
        self,
        cliente_id: int,
        empresa_id: int,
        dias: int = 90
    ) -> Dict[str, Any]:
        """
        Retorna histórico completo de compras do cliente agrupado por NF-e.
        
        Args:
            cliente_id: ID do cliente
            empresa_id: ID da empresa
            dias: Período de análise em dias
        
        Returns:
            Dict com histórico completo de compras por NF-e
        """
        data_limite = datetime.now() - timedelta(days=dias)
        
        # Buscar histórico de compras do cliente (apenas NF-e verificadas)
        historico = self.db.query(models.HistoricoPrecoProduto).filter(
            models.HistoricoPrecoProduto.cliente_id == cliente_id,
            models.HistoricoPrecoProduto.empresa_id == empresa_id,
            models.HistoricoPrecoProduto.data_venda >= data_limite,
            models.HistoricoPrecoProduto.nota_fiscal.isnot(None)  # Apenas NF-e verificadas
        ).order_by(models.HistoricoPrecoProduto.data_venda.desc()).all()
        
        cliente = self.db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
        
        # Agrupar por nota fiscal
        compras_por_nf = defaultdict(lambda: {
            'nota_fiscal': None,
            'data_emissao': None,
            'produtos': [],
            'valor_total': 0
        })
        
        for compra in historico:
            nota_fiscal = compra.nota_fiscal or 'N/A'
            if nota_fiscal not in compras_por_nf:
                compras_por_nf[nota_fiscal]['nota_fiscal'] = nota_fiscal
                compras_por_nf[nota_fiscal]['data_emissao'] = compra.data_venda.isoformat() if compra.data_venda else None
            
            produto = self.db.query(models.Produto).filter(models.Produto.id == compra.produto_id).first()
            
            compras_por_nf[nota_fiscal]['produtos'].append({
                'produto_id': compra.produto_id,
                'produto_nome': produto.nome if produto else 'N/A',
                'codigo': produto.codigo if produto else None,
                'quantidade': compra.quantidade,
                'preco_unitario': compra.preco_unitario,
                'valor_total': compra.valor_total
            })
            compras_por_nf[nota_fiscal]['valor_total'] += compra.valor_total
        
        return {
            'cliente_id': cliente_id,
            'cliente_nome': cliente.razao_social if cliente else 'N/A',
            'cnpj': cliente.cnpj if cliente else None,
            'periodo_dias': dias,
            'total_notas': len(compras_por_nf),
            'compras_por_nota': list(compras_por_nf.values())
        }
    
    def get_top_products_by_cliente(
        self,
        cliente_id: int,
        empresa_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retorna produtos mais comprados pelo cliente.
        
        Args:
            cliente_id: ID do cliente
            empresa_id: ID da empresa
            limit: Limite de produtos a retornar
        
        Returns:
            Lista de produtos mais comprados
        """
        # Buscar histórico agregado por produto
        query = text("""
            SELECT 
                hp.produto_id,
                SUM(hp.quantidade) as total_quantidade,
                SUM(hp.valor_total) as total_valor,
                COUNT(hp.id) as num_compras,
                AVG(hp.preco_unitario) as preco_medio
            FROM historico_preco_produto hp
            WHERE hp.cliente_id = :cliente_id
                AND hp.empresa_id = :empresa_id
                AND hp.nota_fiscal IS NOT NULL
            GROUP BY hp.produto_id
            ORDER BY total_valor DESC
            LIMIT :limit
        """)
        
        result = self.db.execute(query, {
            'cliente_id': cliente_id,
            'empresa_id': empresa_id,
            'limit': limit
        })
        
        produtos_mais_comprados = []
        for row in result:
            produto = self.db.query(models.Produto).filter(
                models.Produto.id == row.produto_id
            ).first()
            
            if produto:
                produtos_mais_comprados.append({
                    'produto_id': row.produto_id,
                    'produto_nome': produto.nome,
                    'codigo': produto.codigo,
                    'total_quantidade': float(row.total_quantidade),
                    'total_valor': float(row.total_valor),
                    'num_compras': row.num_compras,
                    'preco_medio': float(row.preco_medio) if row.preco_medio else 0
                })
        
        return produtos_mais_comprados
    
    def get_global_purchase_suggestions(
        self,
        empresa_id: int,
        dias_analise: int = 90
    ) -> Dict[str, Any]:
        """
        Retorna sugestões de compra baseadas em TODOS os clientes.
        Produtos que são comprados frequentemente por múltiplos clientes.
        
        Args:
            empresa_id: ID da empresa
            dias_analise: Período de análise em dias
        
        Returns:
            Dict com sugestões globais de compra
        """
        data_limite = datetime.now() - timedelta(days=dias_analise)
        
        # Buscar todos os histórico de preços (todas as NF-e processadas)
        historico = self.db.query(models.HistoricoPrecoProduto).filter(
            models.HistoricoPrecoProduto.empresa_id == empresa_id,
            models.HistoricoPrecoProduto.data_venda >= data_limite,
            models.HistoricoPrecoProduto.cliente_id.isnot(None),
            models.HistoricoPrecoProduto.nota_fiscal.isnot(None)  # Apenas NF-e verificadas
        ).all()
        
        # Agrupar por produto
        produtos_comprados = defaultdict(lambda: {
            'total_quantidade': 0,
            'total_valor': 0,
            'num_compras': 0,
            'clientes_unicos': set(),
            'datas': []
        })
        
        for compra in historico:
            produto_id = compra.produto_id
            produtos_comprados[produto_id]['total_quantidade'] += compra.quantidade
            produtos_comprados[produto_id]['total_valor'] += compra.valor_total
            produtos_comprados[produto_id]['num_compras'] += 1
            if compra.cliente_id is not None:
                produtos_comprados[produto_id]['clientes_unicos'].add(compra.cliente_id)
            produtos_comprados[produto_id]['datas'].append(compra.data_venda)
        
        # Criar sugestões
        sugestoes = []
        for produto_id, dados in produtos_comprados.items():
            produto = self.db.query(models.Produto).filter(
                models.Produto.id == produto_id,
                models.Produto.empresa_id == empresa_id
            ).first()
            
            if not produto:
                continue
            
            # Apenas produtos comprados por pelo menos 1 cliente
            if len(dados['clientes_unicos']) < 1:
                continue
            
            quantidade_media = dados['total_quantidade'] / dados['num_compras'] if dados['num_compras'] > 0 else 0
            estoque_atual = produto.quantidade_em_estoque or 0
            
            # Calcular demanda projetada (baseado em vendas recentes)
            vendas_recentes = [
                c for c in historico 
                if c.produto_id == produto_id and c.data_venda >= datetime.now() - timedelta(days=30)
            ]
            demanda_30_dias = sum(c.quantidade for c in vendas_recentes)
            
            # Sugerir quantidade para cobrir 45 dias (demanda recente + margem)
            quantidade_sugerida = max(int(demanda_30_dias * 1.5), int(quantidade_media * 2))
            
            sugestoes.append({
                'produto_id': produto_id,
                'produto_nome': produto.nome or "Sem nome",
                'codigo': produto.codigo or "",
                'num_clientes_compram': len(dados['clientes_unicos']),
                'num_compras_periodo': dados['num_compras'],
                'quantidade_vendida_periodo': dados['total_quantidade'],
                'demanda_30_dias': demanda_30_dias,
                'estoque_atual': estoque_atual,
                'quantidade_sugerida': quantidade_sugerida,
                'preco_custo': produto.preco_custo,
                'valor_estimado': quantidade_sugerida * (produto.preco_custo or 0),
                'prioridade': 'ALTA' if estoque_atual < demanda_30_dias else 'MEDIA'
            })
        
        sugestoes.sort(key=lambda x: (-x['num_clientes_compram'], -x['num_compras_periodo']))
        
        return {
            'periodo_analise_dias': dias_analise,
            'total_produtos': len(sugestoes),
            'sugestoes': sugestoes
        }
    
    def _calcular_frequencia(self, datas: List[datetime]) -> Optional[float]:
        """Calcula frequência média de compra em dias."""
        if len(datas) < 2:
            return None
        
        datas_ordenadas = sorted(set(v.date() for v in datas))
        if len(datas_ordenadas) < 2:
            return None
        
        intervalos = [(datas_ordenadas[i+1] - datas_ordenadas[i]).days 
                     for i in range(len(datas_ordenadas) - 1)]
        
        return sum(intervalos) / len(intervalos) if intervalos else None
