'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Button from '../components/Button';
import Input from '../components/Input';

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
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 via-blue-700 to-blue-900 p-6">
      <div className="max-w-md w-full bg-white rounded-3xl shadow-2xl p-10 space-y-8 border-4 border-higiplas-blue">
        <div className="flex justify-center">
          <Image
            src="/HIGIPLAS-LOGO-2048x761.png"
            alt="Logo Higiplas"
            width={220}
            height={80}
            priority
            className="drop-shadow-lg"
          />
        </div>
        <h2 className="text-4xl font-extrabold text-higiplas-blue text-center tracking-wide">
          Bem-vindo à Higiplas
        </h2>
        <form className="space-y-6" onSubmit={handleLogin} noValidate>
          <Input
            label="Endereço de E-mail"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="placeholder:text-gray-500"
          />
          <Input
            label="Senha"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="placeholder:text-gray-500"
          />
          {error && (
            <p className="text-sm text-red-700 font-semibold animate-fadeIn">
              {error}
            </p>
          )}
          <Button type="submit" fullWidth className="text-lg">
            Entrar
          </Button>
        </form>
      </div>
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
    </main>
  );
}