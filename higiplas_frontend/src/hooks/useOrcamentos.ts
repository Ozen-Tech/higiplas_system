// /src/hooks/useOrcamentos.ts

import { useState, useCallback } from 'react';
import { apiService } from '@/services/apiService';
import { Orcamento, OrcamentoCreatePayload } from '@/types/orcamentos';
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
      if (typeof window !== 'undefined') {
        localStorage.removeItem("authToken");
      }
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

  return {
    orcamentos,
    loading,
    error,
    listarOrcamentosVendedor,
    criarOrcamento,
  };
}