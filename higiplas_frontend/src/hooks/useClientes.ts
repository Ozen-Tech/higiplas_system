// /src/hooks/useClientes.ts
"use client";

import { useState, useEffect } from 'react';
import { apiService } from '@/services/apiService';
import { Cliente, ClienteCreate } from '@/types';
import toast from 'react-hot-toast';

export function useClientes() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchClientes = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.get('/clientes');
      setClientes(data);
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
      setClientes(data);
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
      const newCliente = await apiService.post('/clientes', clienteData);
      setClientes(prev => [...prev, newCliente]);
      toast.success('Cliente criado com sucesso!');
      return newCliente;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao criar cliente';
      toast.error(errorMessage);
      throw err;
    }
  };

  const updateCliente = async (id: number, clienteData: Partial<Cliente>) => {
    try {
      const updatedCliente = await apiService.put(`/clientes/${id}`, clienteData);
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
      return response.data;
    } catch (err: unknown) {
      const errorMessage = err instanceof Error && 'response' in err && err.response && typeof err.response === 'object' && 'data' in err.response && err.response.data && typeof err.response.data === 'object' && 'detail' in err.response.data ? (err.response.data as any).detail : 'Erro ao buscar cliente';
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