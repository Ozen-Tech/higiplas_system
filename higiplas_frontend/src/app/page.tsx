'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Button from '../components/Button';
import Input from '../components/Input';
import { ThemeToggleButton } from '@/components/ThemeToggleButton';

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
    <div className="flex flex-col min-h-screen bg-gray-100 dark:bg-neutral-gray-darkBg">
      {/* HEADER SIMPLES E LOCAL PARA A PÁGINA DE LOGIN */}
      <header className="flex items-center justify-between w-full px-4 md:px-8 py-3 border-b border-gray-200 dark:border-gray-700">
        <Image 
          src="/HIGIPLAS-LOGO-2048x761.png" 
          alt="Logo Higiplas" 
          width={140} 
          height={48} 
          priority 
        />
        <ThemeToggleButton />
      </header>

      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white dark:bg-neutral-gray-darkSurface rounded-2xl shadow-xl p-8 space-y-8 border dark:border-neutral-gray-darkBorder">
          <h2 className="text-2xl font-bold text-center text-gray-800 dark:text-gray-100">Acesso ao Painel</h2>
          <form className="space-y-6" onSubmit={handleLogin} noValidate>
            <Input
              label="E-mail"
              id="login-email" // ID único para este input
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="placeholder:text-gray-500"
            />
            <Input
              label="Senha"
              id="login-password" // ID único para este input
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="placeholder:text-gray-500"
            />
            {error && <p className="text-sm text-center text-red-500 animate-fadeIn">{error}</p>}
            <Button type="submit" fullWidth className="text-lg">Entrar</Button>
          </form>
        </div>
      </main>
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