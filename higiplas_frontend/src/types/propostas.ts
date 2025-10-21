// higiplas_frontend/src/types/propostas.ts

// Tipo para um item da proposta no frontend
export interface ItemPropostaCreate {
  produto_nome: string;
  descricao?: string;
  valor: number;
  rendimento_litros?: string;
  custo_por_litro?: number;
}

// Tipo para criar uma nova proposta
export interface PropostaCreatePayload {
  cliente_id: number;
  status: 'RASCUNHO' | 'ENVIADA';
  observacoes?: string;
  itens: ItemPropostaCreate[];
}

// Tipo para uma proposta recebida do backend
export interface Proposta {
  id: number;
  status: string;
  data_criacao: string;
  data_validade?: string;
  observacoes?: string;
  cliente: {
    id: number;
    razao_social: string;
    telefone?: string;
    email?: string;
    endereco?: string;
  };
  usuario: {
    id: number;
    nome: string;
    email: string;
  };
  itens: {
    id: number;
    produto_nome: string;
    descricao?: string;
    valor: number;
    rendimento_litros?: string;
    custo_por_litro?: number;
  }[];
}

// Tipo para atualizar uma proposta
export interface PropostaUpdatePayload {
  status?: string;
  observacoes?: string;
  data_validade?: string;
}
