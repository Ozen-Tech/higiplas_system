// Hook para gerenciar estado do entregador (operador)
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { apiService } from '@/services/apiService';

export interface Usuario {
  id: number;
  nome: string;
  email: string;
  perfil: string;
  empresa_id: number;
  is_active: boolean;
}

export function useEntregador() {
  const router = useRouter();
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const carregarUsuario = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.get('/users/me');
      const data = response?.data || response;
      
      if (!data) {
        throw new Error('Usuário não encontrado');
      }
      
      // Verificar se é operador (entregador)
      if (data.perfil !== 'OPERADOR') {
        throw new Error('Acesso negado. Apenas entregadores podem acessar esta área.');
      }
      
      setUsuario(data);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMessage = error?.response?.data?.detail || error?.message || 'Erro ao carregar dados do usuário';
      setError(errorMessage);
      // Redirecionar para login se não autenticado
      if (errorMessage.includes('401') || errorMessage.includes('não encontrado')) {
        localStorage.removeItem('authToken');
        router.push('/entregador/login');
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    // Verificar se há token
    const token = localStorage.getItem('authToken');
    if (!token) {
      router.push('/entregador/login');
      return;
    }
    
    carregarUsuario();
  }, [carregarUsuario, router]);

  const logout = useCallback(() => {
    localStorage.removeItem('authToken');
    router.push('/entregador/login');
  }, [router]);

  return {
    usuario,
    loading,
    error,
    isOperador: usuario?.perfil === 'OPERADOR',
    carregarUsuario,
    logout,
  };
}

