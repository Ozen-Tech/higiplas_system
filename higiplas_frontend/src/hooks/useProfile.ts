// /src/hooks/useProfile.ts

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { User, UserUpdate, UserPasswordUpdate } from '@/types';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';

export function useProfile() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleApiError = useCallback((err: unknown) => {
    const errorMessage = err instanceof Error ? err.message : "Ocorreu um erro desconhecido.";

    // Verifica se o erro é de autenticação (401 Unauthorized)
    if (errorMessage.includes("[401]")) {
      localStorage.removeItem("authToken");
      router.push('/');
      setError("Sessão expirou. Faça login novamente.");
    } else {
      setError(errorMessage);
    }
  }, [router]);

  const fetchProfile = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiService.get('/users/me');
      setUser(response?.data || null);
      setError(null);
      return response?.data || null;
    } catch (err) {
      handleApiError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  const updateProfile = async (userUpdate: UserUpdate) => {
    const promise = apiService.put('/users/me', userUpdate).then((response) => {
      const updatedUser = response?.data;
      setUser(updatedUser);
      return updatedUser;
    });

    toast.promise(promise, {
      loading: 'Atualizando perfil...',
      success: 'Perfil atualizado com sucesso!',
      error: (err) => `Erro ao atualizar: ${err.message}`,
    });

    return promise;
  };

  const updatePassword = async (passwordUpdate: UserPasswordUpdate): Promise<void> => {
    const promise = apiService.put('/users/me/password', passwordUpdate).then(() => {
      // Não retorna nada, apenas resolve
    });

    toast.promise(promise, {
      loading: 'Alterando senha...',
      success: 'Senha alterada com sucesso!',
      error: (err) => `Erro ao alterar senha: ${err.message}`,
    });

    await promise;
  };

  return {
    user,
    loading,
    error,
    fetchProfile,
    updateProfile,
    updatePassword,
  };
}


