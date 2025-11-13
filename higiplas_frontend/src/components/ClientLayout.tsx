// /frontend/src/components/ClientLayout.tsx
"use client";

import { useEffect, useState, ReactNode } from "react";
import { useRouter } from 'next/navigation';
import { apiService } from '@/services/apiService';
import { adminService } from '@/services/adminService';

interface ClientLayoutProps {
  children: ReactNode;
}

export default function ClientLayout({ children }: ClientLayoutProps) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Esta verificação só acontece no lado do cliente.
    const token = localStorage.getItem("authToken");

    if (!token) {
      router.replace('/'); // Redireciona para o login
      setIsLoading(false);
      return;
    }

    // Verificar se o usuário é admin ou gestor
    const verificarPermissao = async () => {
      try {
        const userData = await apiService.get('/users/me');
        const usuario = userData?.data || userData;
        
        if (!usuario || !adminService.isAdmin(usuario.perfil)) {
          // Usuário não é admin/gestor, remover token e redirecionar
          localStorage.removeItem('authToken');
          router.replace('/');
          setIsLoading(false);
          return;
        }

        setIsAuthenticated(true);
      } catch {
        // Erro ao verificar usuário, remover token e redirecionar
        localStorage.removeItem('authToken');
        router.replace('/');
      } finally {
        setIsLoading(false);
      }
    };

    verificarPermissao();
  }, [router]);

  // Enquanto verifica a autenticação, mostra uma tela de carregamento.
  // Isso evita o erro de renderização do lado do servidor.
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-100 dark:bg-gray-900">
        <p>Verificando autenticação...</p>
      </div>
    );
  }

  // Só renderiza o conteúdo da página se o usuário estiver autenticado.
  if (isAuthenticated) {
    return <>{children}</>;
  }
  
  // Se não estiver autenticado e o redirect ainda não aconteceu, não renderiza nada.
  return null;
}