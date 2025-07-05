// /src/types/index.ts

// A definição principal de um Produto, como vem da API e é usado na UI.
export interface Product {
  id: number;
  nome: string;
  codigo: string;
  categoria: string;
  descricao?: string | null;
  preco_custo?: number | null;
  preco_venda: number;
  unidade_medida: string;
  estoque_minimo?: number | null;
  empresa_id: number;
  quantidade_em_estoque: number;
  data_validade?: string | null;
}

// Dados necessários para criar um novo produto (sem os campos gerados pelo DB).
// Omit é uma forma mais segura de garantir que campos indesejados não sejam enviados.
export type ProdutoCreateData = Omit<Product, 'id' | 'empresa_id' | 'quantidade_em_estoque'>;

// Dados para a atualização de um produto, onde todos os campos são opcionais.
export type ProdutoUpdateData = Partial<Omit<Product, 'id' | 'empresa_id' | 'quantidade_em_estoque'>>;