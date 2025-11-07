// /src/components/dashboard/Header.tsx
"use client";

import { ReactNode } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { ThemeToggleButton } from "@/components/ThemeToggleButton";

interface HeaderProps {
  // Recebe um 'children' para o conteúdo principal (como título e botões da página)
  children?: ReactNode; 
}

// Micro-componente interno para a barra de usuário
const UserProfileBar = () => {
    const { user, loading } = useAuth();

    if (loading) {
        // Mostra um placeholder enquanto os dados do usuário carregam
        return <div className="w-48 h-8 bg-gray-200 dark:bg-gray-700 rounded-md animate-pulse"></div>;
    }
    
    if (!user) return null; // Não mostra nada se não houver usuário (pouco provável em uma página autenticada)

    return (
        <div className="flex items-center gap-3 pr-3 border-r border-gray-200/50 dark:border-gray-700/50">
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
                {user.nome.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
                <div className="text-sm font-semibold text-gray-800 dark:text-gray-100 truncate">{user.nome}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                    Nível {user.level ?? 1} (XP: {user.xp ?? 0}/100)
                </div>
            </div>
        </div>
    );
};


// Header Principal
export function Header({ children }: HeaderProps) {
    const { logout } = useAuth();
  
    return (
        <header className="flex-shrink-0 flex items-center justify-between w-full h-16 px-4 md:px-8 border-b border-gray-200/50 dark:border-gray-700/50 glass sticky top-0 z-50 transition-all duration-300">
            {/* O conteúdo passado pela página (título, botões de ação) vem aqui */}
            <div className="flex-1 animate-fadeIn">
                {children}
            </div>

            {/* Ações globais sempre presentes no header do dashboard */}
            <div className="flex items-center gap-3 animate-slideUp">
                <UserProfileBar />
                
                <div className="flex items-center gap-1">
                    <ThemeToggleButton />
                    <button 
                        onClick={logout} 
                        className="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-800/50 hover:text-red-600 dark:hover:text-red-400 transition-all duration-200 hover:scale-110 active:scale-95" 
                        aria-label="Sair do sistema"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
                        </svg>
                    </button>
                </div>
            </div>
        </header>
    );
}