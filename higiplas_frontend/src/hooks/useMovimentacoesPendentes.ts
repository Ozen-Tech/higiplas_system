// Hook para gerenciar movimentações pendentes do entregador
import { useState, useEffect, useCallback } from 'react';
import { MovimentacaoPendente, MovimentacaoPendenteCreate } from '@/types';
import { movimentacoesPendentesService } from '@/services/movimentacoesPendentes';
import toast from 'react-hot-toast';

export function useMovimentacoesPendentes(status?: string) {
  const [movimentacoes, setMovimentacoes] = useState<MovimentacaoPendente[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const carregarMovimentacoes = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await movimentacoesPendentesService.getByUser(status);
      setMovimentacoes(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar movimentações';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [status]);

  useEffect(() => {
    carregarMovimentacoes();
  }, [carregarMovimentacoes]);

  const criarMovimentacao = useCallback(async (movimentacao: MovimentacaoPendenteCreate) => {
    try {
      const nova = await movimentacoesPendentesService.create(movimentacao);
      setMovimentacoes(prev => [nova, ...prev]);
      toast.success('Movimentação registrada com sucesso! Aguardando aprovação.');
      return nova;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao criar movimentação';
      toast.error(errorMessage);
      throw err;
    }
  }, []);

  return {
    movimentacoes,
    loading,
    error,
    carregarMovimentacoes,
    criarMovimentacao,
  };
}

