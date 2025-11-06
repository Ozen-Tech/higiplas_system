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
      {/* Header minimalista */}
      <header className="sticky top-0 z-40 w-full border-b bg-white/95 dark:bg-gray-900/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-gray-900/60">
        <div className="flex h-14 items-center justify-between px-4 md:px-6">
          <div className="flex items-center gap-4">
            <Link href="/vendedor/app" className="flex items-center gap-2">
              <Image 
                src="/HIGIPLAS-LOGO-2048x761.png" 
                alt="Logo Higiplas" 
                width={120} 
                height={40} 
                priority 
              />
              <span className="hidden md:inline text-sm font-semibold text-gray-700 dark:text-gray-300">
                Orçamentos
              </span>
            </Link>
          </div>
          <div className="flex items-center gap-2">
            <Link href="/vendedor/app/historico">
              <Button variant="ghost" size="sm">
                Histórico
              </Button>
            </Link>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
            >
              <LogOut size={16} className="mr-2" />
              Sair
            </Button>
          </div>
        </div>
      </header>

      {/* Conteúdo principal */}
      <main className="container mx-auto px-4 py-6 max-w-7xl">
        {children}
      </main>
    </div>
  );
}

