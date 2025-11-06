// Hook para gerenciar estado do vendedor
import { useState, useEffect, useCallback } from 'react';
import { vendedorService, Usuario } from '@/services/vendedorService';
import { useRouter } from 'next/navigation';

export function useVendedor() {
  const router = useRouter();
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const carregarUsuario = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await vendedorService.getMe();
      if (!data) {
        throw new Error('Usuário não encontrado');
      }
      
      // Verificar se é vendedor
      if (!vendedorService.isVendedor(data.perfil)) {
        throw new Error('Acesso negado. Apenas vendedores podem acessar esta área.');
      }
      
      setUsuario(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar dados do usuário';
      setError(errorMessage);
      // Redirecionar para login se não autenticado
      if (errorMessage.includes('401') || errorMessage.includes('não encontrado')) {
        localStorage.removeItem('authToken');
        router.push('/vendedor/login');
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    // Verificar se há token
    const token = localStorage.getItem('authToken');
    if (!token) {
      router.push('/vendedor/login');
      return;
    }
    
    carregarUsuario();
  }, [carregarUsuario, router]);

  const logout = useCallback(() => {
    localStorage.removeItem('authToken');
    router.push('/vendedor/login');
  }, [router]);

  return {
    usuario,
    loading,
    error,
    isVendedor: usuario ? vendedorService.isVendedor(usuario.perfil) : false,
    carregarUsuario,
    logout,
  };
}

