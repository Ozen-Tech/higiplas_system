'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Button from '../components/Button';
import Input from '../components/Input';
import { Header } from '@/components/dashboard/Header'; // O caminho pode precisar de ajuste

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;
      if (!API_BASE_URL) {
        throw new Error("URL da API não configurada.");
      }

      const response = await fetch(`${API_BASE_URL}/users/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          username: email,
          password: password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Credenciais inválidas.');
      }

      const data = await response.json();
      localStorage.setItem('authToken', data.access_token);
      router.push('/dashboard');
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Ocorreu um erro inesperado.');
      }
    }
  };

  return (
    // Estrutura de layout alterada para acomodar o header
    <div className="flex flex-col min-h-screen bg-gray-100 dark:bg-neutral-gray-darkBg">
      {/* O Header é renderizado aqui, na sua versão "pública" */}
      <Header title="Acesso ao Sistema" isAuthenticated={false} />

      <main className="flex-1 flex items-center justify-center p-4 sm:p-6">
        <div className="w-full max-w-md bg-white dark:bg-neutral-gray-darkSurface rounded-2xl shadow-xl p-8 sm:p-10 space-y-8 border border-gray-200 dark:border-neutral-gray-darkBorder">
          <div className="flex justify-center">
            <Image
              src="/HIGIPLAS-LOGO-2048x761.png"
              alt="Logo Higiplas"
              width={200}
              height={75}
              priority
              className="dark:invert-[.15] dark:brightness-150" // Pequeno ajuste para a logo em modo escuro
            />
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-higiplas-blue dark:text-gray-100 text-center tracking-tight">
            Painel de Controle
          </h2>

          <form className="space-y-6" onSubmit={handleLogin} noValidate>
            <Input
              label="E-mail"
              id="email" // Adicionando id para acessibilidade
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="placeholder:text-gray-500"
            />
            <Input
              label="Senha"
              id="password" // Adicionando id para acessibilidade
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="placeholder:text-gray-500"
            />
            
            {/* Mensagem de erro */}
            {error && (
              <p className="text-sm font-medium text-red-600 dark:text-red-500 text-center animate-fadeIn">
                {error}
              </p>
            )}

            <Button type="submit" fullWidth className="text-lg">
              Entrar
            </Button>
          </form>
        </div>
      </main>
      
      {/* Estilos específicos que você tinha antes */}
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-5px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease forwards;
        }
      `}</style>
    </div>
  );
}