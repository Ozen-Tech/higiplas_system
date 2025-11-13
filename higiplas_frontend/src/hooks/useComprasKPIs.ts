'use client';

import { useState, useCallback } from 'react';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';

export interface ComprasKPIs {
  empresa_id: number;
  periodo_meses: number;
  data_calculo: string;
  abc_curva: ABCCurvaKPI[];
  eficiencia_compras: EficienciaCompras;
  estoque_parado: EstoqueParado;
}

export interface ABCCurvaKPI {
  produto_id: number;
  produto_nome: string;
  produto_codigo?: string;
  classificacao: 'A' | 'B' | 'C';
  percentual_vendas: number;
  percentual_estoque: number;
  valor_total_vendas: number;
  percentual_acumulado: number;
}

export interface EficienciaCompras {
  produtos_comprados: number;
  produtos_vendidos: number;
  taxa_acerto_percentual: number;
  periodo_meses: number;
}

export interface EstoqueParado {
  total_produtos_parados: number;
  custo_total_parado: number;
  produtos_parados: Array<{
    produto_id: number;
    produto_nome: string;
    produto_codigo?: string;
    quantidade_estoque: number;
    custo_total: number;
    ultima_movimentacao?: string;
  }>;
}

export interface ProdutoKPI {
  produto_id: number;
  giro_estoque?: {
    produto_id: number;
    produto_nome: string;
    giro_mensal: number;
    giro_anual: number;
    dias_giro: number;
    estoque_atual: number;
    total_vendido_periodo: number;
  };
  dias_cobertura?: {
    produto_id: number;
    produto_nome: string;
    dias_cobertura: number;
    demanda_media_diaria: number;
    estoque_atual: number;
    status: string;
  };
  previsao_compras?: {
    produto_id: number;
    produto_nome: string;
    quantidade_necessaria: number;
    urgencia: string;
    custo_estimado: number;
    dias_cobertura_atual: number;
    demanda_media_diaria: number;
  };
}

export function useComprasKPIs() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchKPIs = useCallback(async (periodoMeses: number = 12): Promise<ComprasKPIs | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.get(`/compras/kpis?periodo_meses=${periodoMeses}`);
      const data = response?.data || response;
      return data;
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMessage = error?.response?.data?.detail || error?.message || 'Erro ao buscar KPIs de compras';
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchKPIProduto = useCallback(async (
    produtoId: number,
    periodoMeses: number = 12
  ): Promise<ProdutoKPI | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.get(`/compras/kpis/produto/${produtoId}?periodo_meses=${periodoMeses}`);
      const data = response?.data || response;
      return data;
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMessage = error?.response?.data?.detail || error?.message || 'Erro ao buscar KPI do produto';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  interface FornecedorKPI {
    fornecedor_id: number;
    fornecedor_nome: string;
    total_entradas: number;
    numero_ordens: number;
    media_por_ordem: number;
    produtos_fornecidos: number;
  }

  const fetchKPIFornecedor = useCallback(async (
    fornecedorId: number,
    periodoMeses: number = 12
  ): Promise<FornecedorKPI | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.get(`/compras/kpis/fornecedor/${fornecedorId}?periodo_meses=${periodoMeses}`);
      const data = response?.data || response;
      return data;
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMessage = error?.response?.data?.detail || error?.message || 'Erro ao buscar KPI do fornecedor';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    fetchKPIs,
    fetchKPIProduto,
    fetchKPIFornecedor
  };
}

