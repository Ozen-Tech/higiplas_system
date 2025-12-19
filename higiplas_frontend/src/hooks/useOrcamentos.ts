// /src/hooks/useOrcamentos.ts

import { useState, useCallback } from 'react';
import { apiService } from '@/services/apiService';
import { Orcamento, OrcamentoCreatePayload, OrcamentoUpdate } from '@/types/orcamentos';
import toast from 'react-hot-toast';
import { useRouter } from 'next/navigation';

export function useOrcamentos() {
  const router = useRouter();
  const [orcamentos, setOrcamentos] = useState<Orcamento[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Função genérica para tratamento de erros
  const handleApiError = useCallback((err: unknown, defaultMessage: string) => {
    const errorMessage = err instanceof Error ? err.message : defaultMessage;
    if (errorMessage.includes("[401]")) {
      toast.error("Sessão expirada. Faça login novamente.");
      localStorage.removeItem("authToken");
      router.push('/');
    } else {
      toast.error(errorMessage);
    }
    setError(errorMessage);
  }, [router]);

  // Busca o histórico de orçamentos do vendedor logado
  const listarOrcamentosVendedor = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiService.get('/orcamentos/me/');
      setOrcamentos(response?.data || []);
    } catch (err) {
      handleApiError(err, 'Erro ao buscar histórico de orçamentos.');
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Cria um novo orçamento no backend
  const criarOrcamento = useCallback(async (payload: OrcamentoCreatePayload): Promise<Orcamento | null> => {
    setLoading(true);
    try {
      const response = await apiService.post('/orcamentos/', payload);
      toast.success('Orçamento salvo com sucesso!');
      return response?.data || null;
    } catch (err) {
      handleApiError(err, 'Erro ao salvar o orçamento.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Funções admin - listar todos os orçamentos
  const listarTodosOrcamentos = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiService.get('/orcamentos/admin/todos');
      setOrcamentos(response?.data || []);
      return response?.data || [];
    } catch (err) {
      handleApiError(err, 'Erro ao buscar orçamentos.');
      return [];
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Buscar orçamento específico por ID
  const buscarOrcamento = useCallback(async (orcamentoId: number): Promise<Orcamento | null> => {
    setLoading(true);
    try {
      const response = await apiService.get(`/orcamentos/${orcamentoId}`);
      return response?.data || null;
    } catch (err) {
      handleApiError(err, 'Erro ao buscar orçamento.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Editar orçamento (admin)
  const editarOrcamento = useCallback(async (
    orcamentoId: number,
    update: OrcamentoUpdate
  ): Promise<Orcamento | null> => {
    setLoading(true);
    try {
      const response = await apiService.put(`/orcamentos/${orcamentoId}`, update);
      toast.success('Orçamento atualizado com sucesso!');
      return response?.data || null;
    } catch (err) {
      handleApiError(err, 'Erro ao atualizar orçamento.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Atualizar status do orçamento (admin)
  const atualizarStatus = useCallback(async (
    orcamentoId: number,
    status: string
  ): Promise<Orcamento | null> => {
    setLoading(true);
    try {
      const response = await apiService.patch(`/orcamentos/${orcamentoId}/status`, { status });
      toast.success('Status atualizado com sucesso!');
      return response?.data || null;
    } catch (err) {
      handleApiError(err, 'Erro ao atualizar status do orçamento.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Confirmar orçamento e opcionalmente dar baixa no estoque (admin)
  const confirmarOrcamento = useCallback(async (
    orcamentoId: number, 
    baixarEstoque: boolean = true
  ): Promise<Orcamento | null> => {
    setLoading(true);
    try {
      const response = await apiService.post(
        `/orcamentos/${orcamentoId}/confirmar?baixar_estoque=${baixarEstoque}`, 
        {}
      );
      
      if (baixarEstoque) {
        toast.success('Orçamento confirmado e baixa de estoque realizada com sucesso!');
      } else {
        toast.success('Orçamento confirmado! Histórico do cliente registrado (estoque não alterado).');
      }
      
      return response?.data || null;
    } catch (err) {
      handleApiError(err, 'Erro ao confirmar orçamento.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Excluir orçamento (admin)
  const excluirOrcamento = useCallback(async (orcamentoId: number): Promise<boolean> => {
    setLoading(true);
    try {
      await apiService.delete(`/orcamentos/${orcamentoId}`);
      toast.success('Orçamento excluído com sucesso!');
      return true;
    } catch (err) {
      handleApiError(err, 'Erro ao excluir orçamento.');
      return false;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  return {
    orcamentos,
    loading,
    error,
    listarOrcamentosVendedor,
    criarOrcamento,
    // Funções admin
    listarTodosOrcamentos,
    buscarOrcamento,
    editarOrcamento,
    atualizarStatus,
    confirmarOrcamento,
    excluirOrcamento,
  };
}