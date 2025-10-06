// /src/hooks/useClientesV2.ts
"use client";

import { useState, useEffect } from 'react';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';
import {
  ClienteV2,
  ClienteQuickCreate,
  ClienteUpdateV2,
  ClienteListItemV2,
  ClienteStats,
  ClienteSearchParams
} from '@/types';

export function useClientesV2() {
  const [clientes, setClientes] = useState<ClienteListItemV2[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ============= CRIAÇÃO RÁPIDA =============
  
  const createClienteQuick = async (clienteData: ClienteQuickCreate): Promise<ClienteV2> => {
    try {
      setLoading(true);
      const response = await apiService.post('/clientes/quick', clienteData);
      const newCliente = response?.data;
      
      if (!newCliente) {
        throw new Error('Erro ao criar cliente');
      }
      
      // Adicionar à lista local
      const listItem: ClienteListItemV2 = {
        id: newCliente.id,
        nome: newCliente.nome,
        telefone: newCliente.telefone,
        bairro: newCliente.bairro,
        cidade: newCliente.cidade,
        status: newCliente.status,
        ultima_venda: newCliente.ultima_venda
      };
      
      setClientes(prev => [listItem, ...prev]);
      toast.success('Cliente criado rapidamente!');
      return newCliente;
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao criar cliente';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // ============= CRIAÇÃO COMPLETA =============
  
  const createCliente = async (clienteData: { nome: string; telefone: string; tipo_pessoa?: string; cpf_cnpj?: string; bairro?: string; cidade?: string; observacoes?: string; referencia_localizacao?: string }): Promise<ClienteV2> => {
    try {
      setLoading(true);
      const response = await apiService.post('/clientes/', clienteData);
      const newCliente = response?.data;
      
      if (!newCliente) {
        throw new Error('Erro ao criar cliente');
      }
      
      // Adicionar à lista local
      const listItem: ClienteListItemV2 = {
        id: newCliente.id,
        nome: newCliente.nome,
        telefone: newCliente.telefone,
        bairro: newCliente.bairro,
        cidade: newCliente.cidade,
        status: newCliente.status,
        ultima_venda: newCliente.ultima_venda
      };
      
      setClientes(prev => [listItem, ...prev]);
      toast.success('Cliente criado com sucesso!');
      return newCliente;
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao criar cliente';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // ============= LISTAGEM E BUSCA =============
  
  const fetchClientes = async (params: ClienteSearchParams = {}): Promise<ClienteListItemV2[]> => {
    try {
      setLoading(true);
      setError(null);
      
      const queryParams = new URLSearchParams();
      if (params.search) queryParams.append('search', params.search);
      if (params.bairro) queryParams.append('bairro', params.bairro);
      if (params.cidade) queryParams.append('cidade', params.cidade);
      if (params.meus_clientes) queryParams.append('meus_clientes', 'true');
      queryParams.append('skip', (params.skip || 0).toString());
      queryParams.append('limit', (params.limit || 50).toString());
      
      const url = `/clientes/?${queryParams.toString()}`;
      const data = await apiService.get(url);
      const clientesList = Array.isArray(data) ? data : [];
      
      setClientes(clientesList);
      return clientesList;
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar clientes';
      setError(errorMessage);
      toast.error(errorMessage);
      return [];
    } finally {
      setLoading(false);
    }
  };

  const searchClientes = async (searchTerm: string): Promise<ClienteListItemV2[]> => {
    return await fetchClientes({ search: searchTerm, limit: 20 });
  };

  const getClientesByBairro = async (bairro: string): Promise<ClienteListItemV2[]> => {
    return await fetchClientes({ bairro, limit: 30 });
  };

  const getMeusClientes = async (): Promise<ClienteListItemV2[]> => {
    return await fetchClientes({ meus_clientes: true, limit: 100 });
  };

  // ============= OPERAÇÕES INDIVIDUAIS =============
  
  const getClienteById = async (id: number): Promise<ClienteV2 | null> => {
    try {
      setLoading(true);
      const response = await apiService.get(`/clientes/${id}`);
      return response?.data || null;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao buscar cliente';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const updateCliente = async (id: number, clienteData: ClienteUpdateV2): Promise<ClienteV2 | null> => {
    try {
      setLoading(true);
      const response = await apiService.put(`/clientes/${id}`, clienteData);
      const updatedCliente = response?.data;
      
      if (updatedCliente) {
        // Atualizar na lista local
        setClientes(prev => prev.map(cliente => 
          cliente.id === id 
            ? {
                ...cliente,
                nome: updatedCliente.nome,
                telefone: updatedCliente.telefone,
                bairro: updatedCliente.bairro,
                cidade: updatedCliente.cidade,
                status: updatedCliente.status
              }
            : cliente
        ));
        toast.success('Cliente atualizado com sucesso!');
      }
      
      return updatedCliente;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao atualizar cliente';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteCliente = async (id: number): Promise<void> => {
    try {
      setLoading(true);
      await apiService.delete(`/clientes/${id}`);
      
      // Remover da lista local
      setClientes(prev => prev.filter(cliente => cliente.id !== id));
      toast.success('Cliente removido com sucesso!');
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao remover cliente';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // ============= FUNCIONALIDADES EXTRAS =============
  
  const getClienteStats = async (id: number): Promise<ClienteStats | null> => {
    try {
      setLoading(true);
      const response = await apiService.get(`/clientes/${id}/stats`);
      return response?.data || null;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar estatísticas';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const searchNearbyClientes = async (bairro: string): Promise<ClienteListItemV2[]> => {
    try {
      const response = await apiService.get(`/clientes/search/nearby?bairro=${encodeURIComponent(bairro)}&limit=20`);
      return Array.isArray(response) ? response : [];
    } catch (err) {
      console.error('Erro ao buscar clientes próximos:', err);
      return [];
    }
  };

  const bulkCreateClientes = async (clientes: { nome: string; telefone: string; tipo_pessoa?: string; cpf_cnpj?: string; bairro?: string; cidade?: string; observacoes?: string; referencia_localizacao?: string }[]): Promise<{ criados: number; clientes: number[] }> => {
    try {
      setLoading(true);
      const response = await apiService.post('/clientes/bulk', { clientes });
      
      if (response?.data) {
        toast.success(`${response.data.criados || 0} clientes criados!`);
        // Recarregar lista
        await fetchClientes();
      }
      
      return response?.data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro na criação em lote';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // ============= EFEITOS =============
  
  useEffect(() => {
    fetchClientes();
  }, []);

  return {
    // Estado
    clientes,
    loading,
    error,
    
    // Criação
    createClienteQuick,
    createCliente,
    bulkCreateClientes,
    
    // Busca e listagem
    fetchClientes,
    searchClientes,
    getClientesByBairro,
    getMeusClientes,
    searchNearbyClientes,
    
    // Operações individuais
    getClienteById,
    updateCliente,
    deleteCliente,
    
    // Extras
    getClienteStats,
  };
}
