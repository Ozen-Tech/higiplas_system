// /src/app/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Button from '../components/Button';
import Input from '../components/Input';
import { ThemeToggleButton } from '@/components/ThemeToggleButton';
import { User } from 'lucide-react';
import { apiService } from '@/services/apiService';
import { adminService } from '@/services/adminService';
import toast from 'react-hot-toast';

export default function LoginPage() {
  // #region agent log
  try { fetch('http://127.0.0.1:7242/ingest/dd87b882-9f5c-4d4f-ba43-1e6325b293f7', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location: 'page.tsx (login)', message: 'LoginPage render', data: {}, timestamp: Date.now(), sessionId: 'debug-session', hypothesisId: 'H3' }) }).catch(() => {}); } catch {}
  // #endregion
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

      // Verificar se o usuário é admin ou gestor
      try {
        const userData = await apiService.get('/users/me');
        const usuario = userData?.data || userData;
        
        if (!usuario) {
          throw new Error('Erro ao obter dados do usuário');
        }

        if (!adminService.isAdmin(usuario.perfil)) {
          localStorage.removeItem('authToken');
          throw new Error('Acesso negado. Apenas administradores ou gestores podem acessar o dashboard.');
        }

        toast.success('Login realizado com sucesso!');
        router.push('/dashboard');
      } catch (userError) {
        localStorage.removeItem('authToken');
        if (userError instanceof Error) {
          throw userError;
        }
        throw new Error('Erro ao verificar permissões do usuário.');
      }
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
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 text-center mb-3">
              É vendedor?
            </p>
            <Button
              type="button"
              variant="secondary"
              fullWidth
              onClick={() => router.push('/vendedor/login')}
              className="gap-2"
            >
              <User size={16} />
              Acessar como Vendedor
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}