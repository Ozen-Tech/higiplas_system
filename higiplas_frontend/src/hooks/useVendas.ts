 // /src/hooks/useVendas.ts - VERSÃO ATUALIZADA

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
// ATENÇÃO: Importe o tipo ClienteV2 que é o correto para a nova API de clientes
import { ClienteV2 } from '@/types';
import { Dashboard, Cliente, Produto, VendaCreate, VendaResponse } from '@/types/vendas';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';

export function useVendas() {
  const router = useRouter();
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleApiError = useCallback((err: unknown) => {
    // ... (função de erro existente, sem alterações)
    const errorMessage = err instanceof Error ? err.message : "Ocorreu um erro desconhecido.";
    if (errorMessage.includes("[401]")) {
      localStorage.removeItem("authToken");
      router.push('/');
      setError("Sessão expirou. Faça login novamente.");
      toast.error("Sua sessão expirou. Por favor, faça login novamente.");
    } else {
      setError(errorMessage);
    }
  }, [router]);

  // Carregar dashboard (sem alterações)
  const carregarDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.get('/vendas/dashboard');
      setDashboard(data?.data || data);
    } catch (err) {
      handleApiError(err);
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Buscar clientes (sem alterações)
  const buscarClientes = useCallback(async (termo?: string, bairro?: string) => {
    try {
      setLoading(true);
      setError(null);
      let url = '/vendas/clientes/busca-rapida?limit=50';
      if (termo) url += `&termo=${encodeURIComponent(termo)}`;
      if (bairro) url += `&bairro=${encodeURIComponent(bairro)}`;
      const data = await apiService.get(url);
      setClientes(data?.data || data || []);
    } catch (err) {
      handleApiError(err);
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // Buscar produtos (sem alterações)
  const buscarProdutos = useCallback(async (busca?: string, categoria?: string) => {
    try {
      setLoading(true);
      setError(null);
      let url = '/vendas/produtos/disponiveis';
      const params = new URLSearchParams();
      if (busca) params.append('busca', busca);
      if (categoria) params.append('categoria', categoria);
      if (params.toString()) url += `?${params.toString()}`;
      const data = await apiService.get(url);
      setProdutos(data?.data || data || []);
    } catch (err) {
      handleApiError(err);
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  // ===== ADIÇÃO IMPORTANTE: Função para criar cliente rápido =====
  const criarClienteRapido = useCallback(async (nome: string, telefone: string): Promise<ClienteV2 | null> => {
    setLoading(true);
    try {
      // Chama o endpoint POST /clientes/quick que já existe no seu backend
      const response = await apiService.post('/clientes/quick', { nome, telefone });
      toast.success('Cliente criado com sucesso!');
      return response?.data || null;
    } catch (err) {
      handleApiError(err);
      return null;
    } finally {
        setLoading(false);
    }
  }, [handleApiError]);

  // Nova função para criar cliente com todos os campos
  const criarClienteCompleto = useCallback(async (
    nome: string,
    telefone: string,
    cnpj?: string,
    email?: string,
    bairro?: string,
    cidade?: string
  ): Promise<ClienteV2 | null> => {
    setLoading(true);
    try {
      // Chama o endpoint POST /clientes para criar cliente completo
      // O schema espera: nome, telefone, tipo_pessoa, e campos opcionais
      const payload: {
        nome: string;
        telefone: string;
        tipo_pessoa: string;
        cpf_cnpj?: string;
        email?: string;
        bairro?: string;
        cidade?: string;
      } = {
        nome,
        telefone,
        tipo_pessoa: cnpj ? "JURIDICA" : "FISICA"
      };
      
      // Adicionar campos opcionais apenas se fornecidos
      if (cnpj && cnpj.trim()) payload.cpf_cnpj = cnpj.trim();
      if (email && email.trim()) payload.email = email.trim();
      if (bairro && bairro.trim()) payload.bairro = bairro.trim();
      if (cidade && cidade.trim()) payload.cidade = cidade.trim();
      const response = await apiService.post('/clientes', payload);
      toast.success('Cliente criado com sucesso!');
      return response?.data || null;
    } catch (err) {
      handleApiError(err);
      return null;
    } finally {
        setLoading(false);
    }
  }, [handleApiError]);

  // Registrar venda (sem alterações)
  const registrarVenda = useCallback(async (venda: VendaCreate): Promise<VendaResponse> => {
    // ...
    setLoading(true);
    try {
      const data = await apiService.post('/vendas/registrar', venda);
      const resultado = data?.data || data;
      toast.success(`Venda registrada! Total: R$ ${resultado.total_venda.toFixed(2)}`);
      carregarDashboard();
      return resultado;
    } catch (err) {
      handleApiError(err);
      const errorMsg = err instanceof Error ? err.message : 'Erro ao registrar venda';
      toast.error(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [handleApiError, carregarDashboard]);

  return {
    dashboard,
    clientes,
    produtos,
    loading,
    error,
    carregarDashboard,
    buscarClientes,
    buscarProdutos,
    criarClienteRapido, // <-- Exporta a nova função
    criarClienteCompleto,
    registrarVenda,
  };
}