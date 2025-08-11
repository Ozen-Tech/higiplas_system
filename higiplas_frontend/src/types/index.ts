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

export interface OrcamentoItem {
  produto_id: number;
  nome: string; // Adicionamos nome e estoque para exibir na UI
  estoque_disponivel: number;
  quantidade: number;
  preco_unitario: number;
}

export interface Orcamento {
  id: number;
  nome_cliente: string;
  status: string;
  data_criacao: string; // Vem como string da API
  data_validade?: string | null;
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

export interface User {
  id: number;
  nome: string;
  email: string;
  perfil: 'ADMIN' | 'GESTOR' | 'OPERADOR';
  is_active: boolean;
  xp?: number;
  level?: number;
}

export interface OrdemDeCompraItem {
  id: number;
  produto_id: number;
  quantidade_solicitada: number;
  custo_unitario_registrado: number;
  produto: Product; // Inclui os dados completos do produto
}

export interface OrdemDeCompra {
  id: number;
  status: string;
  data_criacao: string;
  data_recebimento?: string | null;
  usuario_id: number;
  fornecedor: {
    id: number;
    nome: string;
  };
  itens: OrdemDeCompraItem[];
}


// Dados necessários para criar um novo produto (sem os campos gerados pelo DB).
export type ProdutoCreateData = Omit<Product, 'id' | 'empresa_id' | 'quantidade_em_estoque'>;

// Dados para a atualização de um produto, onde todos os campos são opcionais.
export type ProdutoUpdateData = Partial<Omit<Product, 'id' | 'empresa_id' | 'quantidade_em_estoque'>>;

// Tipos para Clientes
export interface Endereco {
  id: number;
  logradouro: string;
  numero: string;
  complemento?: string | null;
  bairro: string;
  cidade: string;
  estado: string;
  cep: string;
  tipo: 'RESIDENCIAL' | 'COMERCIAL' | 'ENTREGA';
}

export interface Cliente {
  id: number;
  nome: string;
  email?: string | null;
  telefone?: string | null;
  cpf_cnpj?: string | null;
  tipo_pessoa: 'FISICA' | 'JURIDICA';
  data_cadastro: string;
  ativo: boolean;
  observacoes?: string | null;
  empresa_id: number;
  endereco?: {
    logradouro?: string;
    numero?: string;
    complemento?: string | null;
    bairro?: string;
    cidade?: string;
    estado?: string;
    cep?: string;
    tipo?: 'RESIDENCIAL' | 'COMERCIAL' | 'ENTREGA';
  };
  enderecos: Endereco[];
}

export interface ClienteCreate {
  nome: string;
  email?: string | null;
  telefone?: string | null;
  cpf_cnpj?: string | null;
  tipo_pessoa: 'FISICA' | 'JURIDICA';
  observacoes?: string | null;
  ativo?: boolean;
  endereco?: {
    logradouro?: string;
    numero?: string;
    complemento?: string | null;
    bairro?: string;
    cidade?: string;
    estado?: string;
    cep?: string;
    tipo?: 'RESIDENCIAL' | 'COMERCIAL' | 'ENTREGA';
  };
}

export interface ClienteUpdate {
  nome?: string;
  email?: string | null;
  telefone?: string | null;
  cpf_cnpj?: string | null;
  tipo_pessoa?: 'FISICA' | 'JURIDICA';
  observacoes?: string | null;
  ativo?: boolean;
  endereco?: {
    logradouro?: string;
    numero?: string;
    complemento?: string | null;
    bairro?: string;
    cidade?: string;
    estado?: string;
    cep?: string;
    tipo?: 'RESIDENCIAL' | 'COMERCIAL' | 'ENTREGA';
  };
}

export interface HistoricoPagamento {
  id: number;
  cliente_id: number;
  valor: number;
  data_pagamento: string;
  metodo_pagamento: 'DINHEIRO' | 'CARTAO_CREDITO' | 'CARTAO_DEBITO' | 'PIX' | 'TRANSFERENCIA' | 'BOLETO' | 'CHEQUE';
  observacoes?: string | null;
  orcamento_id?: number | null;
  status?: string;
}

export interface HistoricoPagamentoCreate {
  cliente_id: number;
  valor: number;
  data_pagamento: string;
  metodo_pagamento: 'DINHEIRO' | 'CARTAO_CREDITO' | 'CARTAO_DEBITO' | 'PIX' | 'TRANSFERENCIA' | 'BOLETO' | 'CHEQUE';
  observacoes?: string | null;
  orcamento_id?: number | null;
}

export interface ResumoVendasCliente {
  mes: string;
  total_vendas: number;
  quantidade_orcamentos: number;
  total_orcamentos?: number;
  valor_total_vendas?: number;
  valor_medio_orcamento?: number;
  ultimo_orcamento?: string;
}