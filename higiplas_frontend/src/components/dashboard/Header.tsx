// /src/components/dashboard/Header.tsx
"use client";

import { ReactNode } from "react";
import Image from "next/image";
import Link from "next/link";
import { ThemeToggleButton } from "@/components/ThemeToggleButton";
import AuthenticatedHeaderActions from "./AuthenticatedHeaderActions"; // Importa nosso novo componente

interface HeaderProps {
  title: string;
  actions?: ReactNode;
  isAuthenticated?: boolean;
}

export function Header({ title, actions, isAuthenticated = false }: HeaderProps) {
  // NENHUMA CHAMADA a useAuth() AQUI!
  
  return (
    <header className="flex flex-col sm:flex-row items-center justify-between gap-4 w-full px-4 md:px-8 py-4 border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm sticky top-0 z-20">
      
      <div className="flex items-center gap-4">
        <Link href={isAuthenticated ? "/dashboard" : "/"} passHref>
          <Image 
              src="/HIGIPLAS-LOGO-2048x761.png" 
              alt="Logo Higiplas" 
              width={130} 
              height={45} 
              priority 
          />
        </Link>
        {isAuthenticated && (
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100 hidden sm:block">
            | {title}
          </h1>
        )}
      </div>

      <div className="flex items-center gap-3">
        {isAuthenticated ? (
          // Renderiza o componente que DE FATO usa o hook
          <AuthenticatedHeaderActions pageActions={actions} />
        ) : (
          // Na versão pública, renderizamos apenas o botão de tema.
          <ThemeToggleButton />
        )}
      </div>
    </header>
  );
}