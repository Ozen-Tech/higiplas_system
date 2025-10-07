// /src/types/orcamentos.ts

// Tipo para um item DENTRO do carrinho, no frontend.
// Note que tem campos a mais para ajudar a UI, como 'nome' e 'estoque_disponivel'.
export interface ItemCarrinhoOrcamento {
    produto_id: number;
    nome: string;
    quantidade: number;
    estoque_disponivel: number;
    preco_original: number; // Preço de tabela para referência
    preco_unitario_editavel: number; // O preço que o vendedor pode alterar
  }
  
  // Tipo para os dados que enviaremos para criar o orçamento no backend.
  export interface OrcamentoItemCreate {
    produto_id: number;
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