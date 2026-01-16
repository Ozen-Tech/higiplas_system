'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { vendedorService } from '@/services/vendedorService';
import toast from 'react-hot-toast';

export default function VendedorLoginPage() {
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

      // Verificar se o usuário é vendedor
      const usuario = await vendedorService.getMe();
      if (!usuario) {
        throw new Error('Erro ao obter dados do usuário');
      }

      if (!vendedorService.isVendedor(usuario.perfil)) {
        localStorage.removeItem('authToken');
        throw new Error('Acesso negado. Apenas vendedores podem acessar esta área.');
      }

      toast.success('Login realizado com sucesso!');
      router.push('/vendedor/app');
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
              Acesso Vendedor
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Faça login para acessar o aplicativo de orçamentos
            </p>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <Input
              label="E-mail"
              id="vendedor-login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              disabled={loading}
            />
            <Input
              label="Senha"
              id="vendedor-login-password"
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
          <div className="text-center space-y-2">
            <button
              onClick={() => router.push('/vendedor/visitas')}
              className="block w-full px-4 py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition"
            >
              📍 Registrar Visita
            </button>
            <button
              onClick={() => router.push('/')}
              className="text-sm text-gray-600 dark:text-gray-400 hover:underline"
            >
              Voltar para o login principal
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

