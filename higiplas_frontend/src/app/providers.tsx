"use client";

import { ReactNode } from 'react';
import { AuthProvider } from '@/contexts/AuthContext';


interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  // Envolva os children com todos os seus providers de cliente.
  return (
    <AuthProvider>
      {/* 
        Exemplo se você também usar next-themes:
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      */}
      {children}
    </AuthProvider>
  );
}