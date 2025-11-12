'use client';

import Image from 'next/image';
import Link from 'next/link';
import { LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function VendedorAppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const handleLogout = () => {
    localStorage.removeItem('authToken');
    window.location.href = '/vendedor/login';
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header otimizado para mobile */}
      <header className="sticky top-0 z-40 w-full border-b bg-white/95 dark:bg-gray-900/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-gray-900/60 shadow-sm">
        <div className="flex h-14 sm:h-16 items-center justify-between px-3 sm:px-4 md:px-6">
          <div className="flex items-center gap-2 sm:gap-4 min-w-0 flex-1">
            <Link href="/vendedor/app" className="flex items-center gap-2 min-w-0">
              <Image 
                src="/HIGIPLAS-LOGO-2048x761.png" 
                alt="Logo Higiplas" 
                width={100}
                height={35}
                className="sm:w-[120px] sm:h-[40px]"
                priority 
              />
              <span className="hidden sm:inline text-xs sm:text-sm font-semibold text-gray-700 dark:text-gray-300 whitespace-nowrap">
                Orçamentos
              </span>
            </Link>
          </div>
          <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
            <Link href="/vendedor/app/historico">
              <Button 
                variant="ghost" 
                size="sm"
                className="h-10 w-10 sm:h-auto sm:w-auto sm:px-3 sm:py-2"
                title="Histórico"
              >
                <span className="hidden sm:inline">Histórico</span>
                <span className="sm:hidden">📋</span>
              </Button>
            </Link>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="h-10 w-10 sm:h-auto sm:w-auto sm:px-3 sm:py-2"
              title="Sair"
            >
              <LogOut size={18} className="sm:mr-2" />
              <span className="hidden sm:inline">Sair</span>
            </Button>
          </div>
        </div>
      </header>

      {/* Conteúdo principal otimizado para mobile */}
      <main className="w-full px-3 sm:px-4 md:px-6 py-4 sm:py-6 max-w-7xl mx-auto">
        {children}
      </main>
    </div>
  );
}

