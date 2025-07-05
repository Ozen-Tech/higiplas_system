// /src/app/components/Header.tsx

"use client";

import Image from "next/image";
import Link from "next/link";
import { ThemeToggleButton } from "./ThemeToggleButton"; // Assumindo que está em /components

interface HeaderProps {
  onLogoutClick: () => void;
}

export function Header({ onLogoutClick }: HeaderProps) {
  return (
    <header className="flex items-center justify-between w-full px-4 md:px-8 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 sticky top-0 z-10">
      {/* Lado Esquerdo: Logo */}
      <Link href="/dashboard">
        <Image src="/HIGIPLAS-LOGO-2048x761.png" alt="Logo Higiplas" width={150} height={50} priority className="cursor-pointer" />
      </Link>

      {/* Lado Direito: Ações Globais */}
      <div className="flex items-center gap-4">
        <ThemeToggleButton />
        <button onClick={onLogoutClick} className="text-sm font-semibold text-gray-600 dark:text-gray-300 hover:text-red-500 dark:hover:text-red-400 transition-colors">
          Sair
        </button>
      </div>
    </header>
  );
}