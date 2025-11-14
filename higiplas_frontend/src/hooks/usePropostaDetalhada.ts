// src/hooks/usePropostaDetalhada.ts

import { useState, useCallback } from 'react';
import { propostaService, PropostaDetalhada, PropostaDetalhadaCreate } from '@/services/propostaService';

export function usePropostaDetalhada() {
  const [propostas, setPropostas] = useState<PropostaDetalhada[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createProposta = async (proposta: PropostaDetalhadaCreate) => {
    setLoading(true);
    setError(null);
    try {
      console.log('Criando proposta:', proposta);
      const novaProposta = await propostaService.create(proposta);
      console.log('Proposta criada com sucesso:', novaProposta);
      setPropostas((prev) => [novaProposta, ...prev]);
      return novaProposta;
    } catch (err) {
      console.error('Erro ao criar proposta:', err);
      let errorMessage = 'Erro ao criar proposta';
      
      if (err instanceof Error) {
        errorMessage = err.message;
        // Extrair mensagem de erro da API se disponível
        if (errorMessage.includes('[') && errorMessage.includes(']')) {
          try {
            const match = errorMessage.match(/\[(\d+)\]\s*(.+)/);
            if (match && match[2]) {
              errorMessage = match[2].trim();
            }
          } catch {
            // Se não conseguir extrair, usar a mensagem original
          }
        }
      }
      
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getPropostas = useCallback(async (skip = 0, limit = 100, isAdmin = false) => {
    setLoading(true);
    setError(null);
    try {
      const data = isAdmin 
        ? await propostaService.getAll(skip, limit)
        : await propostaService.getMyPropostas(skip, limit);
      setPropostas(data);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao buscar propostas';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getPropostaById = async (propostaId: number) => {
    setLoading(true);
    setError(null);
    try {
      const proposta = await propostaService.getById(propostaId);
      return proposta;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao buscar proposta';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getPropostasByCliente = async (clienteId: number, skip = 0, limit = 100) => {
    setLoading(true);
    setError(null);
    try {
      const data = await propostaService.getByCliente(clienteId, skip, limit);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao buscar propostas do cliente';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const compartilharProposta = async (propostaId: number) => {
    setLoading(true);
    setError(null);
    try {
      const proposta = await propostaService.compartilhar(propostaId);
      // Atualizar na lista
      setPropostas((prev) =>
        prev.map((p) => (p.id === propostaId ? proposta : p))
      );
      return proposta;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao compartilhar proposta';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateProposta = async (propostaId: number, proposta: Partial<PropostaDetalhadaCreate>) => {
    setLoading(true);
    setError(null);
    try {
      const propostaAtualizada = await propostaService.update(propostaId, proposta);
      setPropostas((prev) =>
        prev.map((p) => (p.id === propostaId ? propostaAtualizada : p))
      );
      return propostaAtualizada;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao atualizar proposta';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteProposta = async (propostaId: number) => {
    setLoading(true);
    setError(null);
    try {
      await propostaService.delete(propostaId);
      setPropostas((prev) => prev.filter((p) => p.id !== propostaId));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao deletar proposta';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const calcularRendimento = (
    quantidade: number,
    dilucaoNumerador?: number,
    dilucaoDenominador?: number
  ) => {
    return propostaService.calcularRendimento(quantidade, dilucaoNumerador, dilucaoDenominador);
  };

  const calcularCustoPorLitro = (
    precoProduto: number,
    quantidade: number,
    rendimentoTotal: number | null
  ) => {
    return propostaService.calcularCustoPorLitro(precoProduto, quantidade, rendimentoTotal);
  };

  return {
    propostas,
    loading,
    error,
    createProposta,
    getPropostas,
    getPropostaById,
    getPropostasByCliente,
    compartilharProposta,
    updateProposta,
    deleteProposta,
    calcularRendimento,
    calcularCustoPorLitro,
  };
}

