 // /src/components/dashboard/Sidebar.tsx - VERSÃO CORRIGIDA
"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import {
  CubeIcon, SparklesIcon, ShoppingCartIcon,
  // CORRIGIDO: Ícones não utilizados foram removidos da importação.
  ArrowTrendingUpIcon, ArrowsRightLeftIcon, ClockIcon,
  ChevronDownIcon, ChevronRightIcon, DocumentTextIcon, UserPlusIcon,
  ClipboardDocumentListIcon, UserGroupIcon, CheckCircleIcon,
  UserCircleIcon
} from '@heroicons/react/24/outline';
import Image from 'next/image';

type NavigationItem = {
  name: string;
  href?: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  subItems?: {
    name: string;
    href: string;
    icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  }[];
};

const navigation: NavigationItem[] = [
  { name: 'Estoque', href: '/dashboard', icon: CubeIcon },
  { name: 'Movimentações', href: '/dashboard/movimentacoes', icon: ArrowsRightLeftIcon },
  { name: 'Histórico Geral', href: '/dashboard/historico', icon: ClockIcon },
  { 
    name: 'Compras', 
    href: '/dashboard/compras', 
    icon: ShoppingCartIcon,
    subItems: [
      { name: 'Sugestões', href: '/dashboard/compras', icon: ShoppingCartIcon },
      { name: 'KPIs de Compras', href: '/dashboard/compras/kpis', icon: ArrowTrendingUpIcon }
    ]
  },
  { name: 'Relatórios', href: '/dashboard/relatorios', icon: DocumentTextIcon },
  { name: 'IA Insights', href: '/dashboard/insights', icon: SparklesIcon },
  { name: 'Produtos Mais Vendidos', href: '/dashboard/produtos-mais-vendidos', icon: ArrowTrendingUpIcon },
  { name: 'Meu Perfil', href: '/dashboard/perfil', icon: UserCircleIcon },
];

const adminNavigation: NavigationItem[] = [
  { name: 'Criar Usuário', href: '/admin/criar-usuario', icon: UserPlusIcon },
  { name: 'Solicitações de Movimentação', href: '/dashboard/movimentacoes-pendentes', icon: CheckCircleIcon },
  { name: 'Gerenciar Orçamentos', href: '/dashboard/orcamentos', icon: ClipboardDocumentListIcon },
  { name: 'Gerenciar Clientes', href: '/dashboard/clientes', icon: UserGroupIcon },
  { name: 'Propostas Detalhadas', href: '/dashboard/propostas-detalhadas', icon: DocumentTextIcon },
];

export function Sidebar() {
  const pathname = usePathname();
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const toggleExpanded = (itemName: string) => {
    setExpandedItems(prev =>
      prev.includes(itemName)
        ? prev.filter(name => name !== itemName)
        : [...prev, itemName]
    );
  };

  // Resto do componente permanece o mesmo...
  return (
    <aside className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0 z-40">
      <div className="flex flex-col flex-grow bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl pt-5 pb-4 overflow-y-auto border-r border-gray-200/50 dark:border-gray-700/50 shadow-lg">
        <div className="flex items-center flex-shrink-0 px-4 mb-2 animate-fadeIn">
          <Image
            src="/HIGIPLAS-LOGO-2048x761.png"
            alt="Higiplas Logo"
            width={140}
            height={48}
            priority
            className="transition-opacity duration-300 hover:opacity-80"
          />
        </div>

        <div className="mt-8 flex-1 flex flex-col">
          <nav className="flex-1 px-2 space-y-1">
            {navigation.map((item) => {
              if ('subItems' in item && item.subItems) {
                const isExpanded = expandedItems.includes(item.name);
                const hasActiveSubItem = item.subItems.some(subItem => pathname === subItem.href);

                return (
                  <div key={item.name}>
                    <button
                      onClick={() => toggleExpanded(item.name)}
                      className={`
                        w-full group flex items-center justify-between px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 hover-lift
                        ${
                          hasActiveSubItem
                            ? 'bg-gradient-to-r from-blue-500/10 to-blue-600/10 dark:from-blue-500/20 dark:to-blue-600/20 text-blue-700 dark:text-blue-300 shadow-sm border-l-2 border-blue-500'
                            : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100/80 dark:hover:bg-gray-800/80'
                        }
                      `}
                    >
                      <div className="flex items-center">
                        <item.icon
                          className={`mr-3 h-6 w-6 flex-shrink-0
                            ${hasActiveSubItem ? 'text-blue-600 dark:text-blue-300' : 'text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300'}
                          `}
                        />
                        {item.name}
                      </div>
                      {isExpanded ? (
                        <ChevronDownIcon className="h-4 w-4" />
                      ) : (
                        <ChevronRightIcon className="h-4 w-4" />
                      )}
                    </button>

                    {isExpanded && (
                      <div className="ml-6 mt-1 space-y-1">
                        {item.subItems.map((subItem) => {
                          const isActive = pathname === subItem.href;
                          return (
                            <Link
                              key={subItem.name}
                              href={subItem.href}
                              className={`
                                group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 ml-2
                                ${
                                  isActive
                                    ? 'bg-gradient-to-r from-blue-500/10 to-blue-600/10 dark:from-blue-500/20 dark:to-blue-600/20 text-blue-700 dark:text-blue-300 shadow-sm border-l-2 border-blue-500'
                                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100/80 dark:hover:bg-gray-800/80 hover:translate-x-1'
                                }
                              `}
                            >
                              <subItem.icon
                                className={`mr-3 h-5 w-5 flex-shrink-0
                                  ${isActive ? 'text-blue-600 dark:text-blue-300' : 'text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300'}
                                `}
                              />
                              {subItem.name}
                            </Link>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              }

              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href!}
                  className={`
                    group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 hover-lift
                    ${
                      isActive
                        ? 'bg-gradient-to-r from-blue-500/10 to-blue-600/10 dark:from-blue-500/20 dark:to-blue-600/20 text-blue-700 dark:text-blue-300 shadow-sm border-l-2 border-blue-500'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100/80 dark:hover:bg-gray-800/80'
                    }
                  `}
                >
                  <item.icon
                    className={`mr-3 h-6 w-6 flex-shrink-0
                      ${isActive ? 'text-blue-600 dark:text-blue-300' : 'text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300'}
                    `}
                  />
                  {item.name}
                </Link>
              );
            })}
            
            {/* Seção Admin - disponível para todos os usuários */}
            <div className="pt-4 mt-4 border-t border-gray-200/50 dark:border-gray-700/50">
              <p className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                Administração
              </p>
            </div>
            {adminNavigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href!}
                  className={`
                    group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 hover-lift
                    ${
                      isActive
                        ? 'bg-gradient-to-r from-blue-500/10 to-blue-600/10 dark:from-blue-500/20 dark:to-blue-600/20 text-blue-700 dark:text-blue-300 shadow-sm border-l-2 border-blue-500'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100/80 dark:hover:bg-gray-800/80'
                    }
                  `}
                >
                  <item.icon
                    className={`mr-3 h-6 w-6 flex-shrink-0
                      ${isActive ? 'text-blue-600 dark:text-blue-300' : 'text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300'}
                    `}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </aside>
  );
}