// /src/hooks/useClientes.ts
"use client";

import { useState, useEffect } from 'react';
import { apiService } from '@/services/apiService';
import { Cliente, ClienteCreate, ClienteUpdate } from '@/types';
import toast from 'react-hot-toast';

// Função para mapear a resposta da API para o tipo Cliente do frontend
const mapClienteFromApi = (apiCliente: Record<string, any>): Cliente => {
  let parsedEndereco = apiCliente.endereco;
  if (typeof apiCliente.endereco === 'string') {
    try {
      parsedEndereco = JSON.parse(apiCliente.endereco);
    } catch {
      console.error("Falha ao analisar o JSON do endereço:", apiCliente.endereco);
      parsedEndereco = null;
    }
  }

  return {
    id: apiCliente.id,
    nome: apiCliente.razao_social,
    email: apiCliente.email,
    telefone: apiCliente.telefone,
    cpf_cnpj: apiCliente.cnpj,
    tipo_pessoa: apiCliente.cnpj?.length === 14 ? 'JURIDICA' : 'FISICA',
    data_cadastro: apiCliente.data_criacao,
    ativo: apiCliente.status_pagamento === 'BOM_PAGADOR',
    observacoes: apiCliente.observacoes || null,
    empresa_id: apiCliente.empresa_id,
    endereco: parsedEndereco,
    enderecos: apiCliente.enderecos || [],
  };
};

// Função para mapear o objeto do cliente do frontend para o formato da API
const mapToApi = (clienteData: Partial<ClienteCreate & ClienteUpdate>): Record<string, any> => {
  const { nome, cpf_cnpj, ativo, ...rest } = clienteData;
  const apiPayload: Record<string, any> = { ...rest };

  if (nome) apiPayload.razao_social = nome;
  if (cpf_cnpj) apiPayload.cnpj = cpf_cnpj;
  if (ativo !== undefined) {
    apiPayload.status_pagamento = ativo ? 'BOM_PAGADOR' : 'MAU_PAGADOR';
  }
  if (apiPayload.endereco && typeof apiPayload.endereco === 'object') {
    apiPayload.endereco = JSON.stringify(apiPayload.endereco);
  }

  return apiPayload;
};


export function useClientes() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchClientes = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.get('/clientes');
      setClientes(Array.isArray(data) ? data.map(mapClienteFromApi) : []);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar clientes';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const searchClientes = async (query: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.get(`/clientes/search?q=${encodeURIComponent(query)}`);
      setClientes(Array.isArray(data) ? data.map(mapClienteFromApi) : []);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao buscar clientes';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const createCliente = async (clienteData: ClienteCreate) => {
    try {
      const apiPayload = mapToApi(clienteData);
      const newClienteApi = await apiService.post('/clientes', apiPayload);
      const newCliente = mapClienteFromApi(newClienteApi);
      setClientes(prev => [...prev, newCliente]);
      toast.success('Cliente criado com sucesso!');
      return newCliente;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao criar cliente';
      toast.error(errorMessage);
      throw err;
    }
  };

  const updateCliente = async (id: number, clienteData: Partial<ClienteUpdate>) => {
    try {
      const apiPayload = mapToApi(clienteData);
      const updatedClienteApi = await apiService.put(`/clientes/${id}`, apiPayload);
      const updatedCliente = mapClienteFromApi(updatedClienteApi);
      setClientes(prev => prev.map(cliente => 
        cliente.id === id ? updatedCliente : cliente
      ));
      toast.success('Cliente atualizado com sucesso!');
      return updatedCliente;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao atualizar cliente';
      toast.error(errorMessage);
      throw err;
    }
  };

  const deleteCliente = async (id: number) => {
    try {
      await apiService.delete(`/clientes/${id}`);
      setClientes(prev => prev.filter(cliente => cliente.id !== id));
      toast.success('Cliente removido com sucesso!');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao remover cliente';
      toast.error(errorMessage);
      throw err;
    }
  };

  useEffect(() => {
    fetchClientes();
  }, []);

  const getClienteById = async (id: number): Promise<Cliente | null> => {
    try {
      setLoading(true);
      const response = await apiService.get(`/clientes/${id}`);
      return mapClienteFromApi(response);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao buscar cliente';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    clientes,
    loading,
    error,
    fetchClientes,
    searchClientes,
    createCliente,
    updateCliente,
    deleteCliente,
    getClienteById,
  };
}