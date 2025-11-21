import { MovimentacaoPendente, MovimentacaoPendenteCreate } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function getAuthToken(): string | null {
  return localStorage.getItem('authToken');
}

function getAuthHeaders(): HeadersInit {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

export const movimentacoesPendentesService = {
  async create(movimentacao: MovimentacaoPendenteCreate): Promise<MovimentacaoPendente> {
    const response = await fetch(`${API_BASE_URL}/movimentacoes/pendentes`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(movimentacao),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erro ao criar movimentação pendente' }));
      throw new Error(error.detail || 'Erro ao criar movimentação pendente');
    }

    return response.json();
  },

  async getByUser(status?: string): Promise<MovimentacaoPendente[]> {
    const url = new URL(`${API_BASE_URL}/movimentacoes/pendentes`);
    if (status) {
      url.searchParams.append('status', status);
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erro ao listar movimentações' }));
      throw new Error(error.detail || 'Erro ao listar movimentações');
    }

    return response.json();
  },

  async getAllAdmin(status?: string): Promise<MovimentacaoPendente[]> {
    const url = new URL(`${API_BASE_URL}/movimentacoes/pendentes/admin`);
    if (status) {
      url.searchParams.append('status', status);
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erro ao listar movimentações' }));
      throw new Error(error.detail || 'Erro ao listar movimentações');
    }

    return response.json();
  },

  async confirm(movimentacaoId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/movimentacoes/pendentes/${movimentacaoId}/confirmar`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erro ao confirmar movimentação' }));
      throw new Error(error.detail || 'Erro ao confirmar movimentação');
    }
  },

  async editAndConfirm(movimentacaoId: number, edicao: Partial<MovimentacaoPendenteCreate>): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/movimentacoes/pendentes/${movimentacaoId}/editar`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(edicao),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erro ao editar movimentação' }));
      throw new Error(error.detail || 'Erro ao editar movimentação');
    }
  },

  async reject(movimentacaoId: number, motivoRejeicao: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/movimentacoes/pendentes/${movimentacaoId}/rejeitar`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ motivo_rejeicao: motivoRejeicao }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erro ao rejeitar movimentação' }));
      throw new Error(error.detail || 'Erro ao rejeitar movimentação');
    }
  },
};

