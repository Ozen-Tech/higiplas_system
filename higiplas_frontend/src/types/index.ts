// /src/types/index.ts

// ======================== PRODUTOS ========================

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
  creationDate: string;
}

export type ProdutoCreateData = Omit<Product, 'id' | 'empresa_id' | 'quantidade_em_estoque' | 'creationDate'>;

export type ProdutoUpdateData = Partial<Omit<Product, 'id' | 'empresa_id' | 'quantidade_em_estoque'>>;


// ======================== ORÇAMENTOS ========================

export interface OrcamentoItem {
  produto_id: number;
  nome: string;
  estoque_disponivel: number;
  quantidade: number;
  preco_unitario: number;
}

export interface Orcamento {
  id: number;
  nome_cliente: string;
  status: string;
  data_criacao: string;
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


// ======================== USUÁRIOS ========================

export interface User {
  id: number;
  nome: string;
  email: string;
  perfil: 'ADMIN' | 'GESTOR' | 'OPERADOR';
  is_active: boolean;
  xp?: number;
  level?: number;
  foto_perfil?: string | null;
  data_criacao?: string;
}

export interface UserUpdate {
  nome?: string;
  email?: string;
  foto_perfil?: string | null;
}

export interface UserPasswordUpdate {
  senha_atual: string;
  nova_senha: string;
}

// ======================== MOVIMENTAÇÕES PENDENTES ========================

export enum StatusMovimentacao {
  PENDENTE = 'PENDENTE',
  CONFIRMADO = 'CONFIRMADO',
  REJEITADO = 'REJEITADO'
}

export enum MotivoMovimentacao {
  CARREGAMENTO = 'CARREGAMENTO',
  DEVOLUCAO = 'DEVOLUCAO',
  AJUSTE_FISICO = 'AJUSTE_FISICO',
  PERDA_AVARIA = 'PERDA_AVARIA',
  TRANSFERENCIA_INTERNA = 'TRANSFERENCIA_INTERNA'
}

export interface MovimentacaoPendente {
  id: number;
  produto_id: number;
  quantidade: number;
  tipo_movimentacao: 'ENTRADA' | 'SAIDA';
  observacao?: string | null;
  origem?: string | null;
  data_movimentacao: string;
  quantidade_antes?: number | null;
  quantidade_depois?: number | null;
  status: StatusMovimentacao;
  aprovado_por_id?: number | null;
  data_aprovacao?: string | null;
  motivo_rejeicao?: string | null;
  motivo_movimentacao?: MotivoMovimentacao | null;
  observacao_motivo?: string | null;
  produto?: Product;
  usuario?: User;
  aprovado_por?: User;
}

export interface MovimentacaoPendenteCreate {
  produto_id: number;
  quantidade: number;
  tipo_movimentacao: 'ENTRADA' | 'SAIDA';
  motivo_movimentacao: MotivoMovimentacao;
  observacao?: string | null;
  observacao_motivo?: string | null;
}


// ======================== ORDENS DE COMPRA ========================

export interface OrdemDeCompraItem {
  id: number;
  produto_id: number;
  quantidade_solicitada: number;
  custo_unitario_registrado: number;
  produto: Product;
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


// ======================== SUGESTÕES DE COMPRA ========================

export interface PurchaseSuggestion {
  produto_id: number;
  produto_nome: string;
  codigo?: string | null;
  categoria?: string | null;
  estoque_atual: number;
  estoque_minimo_atual: number;
  estoque_minimo_calculado: number;
  demanda_media_diaria: number;
  demanda_maxima_diaria: number;
  total_vendido_periodo: number;
  numero_vendas: number;
  dias_com_vendas: number;
  dias_cobertura_atual: number;
  quantidade_sugerida: number;
  status: 'CRÍTICO' | 'BAIXO' | 'ADEQUADO';
  tem_historico_suficiente: boolean;
  fornecedor_id?: number | null;
  fornecedor_nome?: string | null;
  preco_custo?: number | null;
  preco_venda?: number | null;
  valor_estimado_compra: number;
  periodo_analise_dias: number;
  lead_time_dias: number;
  coverage_days: number;
}

export interface PurchaseSuggestionResponse {
  total_sugestoes: number;
  sugestoes_criticas: number;
  sugestoes_baixas: number;
  sugestoes: PurchaseSuggestion[];
  data_analise: string;
}

export interface ProductAnalysisResponse {
  produto_id: number;
  produto_nome: string;
  codigo?: string | null;
  categoria?: string | null;
  estoque_atual: number;
  estoque_minimo_atual: number;
  estoque_minimo_calculado: number;
  demanda_media_diaria: number;
  demanda_maxima_diaria: number;
  total_vendido_periodo: number;
  numero_vendas: number;
  dias_com_vendas: number;
  dias_cobertura_atual: number | string;
  quantidade_sugerida: number;
  precisa_compra: boolean;
  status: 'CRÍTICO' | 'BAIXO' | 'ADEQUADO' | 'SEM_HISTORICO';
  tem_historico_suficiente: boolean;
  fornecedor_id?: number | null;
  fornecedor_nome?: string | null;
  preco_custo?: number | null;
  preco_venda?: number | null;
  valor_estimado_compra: number;
  periodo_analise_dias: number;
  lead_time_dias: number;
  coverage_days: number;
}


// ======================== CLIENTES (NOVO MODELO V2) ========================

export interface ClienteV2 {
  id: number;
  nome: string;
  telefone: string;
  tipo_pessoa: 'FISICA' | 'JURIDICA';
  cpf_cnpj?: string;
  bairro?: string;
  cidade?: string;
  observacoes?: string;
  referencia_localizacao?: string;
  status: 'ATIVO' | 'INATIVO' | 'PROSPECTO';
  vendedor_id: number;
  vendedor_nome?: string;
  empresa_id: number;
  total_vendas?: number;
  ultima_venda?: string;
  criado_em: string;
  atualizado_em?: string;
}

export interface ClienteQuickCreate {
  nome: string;
  telefone: string;
}

export interface ClienteCreateV2 {
  nome: string;
  telefone: string;
  tipo_pessoa?: 'FISICA' | 'JURIDICA';
  cpf_cnpj?: string;
  bairro?: string;
  cidade?: string;
  observacoes?: string;
  referencia_localizacao?: string;
}

export interface ClienteUpdateV2 {
  nome?: string;
  telefone?: string;
  tipo_pessoa?: 'FISICA' | 'JURIDICA';
  cpf_cnpj?: string;
  bairro?: string;
  cidade?: string;
  observacoes?: string;
  referencia_localizacao?: string;
  status?: 'ATIVO' | 'INATIVO' | 'PROSPECTO';
}

export interface ClienteListItemV2 {
  id: number;
  nome: string;
  telefone: string;
  bairro?: string;
  cidade?: string;
  status: 'ATIVO' | 'INATIVO' | 'PROSPECTO';
  ultima_venda?: string;
}

export interface ClienteStats {
  total_orcamentos: number;
  total_vendido: number;
  ticket_medio: number;
  produtos_mais_comprados: Array<{
    produto: string;
    quantidade: number;
    valor_total: number;
  }>;
  historico_vendas: Array<{
    data: string;
    valor: number;
    id: number;
  }>;
}

export interface ClienteSearchParams {
  search?: string;
  bairro?: string;
  cidade?: string;
  meus_clientes?: boolean;
  skip?: number;
  limit?: number;
}


// ======================== CLIENTES (MODELO ANTIGO) ========================

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


// ======================== HISTÓRICO DE PAGAMENTOS ========================

export interface HistoricoPagamento {
  id: number;
  cliente_id: number;
  valor: number;
  data_pagamento: string;
  metodo_pagamento: 
    | 'DINHEIRO' 
    | 'CARTAO_CREDITO' 
    | 'CARTAO_DEBITO' 
    | 'PIX' 
    | 'TRANSFERENCIA' 
    | 'BOLETO' 
    | 'CHEQUE';
  observacoes?: string | null;
  orcamento_id?: number | null;
  status?: string;
}

export interface HistoricoPagamentoCreate {
  cliente_id: number;
  valor: number;
  data_pagamento: string;
  metodo_pagamento: 
    | 'DINHEIRO' 
    | 'CARTAO_CREDITO' 
    | 'CARTAO_DEBITO' 
    | 'PIX' 
    | 'TRANSFERENCIA' 
    | 'BOLETO' 
    | 'CHEQUE';
  observacoes?: string | null;
  orcamento_id?: number | null;
}


// ======================== RESUMO DE VENDAS ========================

export interface ResumoVendasCliente {
  mes: string;
  total_vendas: number;
  quantidade_orcamentos: number;
  total_orcamentos?: number;
  valor_total_vendas?: number;
  valor_medio_orcamento?: number;
  ultimo_orcamento?: string;
}
