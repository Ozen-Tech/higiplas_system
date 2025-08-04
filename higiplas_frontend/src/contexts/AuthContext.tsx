// /frontend/src/contexts/AuthContext.tsx
"use client";

import { createContext, useContext, ReactNode, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { apiService } from '@/services/apiService';
import { User } from '@/types'; // Importe nosso novo tipo

interface AuthContextType {
  user: User | null; // O usuário pode ser nulo se não estiver logado
  loading: boolean; // Para saber se estamos carregando os dados do usuário
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true); // Começa carregando

  const fetchUser = useCallback(async () => {
    // Busca os dados do usuário na API usando a rota /users/me
    try {
      const userData = await apiService.get('/users/me');
      setUser(userData);
    } catch (error) {
      console.error("Falha ao buscar usuário, limpando token.", error);
      localStorage.removeItem("authToken"); // Token inválido, limpa
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (token) {
      fetchUser();
    } else {
      setLoading(false); // Se não há token, não há usuário a carregar
    }
  }, [fetchUser]);

  const logout = () => {
    if (confirm("Tem certeza que deseja sair?")) {
      localStorage.removeItem("authToken");
      setUser(null);
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