'use client';

import { useState } from 'react';
import { MovimentacaoPendente } from '@/types';
import { useMovimentacoesPendentesAdmin } from '@/hooks/useMovimentacoesPendentesAdmin';
import { Button } from '@/components/ui/button';
import { Loader2, CheckCircle } from 'lucide-react';

interface ConfirmarMovimentacaoModalProps {
  movimentacao: MovimentacaoPendente;
  onClose: () => void;
}

export function ConfirmarMovimentacaoModal({ movimentacao, onClose }: ConfirmarMovimentacaoModalProps) {
  const { confirmarMovimentacao } = useMovimentacoesPendentesAdmin();
  const [loading, setLoading] = useState(false);

  const handleConfirmar = async () => {
    setLoading(true);
    try {
      await confirmarMovimentacao(movimentacao.id);
      onClose();
    } catch (error) {
      console.error('Erro ao confirmar:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 transition-opacity">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-full max-w-md border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">
          Confirmar Movimentação
        </h2>
        
        <div className="space-y-3 mb-6">
          <div>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Produto:</span>
            <p className="text-gray-900 dark:text-gray-100">{movimentacao.produto?.nome || 'N/A'}</p>
          </div>
          <div>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Tipo:</span>
            <p className="text-gray-900 dark:text-gray-100">{movimentacao.tipo_movimentacao}</p>
          </div>
          <div>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Quantidade:</span>
            <p className="text-gray-900 dark:text-gray-100">
              {movimentacao.quantidade} {movimentacao.produto?.unidade_medida || ''}
            </p>
          </div>
          <div>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Motivo:</span>
            <p className="text-gray-900 dark:text-gray-100">
              {movimentacao.motivo_movimentacao?.replace('_', ' ') || 'N/A'}
            </p>
          </div>
          {movimentacao.observacao && (
            <div>
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Observação:</span>
              <p className="text-gray-900 dark:text-gray-100">{movimentacao.observacao}</p>
            </div>
          )}
        </div>

        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={loading}
            className="flex-1"
          >
            Cancelar
          </Button>
          <Button
            onClick={handleConfirmar}
            disabled={loading}
            className="flex-1"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Confirmando...
              </>
            ) : (
              <>
                <CheckCircle className="mr-2 h-4 w-4" />
                Confirmar
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

