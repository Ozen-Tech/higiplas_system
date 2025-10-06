// /src/hooks/useVendas.ts
// VERSÃO AJUSTADA - 100% compatível com seu sistema

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
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

  // Handler de erro idêntico ao seu useProducts
  const handleApiError = useCallback((err: unknown) => {
    const errorMessage = err instanceof Error ? err.message : "Ocorreu um erro desconhecido.";

    // Verifica se o erro é de autenticação (401 Unauthorized)
    if (errorMessage.includes("[401]")) {
      localStorage.removeItem("authToken");
      router.push('/');
      setError("Sessão expirou. Faça login novamente.");
      toast.error("Sua sessão expirou. Por favor, faça login novamente.");
    } else {
      setError(errorMessage);
    }
  }, [router]);

  // Carregar dashboard
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

  // Buscar clientes
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

  // Buscar produtos
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

  // Criar cliente rápido (novo endpoint que precisamos criar)
  const criarClienteRapido = useCallback(async (nome: string, telefone: string): Promise<Cliente | null> => {
    try {
      const data = await apiService.post('/clientes/quick', { nome, telefone });
      toast.success('Cliente criado com sucesso!');
      return data?.data || data;
    } catch (err) {
      handleApiError(err);
      toast.error('Erro ao criar cliente');
      return null;
    }
  }, [handleApiError]);

  // Registrar venda
  const registrarVenda = useCallback(async (venda: VendaCreate): Promise<VendaResponse> => {
    setLoading(true);
    
    try {
      const data = await apiService.post('/vendas/registrar', venda);
      const resultado = data?.data || data;
      
      toast.success(`Venda registrada! Total: R$ ${resultado.total_venda.toFixed(2)}`);
      
      // Atualizar dashboard após venda
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
    criarClienteRapido,
    registrarVenda,
  };
}