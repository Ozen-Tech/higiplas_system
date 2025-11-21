// Hook para gerenciar movimentações pendentes no dashboard admin
import { useState, useEffect, useCallback } from 'react';
import { MovimentacaoPendente, MotivoMovimentacao } from '@/types';
import { movimentacoesPendentesService } from '@/services/movimentacoesPendentes';
import toast from 'react-hot-toast';

interface EdicaoMovimentacao {
  produto_id?: number;
  quantidade?: number;
  tipo_movimentacao?: 'ENTRADA' | 'SAIDA';
  motivo_movimentacao?: MotivoMovimentacao;
  observacao?: string;
  observacao_motivo?: string;
}

export function useMovimentacoesPendentesAdmin(status?: string) {
  const [movimentacoes, setMovimentacoes] = useState<MovimentacaoPendente[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const carregarMovimentacoes = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await movimentacoesPendentesService.getAllAdmin(status);
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

  const confirmarMovimentacao = useCallback(async (movimentacaoId: number) => {
    try {
      await movimentacoesPendentesService.confirm(movimentacaoId);
      toast.success('Movimentação confirmada com sucesso!');
      await carregarMovimentacoes();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao confirmar movimentação';
      toast.error(errorMessage);
      throw err;
    }
  }, [carregarMovimentacoes]);

  const editarMovimentacao = useCallback(async (movimentacaoId: number, edicao: EdicaoMovimentacao) => {
    try {
      await movimentacoesPendentesService.edit(movimentacaoId, edicao);
      toast.success('Movimentação editada com sucesso!');
      await carregarMovimentacoes();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao editar movimentação';
      toast.error(errorMessage);
      throw err;
    }
  }, [carregarMovimentacoes]);

  const editarEConfirmarMovimentacao = useCallback(async (movimentacaoId: number, edicao: EdicaoMovimentacao) => {
    try {
      await movimentacoesPendentesService.editAndConfirm(movimentacaoId, edicao);
      toast.success('Movimentação editada e confirmada com sucesso!');
      await carregarMovimentacoes();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao editar movimentação';
      toast.error(errorMessage);
      throw err;
    }
  }, [carregarMovimentacoes]);

  const rejeitarMovimentacao = useCallback(async (movimentacaoId: number, motivoRejeicao: string) => {
    try {
      await movimentacoesPendentesService.reject(movimentacaoId, motivoRejeicao);
      toast.success('Movimentação rejeitada.');
      await carregarMovimentacoes();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao rejeitar movimentação';
      toast.error(errorMessage);
      throw err;
    }
  }, [carregarMovimentacoes]);

  return {
    movimentacoes,
    loading,
    error,
    carregarMovimentacoes,
    confirmarMovimentacao,
    editarMovimentacao,
    editarEConfirmarMovimentacao,
    rejeitarMovimentacao,
  };
}

