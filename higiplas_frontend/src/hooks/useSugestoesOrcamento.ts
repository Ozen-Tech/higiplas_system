'use client';

import { useState, useCallback } from 'react';
import { apiService } from '@/services/apiService';

export interface SugestaoProduto {
  produto_id: number;
  ultimo_preco: number | null;
  quantidade_sugerida: number | null;
  historico_disponivel: boolean;
}

export interface SugestoesCliente {
  cliente_id: number;
  sugestoes: SugestaoProduto[];
  total_produtos: number;
}

export function useSugestoesOrcamento() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const obterSugestoesCliente = useCallback(async (clienteId: number): Promise<SugestoesCliente | null> => {
    if (!clienteId) {
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.get(`/orcamentos/sugestoes/${clienteId}`);
      const data = response?.data || response;
      
      return {
        cliente_id: data.cliente_id,
        sugestoes: data.sugestoes || [],
        total_produtos: data.total_produtos || 0
      };
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMessage = error?.response?.data?.detail || error?.message || 'Erro ao obter sugestões';
      setError(errorMessage);
      // Não mostrar toast de erro para evitar spam - sugestões são opcionais
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const obterSugestaoProduto = useCallback(async (
    clienteId: number,
    produtoId: number
  ): Promise<SugestaoProduto | null> => {
    if (!clienteId || !produtoId) {
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.get(`/orcamentos/sugestoes/${clienteId}/${produtoId}`);
      const data = response?.data || response;
      
      return {
        produto_id: data.produto_id,
        ultimo_preco: data.ultimo_preco,
        quantidade_sugerida: data.quantidade_sugerida,
        historico_disponivel: data.historico_disponivel || false
      };
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMessage = error?.response?.data?.detail || error?.message || 'Erro ao obter sugestão';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    obterSugestoesCliente,
    obterSugestaoProduto
  };
}

