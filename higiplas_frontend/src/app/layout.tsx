// /src/app/layout.tsx

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import './globals.css';
import { ThemeProvider } from "@/components/ThemeProvider";
import { AuthProvider } from '@/contexts/AuthContext';


const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Higiplas System",
  description: "Sistema de Gestão de Produtos e Estoque",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased
          min-h-screen
          bg-gray-100 text-gray-900
          dark:bg-gray-900 dark:text-gray-100
          transition-colors duration-300
        `}
      >
         <AuthProvider>  
          {children}
        </AuthProvider>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}