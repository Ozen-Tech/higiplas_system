// /src/app/page.tsx
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
        const errorData = await response.json().catch(() => ({ detail: 'Credenciais inválidas ou erro no servidor.' }));
        throw new Error(errorData.detail);
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
    <div className="flex flex-col min-h-screen">
      <header className="flex items-center justify-between w-full px-4 md:px-8 py-3 border-b bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
        <Image 
          src="/HIGIPLAS-LOGO-2048x761.png" 
          alt="Logo Higiplas" 
          width={140} 
          height={48} 
          priority 
        />
        <ThemeToggleButton />
      </header>
      <main className="flex-1 flex items-center justify-center p-4 bg-gray-50 dark:bg-gray-900">
        <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md dark:bg-gray-800">
          <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-gray-100">Acesso ao Painel</h2>
          <form onSubmit={handleLogin} className="space-y-4">
            <Input
              label="E-mail"
              id="login-email-unique"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
            <Input
              label="Senha"
              id="login-password-unique"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
            {error && <p className="text-red-500 text-sm text-center">{error}</p>}
            <Button type="submit" fullWidth>Entrar</Button>
          </form>
        </div>
      </main>
    </div>
  );
}