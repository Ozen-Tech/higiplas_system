// /src/hooks/useClientesV2.ts
"use client";

import { useState, useEffect } from 'react';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';

// Tipos simplificados para o sistema v2
export interface ClienteV2 {
  id: number;
  nome: string;
  telefone: string;
  tipo_pessoa: 'FISICA' | 'JURIDICA';
  cpf_cnpj?: string;
  bairro?: string;
  cidade?: string;
  observacoes?: string;
  referencia_localizacao?: string;
  status: 'ATIVO' | 'INATIVO' | 'PROSPECTO';
  vendedor_id: number;
  vendedor_nome?: string;
  empresa_id: number;
  total_vendas?: number;
  ultima_venda?: string;
  criado_em: string;
  atualizado_em?: string;
}

export interface ClienteQuickCreate {
  nome: string;
  telefone: string;
}

export interface ClienteCreate {
  nome: string;
  telefone: string;
  tipo_pessoa?: 'FISICA' | 'JURIDICA';
  cpf_cnpj?: string;
  bairro?: string;
  cidade?: string;
  observacoes?: string;
  referencia_localizacao?: string;
}

export interface ClienteUpdate {
  nome?: string;
  telefone?: string;
  tipo_pessoa?: 'FISICA' | 'JURIDICA';
  cpf_cnpj?: string;
  bairro?: string;
  cidade?: string;
  observacoes?: string;
  referencia_localizacao?: string;
  status?: 'ATIVO' | 'INATIVO' | 'PROSPECTO';
}

export interface ClienteListItem {
  id: number;
  nome: string;
  telefone: string;
  bairro?: string;
  cidade?: string;
  status: 'ATIVO' | 'INATIVO' | 'PROSPECTO';
  ultima_venda?: string;
}

export interface ClienteStats {
  total_orcamentos: number;
  total_vendido: number;
  ticket_medio: number;
  produtos_mais_comprados: Array<{
    produto: string;
    quantidade: number;
    valor_total: number;
  }>;
  historico_vendas: Array<{
    data: string;
    valor: number;
    id: number;
  }>;
}

export interface ClienteSearchParams {
  search?: string;
  bairro?: string;
  cidade?: string;
  meus_clientes?: boolean;
  skip?: number;
  limit?: number;
}

export function useClientesV2() {
  const [clientes, setClientes] = useState<ClienteListItem[]>([]);
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
      const listItem: ClienteListItem = {
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
  
  const createCliente = async (clienteData: ClienteCreate): Promise<ClienteV2> => {
    try {
      setLoading(true);
      const response = await apiService.post('/clientes/', clienteData);
      const newCliente = response?.data;
      
      if (!newCliente) {
        throw new Error('Erro ao criar cliente');
      }
      
      // Adicionar à lista local
      const listItem: ClienteListItem = {
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
  
  const fetchClientes = async (params: ClienteSearchParams = {}): Promise<ClienteListItem[]> => {
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

  const searchClientes = async (searchTerm: string): Promise<ClienteListItem[]> => {
    return await fetchClientes({ search: searchTerm, limit: 20 });
  };

  const getClientesByBairro = async (bairro: string): Promise<ClienteListItem[]> => {
    return await fetchClientes({ bairro, limit: 30 });
  };

  const getMeusClientes = async (): Promise<ClienteListItem[]> => {
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

  const updateCliente = async (id: number, clienteData: ClienteUpdate): Promise<ClienteV2 | null> => {
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

  const searchNearbyClientes = async (bairro: string): Promise<any[]> => {
    try {
      const response = await apiService.get(`/clientes/search/nearby?bairro=${encodeURIComponent(bairro)}&limit=20`);
      return Array.isArray(response) ? response : [];
    } catch (err) {
      console.error('Erro ao buscar clientes próximos:', err);
      return [];
    }
  };

  const bulkCreateClientes = async (clientes: ClienteCreate[]): Promise<any> => {
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
