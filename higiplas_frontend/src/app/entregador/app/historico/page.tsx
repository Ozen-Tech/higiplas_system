'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Clock, CheckCircle, XCircle } from 'lucide-react';
import { useEntregador } from '@/hooks/useEntregador';
import { useMovimentacoesPendentes } from '@/hooks/useMovimentacoesPendentes';
import { StatusMovimentacao } from '@/types';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function HistoricoMovimentacoesPage() {
  const router = useRouter();
  const { loading: loadingUser, error, isOperador } = useEntregador();
  const [mounted, setMounted] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const { movimentacoes, loading: loadingMovimentacoes, carregarMovimentacoes } = useMovimentacoesPendentes(statusFilter || undefined);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted) {
      carregarMovimentacoes();
    }
  }, [statusFilter, mounted, carregarMovimentacoes]);

  if (!mounted) {
    return null;
  }

  if (loadingUser) {
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

  const getStatusIcon = (status: StatusMovimentacao) => {
    switch (status) {
      case StatusMovimentacao.PENDENTE:
        return <Clock className="h-5 w-5 text-yellow-600" />;
      case StatusMovimentacao.CONFIRMADO:
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case StatusMovimentacao.REJEITADO:
        return <XCircle className="h-5 w-5 text-red-600" />;
    }
  };

  const getStatusBadge = (status: StatusMovimentacao) => {
    switch (status) {
      case StatusMovimentacao.PENDENTE:
        return (
          <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded">
            Pendente
          </span>
        );
      case StatusMovimentacao.CONFIRMADO:
        return (
          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded">
            Confirmado
          </span>
        );
      case StatusMovimentacao.REJEITADO:
        return (
          <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded">
            Rejeitado
          </span>
        );
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4">
        <div className="min-w-0 flex-1">
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">
            Histórico de Movimentações
          </h1>
          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1">
            Visualize todas as suas movimentações registradas
          </p>
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full sm:w-[200px] h-11">
            <SelectValue placeholder="Filtrar por status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">Todas</SelectItem>
            <SelectItem value="PENDENTE">Pendentes</SelectItem>
            <SelectItem value="CONFIRMADO">Confirmadas</SelectItem>
            <SelectItem value="REJEITADO">Rejeitadas</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card>
        <CardContent className="p-4 sm:p-6">
          {loadingMovimentacoes ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
            </div>
          ) : movimentacoes.length === 0 ? (
            <p className="text-center text-gray-500 dark:text-gray-400 py-8">
              Nenhuma movimentação encontrada.
            </p>
          ) : (
            <div className="space-y-3">
              {movimentacoes.map((mov) => (
                <div
                  key={mov.id}
                  className="p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        {getStatusIcon(mov.status)}
                        <h3 className="font-medium text-gray-900 dark:text-gray-100 truncate">
                          {mov.produto?.nome || 'Produto não encontrado'}
                        </h3>
                      </div>
                      <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                        <p>
                          <span className="font-medium">Tipo:</span> {mov.tipo_movimentacao} -{' '}
                          <span className="font-medium">Quantidade:</span> {mov.quantidade}
                        </p>
                        {mov.motivo_movimentacao && (
                          <p>
                            <span className="font-medium">Motivo:</span>{' '}
                            {mov.motivo_movimentacao.replace('_', ' ').toLowerCase()}
                          </p>
                        )}
                        {mov.observacao && (
                          <p>
                            <span className="font-medium">Observação:</span> {mov.observacao}
                          </p>
                        )}
                        {mov.motivo_rejeicao && (
                          <p className="text-red-600 dark:text-red-400">
                            <span className="font-medium">Motivo da rejeição:</span> {mov.motivo_rejeicao}
                          </p>
                        )}
                        <p className="text-xs text-gray-500 dark:text-gray-500">
                          Registrado em: {new Date(mov.data_movimentacao).toLocaleString('pt-BR')}
                        </p>
                        {mov.data_aprovacao && (
                          <p className="text-xs text-gray-500 dark:text-gray-500">
                            {mov.status === 'CONFIRMADO' ? 'Confirmado' : 'Rejeitado'} em:{' '}
                            {new Date(mov.data_aprovacao).toLocaleString('pt-BR')}
                            {mov.aprovado_por && ` por ${mov.aprovado_por.nome}`}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex-shrink-0">
                      {getStatusBadge(mov.status)}
                    </div>
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

