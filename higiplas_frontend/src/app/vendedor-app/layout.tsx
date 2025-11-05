// /src/app/vendedor-app/layout.tsx
// Layout isolado para vendedores com proteção de rota

'use client';

import { useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function VendedorAppLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    if (!authLoading) {
      const token = localStorage.getItem("authToken");
      
      if (!token) {
        router.replace('/');
        return;
      }

      if (user) {
        // Verifica se o usuário é vendedor
        if (user.perfil !== 'VENDEDOR') {
          // Se não for vendedor, redireciona para o dashboard principal
          router.replace('/dashboard');
          return;
        }
      }
      
      setIsChecking(false);
    }
  }, [user, authLoading, router]);

  // Tela de carregamento enquanto verifica autenticação e perfil
  if (authLoading || isChecking) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-100 dark:bg-gray-900">
        <div className="text-center">
          <p className="text-lg">Verificando acesso...</p>
        </div>
      </div>
    );
  }

  // Se o usuário não for vendedor, não renderiza nada (o redirect já foi feito)
  if (user && user.perfil !== 'VENDEDOR') {
    return null;
  }

  // Layout limpo sem sidebar, otimizado para vendedores
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {children}
    </div>
  );
}

