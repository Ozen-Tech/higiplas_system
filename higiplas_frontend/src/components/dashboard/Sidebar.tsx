// /src/components/dashboard/Sidebar.tsx
"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { CubeIcon, SparklesIcon, ClipboardDocumentListIcon, ShoppingCartIcon, UserGroupIcon, ArrowTrendingUpIcon, ArrowsRightLeftIcon, ClockIcon, ArrowUpIcon, ArrowDownIcon, ChevronDownIcon, ChevronRightIcon } from '@heroicons/react/24/outline'; // Ícones que vamos usar
import Image from 'next/image'; 

// Define os tipos para os itens de navegação
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

// Define a estrutura de cada item do menu
const navigation: NavigationItem[] = [
  { name: 'Estoque', href: '/dashboard', icon: CubeIcon },
  { 
    name: 'Movimentações', 
    icon: ArrowsRightLeftIcon,
    subItems: [
      { name: 'Entrada de Estoque', href: '/dashboard/entrada', icon: ArrowUpIcon },
      { name: 'Saída de Estoque', href: '/dashboard/saida', icon: ArrowDownIcon },
    ]
  },
  { name: 'Histórico Geral', href: '/dashboard/historico', icon: ClockIcon },
  { name: 'Compras', href: '/dashboard/compras', icon: ShoppingCartIcon },
  { name: 'Clientes', href: '/dashboard/clientes', icon: UserGroupIcon },
  { name: 'IA Insights', href: '/dashboard/insights', icon: SparklesIcon },
  { name: 'Orçamentos', href: '/dashboard/orcamentos', icon: ClipboardDocumentListIcon },
  { name: 'Produtos Mais Vendidos', href: '/dashboard/produtos-mais-vendidos', icon: ArrowTrendingUpIcon },
];

export function Sidebar() {
  const pathname = usePathname(); // Hook para saber qual é a página ativa
  const [expandedItems, setExpandedItems] = useState<string[]>(['Movimentações']); // Expandir Movimentações por padrão

  const toggleExpanded = (itemName: string) => {
    setExpandedItems(prev => 
      prev.includes(itemName) 
        ? prev.filter(name => name !== itemName)
        : [...prev, itemName]
    );
  };

  return (
    <aside className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
      {/* Componente Sidebar para desktop */}
      <div className="flex flex-col flex-grow bg-white dark:bg-gray-800 pt-5 pb-4 overflow-y-auto border-r border-gray-200 dark:border-gray-700">
        {/* O Logo não está mais no Header, mas aqui! */}
        <div className="flex items-center flex-shrink-0 px-4">
        <Image
            src="/HIGIPLAS-LOGO-2048x761.png"
            alt="Higiplas Logo"
            width={140} // Ajuste o tamanho conforme preferir
            height={48}
            priority // Otimiza o carregamento da logo
          />
        </div>
        
        <div className="mt-8 flex-1 flex flex-col">
          <nav className="flex-1 px-2 space-y-1">
            {navigation.map((item) => {
              // Se o item tem subItems, renderiza de forma diferente
              if ('subItems' in item && item.subItems) {
                const isExpanded = expandedItems.includes(item.name);
                const hasActiveSubItem = item.subItems.some(subItem => pathname === subItem.href);
                
                return (
                  <div key={item.name}>
                    {/* Item principal com sub-itens */}
                    <button
                      onClick={() => toggleExpanded(item.name)}
                      className={`
                        w-full group flex items-center justify-between px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150
                        ${
                          hasActiveSubItem
                            ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-200'
                            : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
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
                    
                    {/* Sub-itens */}
                    {isExpanded && (
                      <div className="ml-6 mt-1 space-y-1">
                        {item.subItems.map((subItem) => {
                          const isActive = pathname === subItem.href;
                          return (
                            <Link
                              key={subItem.name}
                              href={subItem.href}
                              className={`
                                group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150
                                ${
                                  isActive
                                    ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-200'
                                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
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
              
              // Item normal sem sub-itens
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href!}
                  className={`
                    group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150
                    ${
                      isActive
                        ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-200'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
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
              )
            })}
          </nav>
        </div>
      </div>
    </aside>
  );
}