'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Package, Clock, CheckCircle, XCircle } from 'lucide-react';
import { useEntregador } from '@/hooks/useEntregador';
import { useMovimentacoesPendentes } from '@/hooks/useMovimentacoesPendentes';
import Link from 'next/link';

export default function EntregadorAppPage() {
  const router = useRouter();
  const { usuario, loading, error, isOperador } = useEntregador();
  const { movimentacoes, loading: loadingMovimentacoes } = useMovimentacoesPendentes();
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

  if (error || !isOperador) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full">
          <CardContent className="p-6 text-center space-y-4">
            <p className="text-red-600 dark:text-red-400">{error || 'Acesso negado. Apenas entregadores podem acessar esta área.'}</p>
            <Button onClick={() => router.push('/entregador/login')}>
              Voltar para Login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const pendentes = movimentacoes.filter(m => m.status === 'PENDENTE').length;
  const confirmadas = movimentacoes.filter(m => m.status === 'CONFIRMADO').length;
  const rejeitadas = movimentacoes.filter(m => m.status === 'REJEITADO').length;

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4">
        <div className="min-w-0 flex-1">
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">
            Movimentações de Estoque
          </h1>
          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1">
            Bem-vindo, {usuario?.nome}
          </p>
        </div>
        <Link href="/entregador/app/registrar">
          <Button className="w-full sm:w-auto min-h-[44px]">
            <Package className="mr-2 h-4 w-4" />
            Registrar Movimentação
          </Button>
        </Link>
      </div>

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Pendentes</p>
                <p className="text-2xl font-bold text-yellow-600">{pendentes}</p>
              </div>
              <Clock className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Confirmadas</p>
                <p className="text-2xl font-bold text-green-600">{confirmadas}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Rejeitadas</p>
                <p className="text-2xl font-bold text-red-600">{rejeitadas}</p>
              </div>
              <XCircle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Movimentações recentes */}
      <Card>
        <CardContent className="p-4 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Movimentações Recentes
            </h2>
            <Link href="/entregador/app/historico">
              <Button variant="outline" size="sm">
                Ver Todas
              </Button>
            </Link>
          </div>
          {loadingMovimentacoes ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
            </div>
          ) : movimentacoes.length === 0 ? (
            <p className="text-center text-gray-500 dark:text-gray-400 py-8">
              Nenhuma movimentação registrada ainda.
            </p>
          ) : (
            <div className="space-y-3">
              {movimentacoes.slice(0, 5).map((mov) => (
                <div
                  key={mov.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 dark:text-gray-100 truncate">
                      {mov.produto?.nome || 'Produto não encontrado'}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {mov.tipo_movimentacao} - {mov.quantidade} unidades
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      {new Date(mov.data_movimentacao).toLocaleString('pt-BR')}
                    </p>
                  </div>
                  <div className="ml-4">
                    {mov.status === 'PENDENTE' && (
                      <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded">
                        Pendente
                      </span>
                    )}
                    {mov.status === 'CONFIRMADO' && (
                      <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded">
                        Confirmado
                      </span>
                    )}
                    {mov.status === 'REJEITADO' && (
                      <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded">
                        Rejeitado
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

