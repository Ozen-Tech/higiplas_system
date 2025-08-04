// /src/app/dashboard/orcamentos/page.tsx
"use client";

import Link from 'next/link';
import { Header } from "@/components/dashboard/Header";
import ClientLayout from '@/components/ClientLayout';
import { ClipboardDocumentListIcon, DocumentPlusIcon } from '@heroicons/react/24/outline';
import { useAuth } from '@/contexts/AuthContext';
import { ThemeToggleButton } from '@/components/ThemeToggleButton';

function OrcamentosPageContent() {
  const { logout } = useAuth();

  return (
    <>
      <Header>
        <h1 className="text-xl font-bold">Gerenciador de Orçamentos</h1>
        <div className="flex-1" />
        <div className="flex items-center gap-2 border-l border-gray-300 dark:border-gray-600 ml-2 pl-2">
            <ThemeToggleButton />
            <button onClick={logout} aria-label="Sair" className="p-2 rounded-md ...">
                <svg>...</svg> {/* Ícone de sair */}
            </button>
        </div>
      </Header>

      <main className="flex-1 p-4 sm:p-6 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* Card 1: Criar Novo Orçamento */}
          <Link href="/dashboard/orcamentos/novo" className="block p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-blue-500">
            <div className="flex items-center gap-4">
                <DocumentPlusIcon className="w-10 h-10 text-blue-500" />
                <div>
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Criar Novo Orçamento</h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Comece a montar uma nova cotação para um cliente.</p>
                </div>
            </div>
          </Link>

          {/* Card 2: Visualizar Orçamentos */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border-l-4 border-gray-400">
             <div className="flex items-center gap-4">
                <ClipboardDocumentListIcon className="w-10 h-10 text-gray-400" />
                 <div>
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Meus Orçamentos</h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Veja e gerencie seus orçamentos salvos. (Em breve)</p>
                </div>
             </div>
          </div>

        </div>
        
        {/* Placeholder para a lista de orçamentos no futuro */}
        <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">Orçamentos Recentes</h3>
            <p className="text-center text-gray-500 dark:text-gray-400">A lista com seus orçamentos salvos aparecerá aqui.</p>
        </div>
      </main>
    </>
  );
}

// O wrapper para proteção continua igual
export default function OrcamentosPageWrapper() {
  return (
    <ClientLayout>
      <OrcamentosPageContent />
    </ClientLayout>
  );
}