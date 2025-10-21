// higiplas_frontend/src/hooks/usePropostas.ts

import { useState, useCallback } from 'react';
import { apiService } from '@/services/apiService';
import { Proposta, PropostaCreatePayload } from '@/types/propostas';
import toast from 'react-hot-toast';
import { useRouter } from 'next/navigation';

export function usePropostas() {
  const router = useRouter();
  const [propostas, setPropostas] = useState<Proposta[]>([]);
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

  // Busca o histórico de propostas do vendedor logado
  const listarPropostasVendedor = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiService.get('/propostas/me/');
      setPropostas(response?.data || []);
    } catch (err) {
      handleApiError(err, 'Erro ao buscar histórico de propostas.');
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Cria uma nova proposta no backend
  const criarProposta = useCallback(async (payload: PropostaCreatePayload): Promise<Proposta | null> => {
    setLoading(true);
    try {
      const response = await apiService.post('/propostas/', payload);
      toast.success('Proposta salva com sucesso!');
      return response?.data || null;
    } catch (err) {
      handleApiError(err, 'Erro ao salvar a proposta.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Gera e baixa o PDF da proposta
  const gerarPDFProposta = useCallback(async (propostaId: number): Promise<Blob | null> => {
    setLoading(true);
    try {
      const response = await apiService.getBlob(`/propostas/${propostaId}/pdf/`);
      const blob = await response.blob();
      return blob;
    } catch (err) {
      handleApiError(err, 'Erro ao gerar PDF da proposta.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  return {
    propostas,
    loading,
    error,
    listarPropostasVendedor,
    criarProposta,
    gerarPDFProposta,
  };
}
