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
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#2563eb" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="Orçamentos" />
      </head>
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}