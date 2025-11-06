'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useVendedor } from '@/hooks/useVendedor';
import { OrcamentoBuilder } from '@/components/vendedor/OrcamentoBuilder';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

export default function VendedorAppPage() {
  const router = useRouter();
  const { usuario, loading, error, isVendedor } = useVendedor();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">Carregando...</p>
        </div>
      </div>
    );
  }

  if (error || !isVendedor) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full">
          <CardContent className="p-6 text-center space-y-4">
            <p className="text-red-600 dark:text-red-400">{error || 'Acesso negado. Apenas vendedores podem acessar esta área.'}</p>
            <Button onClick={() => router.push('/vendedor/login')}>
              Voltar para Login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Novo Orçamento
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Bem-vindo, {usuario?.nome}
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => router.push('/vendedor/app/historico')}
        >
          Ver Histórico
        </Button>
      </div>

      <OrcamentoBuilder />
    </div>
  );
}

