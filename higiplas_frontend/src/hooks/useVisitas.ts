import { useState, useCallback } from 'react';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';

export interface VisitaVendedor {
  id: number;
  vendedor_id: number;
  cliente_id?: number;
  data_visita: string;
  latitude: number;
  longitude: number;
  endereco_completo?: string;
  motivo_visita?: string;
  observacoes?: string;
  foto_comprovante?: string;
  confirmada: boolean;
  empresa_id: number;
  criado_em: string;
  atualizado_em?: string;
  vendedor_nome?: string;
  cliente_nome?: string;
  empresa_nome?: string;
}

export interface VisitaCreate {
  vendedor_id: number;
  cliente_id?: number;
  latitude: number;
  longitude: number;
  endereco_completo?: string;
  motivo_visita?: string;
  observacoes?: string;
  foto_comprovante?: string;
  empresa_id: number;
}

export interface VisitaUpdate {
  cliente_id?: number;
  motivo_visita?: string;
  observacoes?: string;
  foto_comprovante?: string;
}

export interface VisitaStats {
  total_visitas: number;
  visitas_hoje: number;
  visitas_semana: number;
  visitas_mes: number;
  visitas_confirmadas: number;
  visitas_pendentes: number;
}

export function useVisitas() {
  const [visitas, setVisitas] = useState<VisitaVendedor[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<VisitaStats | null>(null);

  const handleApiError = useCallback((err: unknown, defaultMessage: string) => {
    const errorMessage = err instanceof Error ? err.message : defaultMessage;
    toast.error(errorMessage);
    setError(errorMessage);
  }, []);

  const criarVisita = useCallback(async (visita: VisitaCreate): Promise<VisitaVendedor | null> => {
    setLoading(true);
    try {
      const response = await apiService.post('/visitas/', visita);
      toast.success('Visita registrada com sucesso!');
      return response?.data || null;
    } catch (err) {
      handleApiError(err, 'Erro ao registrar visita.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  const listarVisitas = useCallback(async (
    vendedor_id?: number,
    confirmada?: boolean,
    limit: number = 100,
    offset: number = 0
  ) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (vendedor_id) params.append('vendedor_id', vendedor_id.toString());
      if (confirmada !== undefined) params.append('confirmada', confirmada.toString());
      params.append('limit', limit.toString());
      params.append('offset', offset.toString());
      
      const url = `/visitas/?${params.toString()}`;
      const response = await apiService.get(url);
      const visitasList = response?.data || [];
      setVisitas(visitasList);
      return visitasList;
    } catch (err) {
      handleApiError(err, 'Erro ao listar visitas.');
      return [];
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  const listarVisitasMapa = useCallback(async (
    vendedor_id?: number,
    cliente_id?: number,
    data_inicio?: string,
    data_fim?: string,
    limit: number = 1000
  ) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (vendedor_id) params.append('vendedor_id', vendedor_id.toString());
      if (cliente_id) params.append('cliente_id', cliente_id.toString());
      if (data_inicio) params.append('data_inicio', data_inicio);
      if (data_fim) params.append('data_fim', data_fim);
      params.append('limit', limit.toString());
      
      const url = `/visitas/mapa?${params.toString()}`;
      const response = await apiService.get(url);
      const visitasList = response?.data || [];
      return visitasList;
    } catch (err) {
      handleApiError(err, 'Erro ao buscar visitas para mapa.');
      return [];
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  const atualizarVisita = useCallback(async (
    visita_id: number,
    update: VisitaUpdate
  ): Promise<VisitaVendedor | null> => {
    setLoading(true);
    try {
      const response = await apiService.patch(`/visitas/${visita_id}`, update);
      toast.success('Visita atualizada com sucesso!');
      return response?.data || null;
    } catch (err) {
      handleApiError(err, 'Erro ao atualizar visita.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  const confirmarVisita = useCallback(async (visita_id: number): Promise<VisitaVendedor | null> => {
    try {
      const response = await apiService.post(`/visitas/${visita_id}/confirmar`, {});
      toast.success('Visita confirmada com sucesso!');
      const visitaConfirmada = response?.data || null;
      // Atualizar lista local
      if (visitaConfirmada) {
        setVisitas(prev => prev.map(v => v.id === visita_id ? visitaConfirmada : v));
      }
      return visitaConfirmada;
    } catch (err) {
      handleApiError(err, 'Erro ao confirmar visita.');
      return null;
    }
  }, [handleApiError]);

  const buscarVisita = useCallback(async (visita_id: number): Promise<VisitaVendedor | null> => {
    setLoading(true);
    try {
      const response = await apiService.get(`/visitas/${visita_id}`);
      return response?.data || null;
    } catch (err) {
      handleApiError(err, 'Erro ao buscar visita.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  const obterEstatisticas = useCallback(async (
    vendedor_id?: number,
    periodo_dias: number = 30
  ) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (vendedor_id) params.append('vendedor_id', vendedor_id.toString());
      params.append('periodo_dias', periodo_dias.toString());
      
      const url = `/visitas/stats/estatisticas?${params.toString()}`;
      const response = await apiService.get(url);
      const statsData = response?.data || null;
      setStats(statsData);
      return statsData;
    } catch (err) {
      handleApiError(err, 'Erro ao obter estatísticas.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  const removerVisita = useCallback(async (visita_id: number): Promise<boolean> => {
    setLoading(true);
    try {
      await apiService.delete(`/visitas/${visita_id}`);
      toast.success('Visita removida com sucesso!');
      return true;
    } catch (err) {
      handleApiError(err, 'Erro ao remover visita.');
      return false;
    } finally {
      setLoading(false);
    }
  }, [handleApiError]);

  return {
    visitas,
    loading,
    error,
    stats,
    criarVisita,
    listarVisitas,
    listarVisitasMapa,
    atualizarVisita,
    confirmarVisita,
    buscarVisita,
    obterEstatisticas,
    removerVisita
  };
}
