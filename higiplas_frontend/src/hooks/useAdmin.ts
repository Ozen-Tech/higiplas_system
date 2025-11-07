// Hook para gerenciar operações administrativas
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { adminService, UsuarioCreatePayload, Usuario, Empresa } from '@/services/adminService';
import { vendedorService, Usuario as UsuarioType } from '@/services/vendedorService';
import toast from 'react-hot-toast';

export function useAdmin() {
  const router = useRouter();
  const [usuario, setUsuario] = useState<UsuarioType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [empresas, setEmpresas] = useState<Empresa[]>([]);

  const carregarUsuario = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await vendedorService.getMe();
      if (!data) {
        throw new Error('Usuário não encontrado');
      }
      
      // Verificar se é admin
      if (!adminService.isAdmin(data.email)) {
        throw new Error('Acesso negado. Apenas o administrador pode acessar esta área.');
      }
      
      setUsuario(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar dados do usuário';
      setError(errorMessage);
      // Redirecionar para login se não autenticado
      if (errorMessage.includes('401') || errorMessage.includes('não encontrado')) {
        localStorage.removeItem('authToken');
        router.push('/');
      } else if (errorMessage.includes('Acesso negado')) {
        router.push('/dashboard');
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  const carregarEmpresas = useCallback(async () => {
    try {
      const empresasList = await adminService.listarEmpresas();
      setEmpresas(empresasList);
    } catch (err) {
      console.error('Erro ao carregar empresas:', err);
    }
  }, []);

  useEffect(() => {
    // Verificar se há token
    const token = localStorage.getItem('authToken');
    if (!token) {
      router.push('/');
      return;
    }
    
    carregarUsuario();
    carregarEmpresas();
  }, [carregarUsuario, carregarEmpresas, router]);

  const criarUsuario = useCallback(async (payload: UsuarioCreatePayload): Promise<Usuario | null> => {
    setLoading(true);
    try {
      const novoUsuario = await adminService.criarUsuario(payload);
      if (novoUsuario) {
        toast.success(`Usuário ${novoUsuario.nome} criado com sucesso!`);
        return novoUsuario;
      }
      return null;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao criar usuário';
      toast.error(errorMessage);
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('authToken');
    router.push('/');
  }, [router]);

  return {
    usuario,
    loading,
    error,
    isAdmin: usuario ? adminService.isAdmin(usuario.email) : false,
    empresas,
    criarUsuario,
    carregarEmpresas,
    logout,
  };
}

