// /src/types/orcamentos.ts

// Tipo para um item DENTRO do carrinho, no frontend.
// Note que tem campos a mais para ajudar a UI, como 'nome' e 'estoque_disponivel'.
export interface ItemCarrinhoOrcamento {
    produto_id?: number; // Opcional: se não tiver, é item personalizado
    nome_produto_personalizado?: string; // Opcional: nome do produto personalizado
    nome: string;
    quantidade: number;
    estoque_disponivel?: number; // Opcional: itens personalizados não têm estoque
    preco_original: number; // Preço de tabela para referência
    preco_unitario_editavel: number; // O preço que o vendedor pode alterar
    isPersonalizado?: boolean; // Flag para identificar itens personalizados
  }
  
  // Tipo para os dados que enviaremos para criar o orçamento no backend.
  export interface OrcamentoItemCreate {
    produto_id?: number; // Opcional: se não tiver, deve ter nome_produto_personalizado
    nome_produto_personalizado?: string; // Opcional: nome do produto personalizado
    quantidade: number;
    preco_unitario: number; // Será o 'preco_unitario_editavel'
  }
  
  export interface OrcamentoCreatePayload {
    cliente_id: number;
    condicao_pagamento: string;
    status: 'RASCUNHO' | 'ENVIADO';
    itens: OrcamentoItemCreate[];
  }
  
  // Tipo para um orçamento que recebemos do backend (no Histórico).
  export interface Orcamento {
    id: number;
    status: string;
    data_criacao: string;
    condicao_pagamento: string;
    token_compartilhamento?: string;
    cliente: {
      id: number;
      razao_social: string;
    };
    usuario: {
      id: number;
      nome: string;
    };
    itens: {
      id: number;
      quantidade: number;
      preco_unitario_congelado: number;
      produto: {
        id: number;
        nome: string;
        codigo: string;
      };
    }[];
  }

  // Tipos para atualização (admin)
  export interface OrcamentoItemUpdate {
    id?: number;
    produto_id: number;
    quantidade: number;
    preco_unitario: number;
  }

  export interface OrcamentoUpdate {
    cliente_id?: number;
    condicao_pagamento?: string;
    status?: string;
    itens?: OrcamentoItemUpdate[];
  }

  export interface OrcamentoStatusUpdate {
    status: string;
  }