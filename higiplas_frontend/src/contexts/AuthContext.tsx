"use client";

import { createContext, useContext, ReactNode, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { apiService } from '@/services/apiService';
import { User } from '@/types';
import toast from 'react-hot-toast';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    try {
      const userData = await apiService.get('/users/me');
      setUser(userData?.data || null);
    } catch (error) {
      console.error("Falha ao buscar usuário, limpando tokens.", error);
      localStorage.removeItem("authToken");
      localStorage.removeItem("refreshToken");
      setUser(null);
      toast.error("Sua sessão expirou. Por favor, faça login novamente.");
      router.push('/');
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [fetchUser]);

  const logout = async () => {
    if (confirm("Tem certeza que deseja sair?")) {
      try {
        const refreshToken = localStorage.getItem("refreshToken");

        // Tenta revogar o refresh token no backend
        if (refreshToken) {
          await apiService.post('/users/logout', { refresh_token: refreshToken }).catch(() => {
            // Ignora erros ao fazer logout no backend
          });
        }
      } catch (error) {
        console.error("Erro ao fazer logout:", error);
      } finally {
        // Sempre limpa os tokens localmente
        localStorage.removeItem("authToken");
        localStorage.removeItem("refreshToken");
        setUser(null);
        toast.success("Você saiu com sucesso!");
        router.push('/');
      }
    }
  };

  const contextValue = { user, loading, logout };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
}