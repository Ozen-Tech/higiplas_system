// /src/components/dashboard/Header.tsx
"use client";

import { ReactNode } from "react";

interface HeaderProps {
  children?: ReactNode; // 'children' vai conter o título e os botões
}

export function Header({ children }: HeaderProps) {
  return (
    <header className="flex-shrink-0 flex items-center justify-between w-full h-16 px-4 md:px-8 border-b border-gray-200 dark:border-gray-700 bg-white/95 dark:bg-gray-800/95 sticky top-0 z-10">
      {/* O conteúdo do header (título, botões) será passado pela página */}
      {children}
    </header>
  );
}