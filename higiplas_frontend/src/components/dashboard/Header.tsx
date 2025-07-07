// /src/components/dashboard/Header.tsx
"use client";

import { ReactNode } from "react";
import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext"; // Usando nosso novo hook!
import { ThemeToggleButton } from "@/components/ThemeToggleButton";

// Interface para children, tornando o Header um componente de layout
interface HeaderProps {
  title: string;
  actions?: ReactNode; // Ações específicas da página (botões)
}

export function Header({ title, actions }: HeaderProps) {
  const { logout } = useAuth(); // A lógica de logout vem do contexto!

  return (
    <header className="flex flex-col sm:flex-row items-center justify-between gap-4 w-full px-4 md:px-8 py-4 border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm sticky top-0 z-20">
      
      {/* Grupo Esquerdo: Logo e Título */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard" passHref>
            <Image 
                src="/HIGIPLAS-LOGO-2048x761.png" 
                alt="Logo Higiplas" 
                width={130} 
                height={45} 
                priority 
            />
        </Link>
        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100 hidden sm:block">
          | {title}
        </h1>
      </div>

      {/* Grupo Direito: Ações da página + Ações Globais */}
      <div className="flex items-center gap-3">
        {actions} {/* Renderiza os botões específicos da página */}
        
        <div className="flex items-center gap-3 border-l border-gray-300 dark:border-gray-600 ml-3 pl-3">
            <ThemeToggleButton />
            <button 
                onClick={logout} 
                className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-800/50 hover:text-red-600 dark:hover:text-red-400 transition-colors" 
                aria-label="Sair do sistema"
            >
                {/* Heroicon: ArrowLeftOnRectangle */}
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
                </svg>
            </button>
        </div>
      </div>
    </header>
  );
}