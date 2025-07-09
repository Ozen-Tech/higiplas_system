"use client";

import { useAuth } from "@/contexts/AuthContext";
import { ThemeToggleButton } from "@/components/ThemeToggleButton";
import { ReactNode } from "react";
import Link from 'next/link'; // Importe o Link do Next.js

interface AuthenticatedHeaderActionsProps {
    pageActions?: ReactNode; // Ações específicas da página
}

export default function AuthenticatedHeaderActions({ pageActions }: AuthenticatedHeaderActionsProps) {
    const { logout } = useAuth();

    return (
        <div className="flex items-center gap-2 sm:gap-4"> {/* Adicionei gap-4 para telas maiores */}

            {/* Ações específicas da página, como 'Exportar Excel' */}
            {pageActions} 

            {/* Botão para a Página de Insights */}
            <Link 
                href="/dashboard/insights"
                className="px-3 py-2 text-sm font-semibold rounded-lg bg-purple-600 text-white hover:bg-purple-700 transition-colors shadow-sm"
            >
                IA Insights
            </Link>

            {/* Seção de Configurações (Sair e Tema) */}
            <div className="flex items-center gap-3 border-l border-gray-300 dark:border-gray-600 ml-3 pl-3">
                <ThemeToggleButton />
                <button 
                    onClick={logout} 
                    className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-800/50 hover:text-red-600 dark:hover:text-red-400 transition-colors" 
                    aria-label="Sair do sistema"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
                    </svg>
                </button>
            </div>
        </div>
    );
}