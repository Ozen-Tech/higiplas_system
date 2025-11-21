'use client';

import { MovimentacaoPendente, StatusMovimentacao } from '@/types';
import { Button } from '@/components/ui/button';
import { CheckCircle, XCircle, Edit, Clock } from 'lucide-react';

interface MovimentacoesPendentesTableProps {
  movimentacoes: MovimentacaoPendente[];
  onConfirmar: (movimentacao: MovimentacaoPendente) => void;
  onEditar: (movimentacao: MovimentacaoPendente) => void;
  onRejeitar: (movimentacao: MovimentacaoPendente) => void;
}

export function MovimentacoesPendentesTable({
  movimentacoes,
  onConfirmar,
  onEditar,
  onRejeitar,
}: MovimentacoesPendentesTableProps) {
  const getStatusBadge = (status: StatusMovimentacao) => {
    switch (status) {
      case StatusMovimentacao.PENDENTE:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded">
            <Clock className="h-3 w-3" />
            Pendente
          </span>
        );
      case StatusMovimentacao.CONFIRMADO:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded">
            <CheckCircle className="h-3 w-3" />
            Confirmado
          </span>
        );
      case StatusMovimentacao.REJEITADO:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded">
            <XCircle className="h-3 w-3" />
            Rejeitado
          </span>
        );
    }
  };

  const getMotivoLabel = (motivo: string) => {
    const labels: Record<string, string> = {
      CARREGAMENTO: 'Carregamento para entrega',
      DEVOLUCAO: 'Devolução',
      AJUSTE_FISICO: 'Ajuste físico',
      PERDA_AVARIA: 'Perda/Avaria',
      TRANSFERENCIA_INTERNA: 'Transferência interna',
    };
    return labels[motivo] || motivo;
  };

  if (movimentacoes.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">
          Nenhuma movimentação encontrada.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b">
            <th className="text-left p-3 text-sm font-medium text-gray-700 dark:text-gray-300">Data</th>
            <th className="text-left p-3 text-sm font-medium text-gray-700 dark:text-gray-300">Entregador</th>
            <th className="text-left p-3 text-sm font-medium text-gray-700 dark:text-gray-300">Produto</th>
            <th className="text-left p-3 text-sm font-medium text-gray-700 dark:text-gray-300">Tipo</th>
            <th className="text-left p-3 text-sm font-medium text-gray-700 dark:text-gray-300">Quantidade</th>
            <th className="text-left p-3 text-sm font-medium text-gray-700 dark:text-gray-300">Motivo</th>
            <th className="text-left p-3 text-sm font-medium text-gray-700 dark:text-gray-300">Status</th>
            <th className="text-left p-3 text-sm font-medium text-gray-700 dark:text-gray-300">Ações</th>
          </tr>
        </thead>
        <tbody>
          {movimentacoes.map((mov) => (
            <tr key={mov.id} className="border-b hover:bg-gray-50 dark:hover:bg-gray-800">
              <td className="p-3 text-sm text-gray-900 dark:text-gray-100">
                {new Date(mov.data_movimentacao).toLocaleString('pt-BR')}
              </td>
              <td className="p-3 text-sm text-gray-900 dark:text-gray-100">
                {mov.usuario?.nome || 'N/A'}
              </td>
              <td className="p-3 text-sm text-gray-900 dark:text-gray-100">
                <div>
                  <div className="font-medium">{mov.produto?.nome || 'Produto não encontrado'}</div>
                  {mov.produto?.codigo && (
                    <div className="text-xs text-gray-500">Código: {mov.produto.codigo}</div>
                  )}
                </div>
              </td>
              <td className="p-3 text-sm text-gray-900 dark:text-gray-100">
                {mov.tipo_movimentacao}
              </td>
              <td className="p-3 text-sm text-gray-900 dark:text-gray-100">
                {mov.quantidade} {mov.produto?.unidade_medida || ''}
              </td>
              <td className="p-3 text-sm text-gray-900 dark:text-gray-100">
                {mov.motivo_movimentacao ? getMotivoLabel(mov.motivo_movimentacao) : 'N/A'}
              </td>
              <td className="p-3">
                {getStatusBadge(mov.status)}
              </td>
              <td className="p-3">
                {mov.status === StatusMovimentacao.PENDENTE ? (
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => onConfirmar(mov)}
                      className="h-8"
                    >
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Confirmar
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => onEditar(mov)}
                      className="h-8"
                    >
                      <Edit className="h-4 w-4 mr-1" />
                      Editar
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => onRejeitar(mov)}
                      className="h-8 text-red-600 hover:text-red-700"
                    >
                      <XCircle className="h-4 w-4 mr-1" />
                      Rejeitar
                    </Button>
                  </div>
                ) : (
                  <span className="text-xs text-gray-500">
                    {mov.aprovado_por?.nome && `Por: ${mov.aprovado_por.nome}`}
                    {mov.data_aprovacao && ` em ${new Date(mov.data_aprovacao).toLocaleDateString('pt-BR')}`}
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

