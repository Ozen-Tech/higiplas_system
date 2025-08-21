import { useState, useCallback } from 'react';
import { apiService } from '@/services/apiService';

// Re-use o tipo do seu schema do backend para manter a consistência
export interface Orcamento {
  id: number;
  nome_cliente: string;
  status: string;
  data_criacao: string;
  itens: { produto: { nome: string } }[]; // Apenas o que precisamos para a lista
}

export function useOrcamentos() {
  const [orcamentos, setOrcamentos] = useState<Orcamento[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchOrcamentos = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiService.get('/orcamentos/');
      setOrcamentos(data?.data || []);
    } catch (error) {
      console.error("Falha ao buscar orçamentos", error);
    } finally {
      setLoading(false);
    }
  }, []);

  return { orcamentos, loading, fetchOrcamentos };
}