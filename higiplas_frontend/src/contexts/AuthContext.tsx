"use client";

import { createContext, useContext, ReactNode, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { apiService } from '@/services/apiService';
import { User } from '@/types';
import toast from 'react-hot-toast'; // <-- 1. Importar o toast

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
      // --- 2. ADICIONAR O TOAST DE ERRO AQUI ---
      console.error("Falha ao buscar usuário, limpando token.", error);
      localStorage.removeItem("authToken");
      setUser(null);
      toast.error("Sua sessão expirou. Por favor, faça login novamente."); // <-- Notificação para o usuário
      router.push('/'); // Garante o redirecionamento
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

  const logout = () => {
    if (confirm("Tem certeza que deseja sair?")) {
      localStorage.removeItem("authToken");
      setUser(null);
      toast.success("Você saiu com sucesso!"); // <-- Feedback positivo no logout
      router.push('/');
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