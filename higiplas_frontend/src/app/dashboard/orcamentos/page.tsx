// /src/app/dashboard/orcamentos/page.tsx (ou onde quer que este componente esteja)

"use client";

import Link from 'next/link';
// --- 1. IMPORTAR O useRouter ---
import { useRouter } from 'next/navigation'; 
import { useEffect } from 'react';
import { Header } from "@/components/dashboard/Header";
import ClientLayout from '@/components/ClientLayout';
import { ClipboardDocumentListIcon, DocumentPlusIcon } from '@heroicons/react/24/outline';
import { useAuth } from '@/contexts/AuthContext';
import { ThemeToggleButton } from '@/components/ThemeToggleButton';
import { useOrcamentos } from '@/hooks/useOrcamentos';
import {ArrowUpOnSquareIcon } from '@heroicons/react/24/outline';

// O conteúdo principal da página foi movido para cá.
function OrcamentosPageContent() {
  const { logout } = useAuth();
  const { orcamentos, loading, fetchOrcamentos } = useOrcamentos();
  // --- 2. INICIAR O HOOK DO ROUTER ---
  const router = useRouter(); 

  useEffect(() => {
    fetchOrcamentos();
  }, [fetchOrcamentos]);

  return (
    <>
      <Header>
        <h1 className="text-xl font-bold text-gray-800 dark:text-gray-100">Gerenciador de Orçamentos</h1>
        <div className="flex-1" />
        <div className="flex items-center gap-2 border-l border-gray-300 dark:border-gray-600 ml-2 pl-2">
            <ThemeToggleButton />
            <button onClick={logout} aria-label="Sair" className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-800/50 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
              </svg>
            </button>
        </div>
      </Header>

      <main className="flex-1 p-4 sm:p-6 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto">
          {/* Cards de Ação */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Link href="/dashboard/orcamentos/novo" className="block p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-blue-500">
              <div className="flex items-center gap-4">
                  <DocumentPlusIcon className="w-10 h-10 text-blue-500" />
                  <div>
                      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Criar Novo Orçamento</h2>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Comece a montar uma nova cotação para um cliente.</p>
                  </div>
              </div>
            </Link>
            <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border-l-4 border-gray-400">
               <div className="flex items-center gap-4">
                  <ClipboardDocumentListIcon className="w-10 h-10 text-gray-400" />
                   <div>
                      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Meus Orçamentos</h2>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Veja e gerencie seus orçamentos salvos.</p>
                  </div>
               </div>
            </div>
          </div>
          {/* --- NOVO CARD PARA IMPORTAÇÃO --- */}
          <Link href="/dashboard/orcamentos/importar" className="block p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-green-500">
               <div className="flex items-center gap-4">
                  <ArrowUpOnSquareIcon className="w-10 h-10 text-green-500" />
                   <div>
                      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Criar a partir de NF-e</h2>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Faça upload de uma nota fiscal e dê baixa no estoque.</p>
                  </div>
               </div>
            </Link>
          
          {/* Tabela de Orçamentos Recentes */}
          <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <div className="px-6 py-4 border-b dark:border-gray-700">
              <h3 className="text-lg font-semibold">Orçamentos Recentes</h3>
            </div>
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-700/50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">ID</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Cliente</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Data</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Status</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Ações</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {loading ? (
                            <tr>
                                <td colSpan={5} className="text-center p-8 text-gray-500">Carregando orçamentos...</td>
                            </tr>
                        ) : orcamentos.length > 0 ? (
                            orcamentos.map(orc => (
                                // --- 3. ADICIONAR onClick E cursor-pointer NA LINHA ---
                                <tr 
                                  key={orc.id} 
                                  onClick={() => router.push(`/dashboard/orcamentos/${orc.id}`)}
                                  className="hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
                                >
                                    <td className="px-6 py-4 font-mono text-xs text-gray-500">#{String(orc.id).padStart(4, '0')}</td>
                                    <td className="px-6 py-4 font-medium text-gray-900 dark:text-gray-100">{orc.nome_cliente}</td>
                                    <td className="px-6 py-4 text-gray-500 dark:text-gray-400">{new Date(orc.data_criacao).toLocaleDateString('pt-BR')}</td>
                                    <td className="px-6 py-4">
                                        {/* --- 4. LÓGICA DE COR DINÂMICA PARA O STATUS --- */}
                                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                            orc.status === 'FINALIZADO' 
                                              ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' 
                                              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                                          }`}
                                        >
                                          {orc.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <span className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 font-semibold">Ver Detalhes</span>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={5} className="text-center p-8 text-gray-500">Nenhum orçamento encontrado.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

// O wrapper para proteção continua, pois garante que a página só renderize para usuários logados.
export default function OrcamentosPageWrapper() {
  return (
    <ClientLayout>
      <OrcamentosPageContent />
    </ClientLayout>
  );
}