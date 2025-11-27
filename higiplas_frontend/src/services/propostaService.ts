// src/services/propostaService.ts

import { apiService } from './apiService';

export interface FichaTecnica {
  id: number;
  produto_id?: number;
  nome_produto: string;
  dilucao_recomendada?: string;
  dilucao_numerador?: number;
  dilucao_denominador?: number;
  rendimento_litro?: number;
  modo_uso?: string;
  arquivo_pdf_path?: string;
  observacoes?: string;
  data_criacao: string;
  data_atualizacao?: string;
}

export interface ProdutoConcorrente {
  id: number;
  nome: string;
  marca?: string;
  preco_medio?: number;
  rendimento_litro?: number;
  dilucao?: string;
  dilucao_numerador?: number;
  dilucao_denominador?: number;
  categoria?: string;
  observacoes?: string;
  ativo: boolean;
  data_criacao: string;
  data_atualizacao?: string;
}

export interface ComparacaoConcorrente {
  concorrente_id: number;
  concorrente_nome: string;
  concorrente_marca?: string;
  preco_concorrente?: number;
  rendimento_concorrente?: number;
  custo_por_litro_concorrente?: number;
  economia_percentual?: number;
  economia_valor?: number;
}

export interface ComparacaoConcorrenteManual {
  id: number;
  nome: string;
  rendimento_litro?: number;
  custo_por_litro?: number;
  observacoes?: string;
  ordem?: number;
}

export interface PropostaDetalhadaItem {
  id: number;
  proposta_id: number;
  produto_id: number;
  quantidade_produto: number;
  dilucao_aplicada?: string;
  dilucao_numerador?: number;
  dilucao_denominador?: number;
  rendimento_total_litros?: number;
  preco_produto?: number;
  custo_por_litro_final?: number;
  observacoes?: string;
  ordem?: number;
  concorrente_nome_manual?: string;
  concorrente_rendimento_manual?: number;
  concorrente_custo_por_litro_manual?: number;
  produto_nome?: string;
}

export interface PropostaDetalhadaItemCreatePayload {
  produto_id: number;
  quantidade_produto: number;
  dilucao_aplicada?: string;
  dilucao_numerador?: number;
  dilucao_denominador?: number;
  observacoes?: string;
  ordem?: number;
  concorrente_nome_manual?: string;
  concorrente_rendimento_manual?: number;
  concorrente_custo_por_litro_manual?: number;
}

export interface ComparacaoConcorrenteManualCreate {
  nome: string;
  rendimento_litro?: number;
  custo_por_litro?: number;
  observacoes?: string;
  ordem?: number;
}

export interface PropostaDetalhada {
  id: number;
  orcamento_id?: number;
  cliente_id: number;
  vendedor_id: number;
  produto_id: number;
  ficha_tecnica_id?: number;
  quantidade_produto: number;
  dilucao_aplicada?: string;
  dilucao_numerador?: number;
  dilucao_denominador?: number;
  rendimento_total_litros?: number;
  preco_produto?: number;
  custo_por_litro_final?: number;
  concorrente_id?: number;
  economia_vs_concorrente?: number;
  economia_percentual?: number;
  economia_valor?: number;
  observacoes?: string;
  compartilhavel: boolean;
  token_compartilhamento?: string;
  data_criacao: string;
  data_atualizacao?: string;
  produto_nome?: string;
  cliente_nome?: string;
  vendedor_nome?: string;
  ficha_tecnica?: FichaTecnica;
  concorrente?: ProdutoConcorrente;
  comparacoes?: ComparacaoConcorrente[];
  itens: PropostaDetalhadaItem[];
  comparacoes_personalizadas?: ComparacaoConcorrenteManual[];
}

export interface PropostaDetalhadaCreate {
  orcamento_id?: number;
  cliente_id: number;
  observacoes?: string;
  compartilhavel?: boolean;
  itens: PropostaDetalhadaItemCreatePayload[];
  comparacoes_personalizadas?: ComparacaoConcorrenteManualCreate[];
}

// ============= FICHAS TÉCNICAS =============

export const fichaTecnicaService = {
  async getByProduto(produtoId: number): Promise<FichaTecnica | null> {
    try {
      const response = await apiService.get(`/fichas-tecnicas/produto/${produtoId}`);
      return response?.data ?? null;
    } catch (error) {
      if (error instanceof Error && error.message.includes('404')) {
        return null;
      }
      throw error;
    }
  },

  async getAll(skip = 0, limit = 100): Promise<FichaTecnica[]> {
    const response = await apiService.get(`/fichas-tecnicas?skip=${skip}&limit=${limit}`);
    return response?.data ?? [];
  },

  async processarPasta(pasta: string): Promise<FichaTecnica[]> {
    const response = await apiService.post(`/fichas-tecnicas/processar-pasta?pasta=${encodeURIComponent(pasta)}`, {});
    return response?.data ?? [];
  },

  async create(ficha: Partial<FichaTecnica>): Promise<FichaTecnica> {
    const response = await apiService.post('/fichas-tecnicas', ficha);
    if (!response?.data) {
      throw new Error('Resposta inválida ao criar ficha técnica');
    }
    return response.data;
  },

  async update(fichaId: number, ficha: Partial<FichaTecnica>): Promise<FichaTecnica> {
    const response = await apiService.put(`/fichas-tecnicas/${fichaId}`, ficha);
    if (!response?.data) {
      throw new Error('Resposta inválida ao atualizar ficha técnica');
    }
    return response.data;
  },

  async delete(fichaId: number): Promise<void> {
    await apiService.delete(`/fichas-tecnicas/${fichaId}`);
  },
};

// ============= CONCORRENTES =============

export const concorrenteService = {
  async getAll(categoria?: string, ativo = true): Promise<ProdutoConcorrente[]> {
    const params = new URLSearchParams();
    if (categoria) params.append('categoria', categoria);
    params.append('ativo', ativo.toString());
    const response = await apiService.get(`/concorrentes?${params.toString()}`);
    return response?.data ?? [];
  },

  async getById(concorrenteId: number): Promise<ProdutoConcorrente> {
    const response = await apiService.get(`/concorrentes/${concorrenteId}`);
    if (!response?.data) {
      throw new Error('Concorrente não encontrado');
    }
    return response.data;
  },

  async getByCategoria(categoria: string): Promise<ProdutoConcorrente[]> {
    const response = await apiService.get(`/concorrentes/categoria/${categoria}`);
    return response?.data ?? [];
  },

  async create(concorrente: Partial<ProdutoConcorrente>): Promise<ProdutoConcorrente> {
    const response = await apiService.post('/concorrentes', concorrente);
    if (!response?.data) {
      throw new Error('Resposta inválida ao criar concorrente');
    }
    return response.data;
  },

  async update(concorrenteId: number, concorrente: Partial<ProdutoConcorrente>): Promise<ProdutoConcorrente> {
    const response = await apiService.put(`/concorrentes/${concorrenteId}`, concorrente);
    if (!response?.data) {
      throw new Error('Resposta inválida ao atualizar concorrente');
    }
    return response.data;
  },

  async delete(concorrenteId: number): Promise<void> {
    await apiService.delete(`/concorrentes/${concorrenteId}`);
  },
};

// ============= PROPOSTAS DETALHADAS =============

export const propostaService = {
  async create(proposta: PropostaDetalhadaCreate): Promise<PropostaDetalhada> {
    const response = await apiService.post('/propostas-detalhadas/', proposta);
    if (!response?.data) {
      throw new Error('Resposta inválida ao criar proposta');
    }
    return response.data;
  },

  async getMyPropostas(skip = 0, limit = 100): Promise<PropostaDetalhada[]> {
    const response = await apiService.get(`/propostas-detalhadas/me?skip=${skip}&limit=${limit}`);
    return response?.data ?? [];
  },

  async getById(propostaId: number): Promise<PropostaDetalhada> {
    const response = await apiService.get(`/propostas-detalhadas/${propostaId}`);
    if (!response?.data) {
      throw new Error('Proposta não encontrada');
    }
    return response.data;
  },

  async getByCliente(clienteId: number, skip = 0, limit = 100): Promise<PropostaDetalhada[]> {
    const response = await apiService.get(`/propostas-detalhadas/cliente/${clienteId}?skip=${skip}&limit=${limit}`);
    return response?.data ?? [];
  },

  async getAll(skip = 0, limit = 100): Promise<PropostaDetalhada[]> {
    const response = await apiService.get(`/propostas-detalhadas/admin/todas?skip=${skip}&limit=${limit}`);
    return response?.data ?? [];
  },

  async compartilhar(propostaId: number): Promise<PropostaDetalhada> {
    const response = await apiService.post(`/propostas-detalhadas/${propostaId}/compartilhar`, {});
    if (!response?.data) {
      throw new Error('Resposta inválida ao compartilhar proposta');
    }
    return response.data;
  },

  async getCompartilhada(token: string): Promise<PropostaDetalhada> {
    const response = await apiService.get(`/propostas-detalhadas/compartilhar/${token}`);
    if (!response?.data) {
      throw new Error('Proposta compartilhada não encontrada');
    }
    return response.data;
  },

  async update(propostaId: number, proposta: Partial<PropostaDetalhadaCreate>): Promise<PropostaDetalhada> {
    const response = await apiService.put(`/propostas-detalhadas/${propostaId}`, proposta);
    if (!response?.data) {
      throw new Error('Resposta inválida ao atualizar proposta');
    }
    return response.data;
  },

  async delete(propostaId: number): Promise<void> {
    await apiService.delete(`/propostas-detalhadas/${propostaId}`);
  },

  // Funções auxiliares de cálculo
  calcularRendimento(
    quantidade: number,
    dilucaoNumerador?: number,
    dilucaoDenominador?: number
  ): number | null {
    if (!dilucaoNumerador || !dilucaoDenominador || dilucaoNumerador === 0) {
      return null;
    }
    return quantidade * (dilucaoDenominador / dilucaoNumerador);
  },

  calcularCustoPorLitro(
    precoProduto: number,
    quantidade: number,
    rendimentoTotal: number | null
  ): number | null {
    if (!rendimentoTotal || rendimentoTotal === 0) {
      return null;
    }
    const custoTotal = precoProduto * quantidade;
    return custoTotal / rendimentoTotal;
  },
};

