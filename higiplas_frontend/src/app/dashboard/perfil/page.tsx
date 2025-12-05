// /src/app/dashboard/perfil/page.tsx

'use client';

import { useEffect } from 'react';
import { useProfile } from '@/hooks/useProfile';
import ProfileForm from '@/components/perfil/ProfileForm';
import PasswordForm from '@/components/perfil/PasswordForm';
import { Header } from '@/components/dashboard/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { User, Lock } from 'lucide-react';

export default function PerfilPage() {
  const { user, loading, fetchProfile, updateProfile, updatePassword } = useProfile();

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-higiplas-blue mx-auto"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Carregando perfil...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <p className="text-red-600">Erro ao carregar perfil. Tente novamente.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Meu Perfil</h1>

          {/* Formulário de Perfil */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <User className="w-5 h-5" />
                <span>Informações Pessoais</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ProfileForm user={user} onUpdate={updateProfile} />
            </CardContent>
          </Card>

          {/* Formulário de Senha */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Lock className="w-5 h-5" />
                <span>Alterar Senha</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <PasswordForm onUpdate={updatePassword} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}


