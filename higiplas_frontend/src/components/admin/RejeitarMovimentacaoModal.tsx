'use client';

import { useState } from 'react';
import { MovimentacaoPendente } from '@/types';
import { useMovimentacoesPendentesAdmin } from '@/hooks/useMovimentacoesPendentesAdmin';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, XCircle } from 'lucide-react';

interface RejeitarMovimentacaoModalProps {
  movimentacao: MovimentacaoPendente;
  onClose: () => void;
}

export function RejeitarMovimentacaoModal({ movimentacao, onClose }: RejeitarMovimentacaoModalProps) {
  const { rejeitarMovimentacao } = useMovimentacoesPendentesAdmin();
  const [loading, setLoading] = useState(false);
  const [motivoRejeicao, setMotivoRejeicao] = useState('');

  const handleRejeitar = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!motivoRejeicao.trim()) {
      return;
    }

    setLoading(true);
    try {
      await rejeitarMovimentacao(movimentacao.id, motivoRejeicao);
      onClose();
    } catch (error) {
      console.error('Erro ao rejeitar:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 transition-opacity">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-full max-w-md border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">
          Rejeitar Movimentação
        </h2>
        
        <div className="space-y-3 mb-6">
          <div>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Produto:</span>
            <p className="text-gray-900 dark:text-gray-100">{movimentacao.produto?.nome || 'N/A'}</p>
          </div>
          <div>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Quantidade:</span>
            <p className="text-gray-900 dark:text-gray-100">
              {movimentacao.quantidade} {movimentacao.produto?.unidade_medida || ''}
            </p>
          </div>
        </div>

        <form onSubmit={handleRejeitar} className="space-y-4">
          <div>
            <Label htmlFor="motivoRejeicao">Motivo da Rejeição *</Label>
            <Textarea
              id="motivoRejeicao"
              value={motivoRejeicao}
              onChange={(e) => setMotivoRejeicao(e.target.value)}
              placeholder="Informe o motivo da rejeição..."
              rows={4}
              required
              className="resize-none"
            />
          </div>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
              className="flex-1"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              disabled={loading || !motivoRejeicao.trim()}
              variant="destructive"
              className="flex-1"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Rejeitando...
                </>
              ) : (
                <>
                  <XCircle className="mr-2 h-4 w-4" />
                  Rejeitar
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

