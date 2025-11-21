'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Button from '@/components/Button';
import Input from '@/components/Input';
import toast from 'react-hot-toast';

export default function EntregadorLoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

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

      // Verificar se o usuário é operador (entregador)
      const userResponse = await fetch(`${API_BASE_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      });

      if (!userResponse.ok) {
        throw new Error('Erro ao obter dados do usuário');
      }

      const usuario = await userResponse.json();
      
      if (usuario.perfil !== 'OPERADOR') {
        localStorage.removeItem('authToken');
        throw new Error('Acesso negado. Apenas entregadores podem acessar esta área.');
      }

      toast.success('Login realizado com sucesso!');
      router.push('/entregador/app');
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
        toast.error(err.message);
      } else {
        setError('Ocorreu um erro inesperado.');
        toast.error('Ocorreu um erro inesperado.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <header className="flex items-center justify-between w-full px-4 md:px-8 py-4 border-b bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
        <Image 
          src="/HIGIPLAS-LOGO-2048x761.png" 
          alt="Logo Higiplas" 
          width={140} 
          height={48} 
          priority 
        />
      </header>
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md p-8 space-y-6 bg-white dark:bg-gray-800 rounded-lg shadow-xl">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Acesso Entregador
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Faça login para registrar movimentações de estoque
            </p>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <Input
              label="E-mail"
              id="entregador-login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              disabled={loading}
            />
            <Input
              label="Senha"
              id="entregador-login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              disabled={loading}
            />
            {error && <p className="text-red-500 text-sm text-center">{error}</p>}
            <Button type="submit" fullWidth disabled={loading}>
              {loading ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>
          <div className="text-center">
            <button
              onClick={() => router.push('/')}
              className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              Voltar para o login principal
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

