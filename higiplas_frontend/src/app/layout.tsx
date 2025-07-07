// /src/app/layout.tsx
import type { Metadata } from 'next';
import './globals.css';
import { Providers } from './providers'; // Importa nosso componente de providers

export const metadata: Metadata = {
  title: 'Higiplas Estoque',
  description: 'Sistema de Gestão de Estoque da Higiplas',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-br" suppressHydrationWarning>
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}