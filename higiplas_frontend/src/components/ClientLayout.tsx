// /frontend/src/components/ClientLayout.tsx
"use client";

import { useEffect, useState, ReactNode } from "react";
import { useRouter } from 'next/navigation';

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
    } else {
      setIsAuthenticated(true);
    }
    setIsLoading(false);
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