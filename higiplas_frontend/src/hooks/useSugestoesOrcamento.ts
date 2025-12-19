'use client';

import { useState, useCallback } from 'react';
import { apiService } from '@/services/apiService';

// Range de preços do histórico com o cliente
export interface PrecoCliente {
  ultimo: number | null;    // Último preço vendido
  minimo: number | null;    // Menor preço já vendido
  maximo: number | null;    // Maior preço já vendido
  medio: number | null;     // Média de preços
}

// Sugestão expandida com range de preços e preço do sistema
export interface SugestaoProduto {
  produto_id: number;
  produto_nome?: string | null;
  preco_sistema: number;           // Preço de venda cadastrado no produto
  preco_cliente: PrecoCliente | null;  // Range de preços do cliente
  quantidade_sugerida: number | null;
  total_vendas: number;            // Quantas vezes vendeu para este cliente
  historico_disponivel: boolean;
  // Campos legados para compatibilidade
  ultimo_preco?: number | null;
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
      
      // Mapear sugestões para incluir campo legado ultimo_preco
      const sugestoes: SugestaoProduto[] = (data.sugestoes || []).map((s: SugestaoProduto) => ({
        ...s,
        ultimo_preco: s.preco_cliente?.ultimo || null
      }));
      
      return {
        cliente_id: data.cliente_id,
        sugestoes,
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
        produto_nome: data.produto_nome || null,
        preco_sistema: data.preco_sistema || 0,
        preco_cliente: data.preco_cliente || null,
        quantidade_sugerida: data.quantidade_sugerida,
        total_vendas: data.total_vendas || 0,
        historico_disponivel: data.historico_disponivel || false,
        ultimo_preco: data.preco_cliente?.ultimo || null
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

