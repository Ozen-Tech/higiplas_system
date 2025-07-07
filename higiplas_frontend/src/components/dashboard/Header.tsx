// /src/components/dashboard/Header.tsx
"use client";

import { ReactNode } from "react";
import Image from "next/image";
import Link from "next/link";

interface HeaderProps {
  children?: ReactNode; // Ações a serem exibidas na direita
}

export function Header({ children }: HeaderProps) {
  return (
    <header className="flex items-center justify-between w-full px-4 md:px-8 py-3 border-b border-gray-200 dark:border-gray-700 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm sticky top-0 z-20">
      
      {/* Lado Esquerdo: Apenas a Logo que sempre leva ao dashboard */}
      <Link href="/dashboard" passHref>
          <Image 
              src="/HIGIPLAS-LOGO-2048x761.png" 
              alt="Logo Higiplas" 
              width={140} 
              height={48} 
              priority 
          />
      </Link>

      {/* Lado Direito: Container para ações */}
      <div className="flex items-center gap-3">
        {children} {/* Renderiza qualquer botão ou elemento que a página passar */}
      </div>
    </header>
  );
}