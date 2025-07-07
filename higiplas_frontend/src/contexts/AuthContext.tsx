// /frontend/src/contexts/AuthContext.tsx
"use client";

import { createContext, useContext, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

interface AuthContextType {
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();

  const logout = () => {
    if (confirm("Tem certeza que deseja sair?")) {
      localStorage.removeItem("authToken");
      router.push('/');
    }
  };

  return (
    <AuthContext.Provider value={{ logout }}>
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