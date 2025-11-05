// /src/hooks/useVendedorOrcamentos.ts
// Hook otimizado para operações de orçamento do vendedor

import { useState, useCallback } from 'react';
import { apiService } from '@/services/apiService';
import { Orcamento, OrcamentoCreatePayload } from '@/types/orcamentos';
import { Product } from '@/types';
import { ClienteV2 } from '@/types';
import toast from 'react-hot-toast';
import { useRouter } from 'next/navigation';

export function useVendedorOrcamentos() {
  const router = useRouter();
  const [orcamentos, setOrcamentos] = useState<Orcamento[]>([]);
  const [produtos, setProdutos] = useState<Product[]>([]);
  const [clientes, setClientes] = useState<Array<ClienteV2 | { id: number; nome: string; telefone: string; bairro?: string; cidade?: string }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  // Busca todos os produtos (sem filtro de estoque)
  const buscarProdutos = useCallback(async () => {
    setLoading(true);
    try {
      setError(null);
      const response = await apiService.get('/produtos/');
      const produtosData = response?.data || [];
      setProdutos(produtosData);
      return produtosData;
    } catch (err) {
      handleApiError(err, 'Erro ao buscar produtos.');
      return [];
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Busca clientes
  const buscarClientes = useCallback(async (termo?: string) => {
    setLoading(true);
    try {
      setError(null);
      let url = '/clientes?meus_clientes=true&limit=50';
      if (termo) url += `&search=${encodeURIComponent(termo)}`;
      const response = await apiService.get(url);
      const clientesData = response?.data || response || [];
      setClientes(clientesData);
      return clientesData;
    } catch (err) {
      handleApiError(err, 'Erro ao buscar clientes.');
      return [];
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Cria cliente rápido
  const criarClienteRapido = useCallback(async (nome: string, telefone: string): Promise<ClienteV2 | null> => {
    setLoading(true);
    try {
      const response = await apiService.post('/clientes/quick', { nome, telefone });
      toast.success('Cliente criado com sucesso!');
      const novoCliente = response?.data || null;
      if (novoCliente) {
        setClientes(prev => [novoCliente, ...prev]);
      }
      return novoCliente;
    } catch (err) {
      handleApiError(err, 'Erro ao criar cliente.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Lista orçamentos do vendedor
  const listarOrcamentos = useCallback(async () => {
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

  // Cria novo orçamento
  const criarOrcamento = useCallback(async (payload: OrcamentoCreatePayload): Promise<Orcamento | null> => {
    setLoading(true);
    try {
      const response = await apiService.post('/orcamentos/', payload);
      toast.success('Orçamento criado com sucesso!');
      const novoOrcamento = response?.data || null;
      if (novoOrcamento) {
        setOrcamentos(prev => [novoOrcamento, ...prev]);
      }
      return novoOrcamento;
    } catch (err) {
      handleApiError(err, 'Erro ao criar o orçamento.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Download PDF do orçamento
  const downloadPDF = useCallback(async (orcamentoId: number): Promise<void> => {
    try {
      const response = await apiService.getBlob(`/orcamentos/${orcamentoId}/pdf/`);
      const blob = await response.blob();

      const contentDisposition = response.headers.get('content-disposition');
      let filename = `orcamento_${orcamentoId}.pdf`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch && filenameMatch.length > 1) {
          filename = filenameMatch[1];
        }
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();

      setTimeout(() => {
        window.URL.revokeObjectURL(url);
        link.remove();
      }, 100);

      toast.success('PDF gerado com sucesso!');
    } catch (err) {
      handleApiError(err, 'Erro ao gerar PDF.');
    }
  }, [handleApiError]);

  return {
    orcamentos,
    produtos,
    clientes,
    loading,
    error,
    buscarProdutos,
    buscarClientes,
    criarClienteRapido,
    listarOrcamentos,
    criarOrcamento,
    downloadPDF,
  };
}

