'use client';

import { useState, useCallback } from 'react';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';

export interface ClienteKPIs {
  cliente_id: number;
  periodo_dias: number;
  total_vendido: number;
  numero_pedidos: number;
  ticket_medio?: number;
  frequencia_compras_dias?: number;
  produtos_mais_comprados: ProdutoClienteKPI[];
  data_calculo: string;
}

export interface ProdutoClienteKPI {
  produto_id: number;
  produto_nome: string;
  produto_codigo?: string;
  quantidade_total: number;
  ultima_compra?: string;
  numero_pedidos: number;
}

export interface RankingCliente {
  metrica: string;
  periodo_dias: number;
  ranking: Array<{
    cliente_id: number;
    cliente_nome: string;
    total_vendido: number;
    numero_pedidos: number;
    ticket_medio?: number;
    frequencia_compras_dias?: number;
  }>;
}

export function useClienteKPIs() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchKPIs = useCallback(async (
    clienteId: number,
    diasPeriodo: number = 90
  ): Promise<ClienteKPIs | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.get(`/clientes/${clienteId}/kpis?dias_periodo=${diasPeriodo}`);
      const data = response?.data || response;
      return data;
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMessage = error?.response?.data?.detail || error?.message || 'Erro ao buscar KPIs do cliente';
      setError(errorMessage);
      // Não mostrar toast para evitar spam
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchRanking = useCallback(async (
    metrica: string = 'total_vendido',
    limite: number = 10,
    diasPeriodo: number = 90
  ): Promise<RankingCliente | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.get(
        `/clientes/kpis/ranking?metrica=${metrica}&limite=${limite}&dias_periodo=${diasPeriodo}`
      );
      const data = response?.data || response;
      return data;
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMessage = error?.response?.data?.detail || error?.message || 'Erro ao buscar ranking';
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    fetchKPIs,
    fetchRanking
  };
}

