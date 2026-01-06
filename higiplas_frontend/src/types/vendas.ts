// /src/types/vendas.ts

export interface Dashboard {
    total_vendido_hoje: number;
    quantidade_pedidos_hoje: number;
    clientes_visitados_hoje: number;
    meta_dia: number;
    progresso_meta: number;
  }
  
  export interface Cliente {
    id: number;
    nome: string;
    telefone: string;
    bairro: string | null;
    cidade: string | null;
    ultima_compra: string | null;
  }
  
  export interface EstatisticasPreco {
    preco_maior: number | null;
    preco_medio: number | null;
    preco_menor: number | null;
    total_vendas: number;
  }

  export interface PrecoClienteRange {
    minimo: number | null;
    maximo: number | null;
    medio: number | null;
    ultimo: number | null;
    total_vendas: number;
  }

  export interface Produto {
    id: number;
    nome: string;
    codigo: string;
    preco: number;
    estoque_disponivel: number;
    categoria: string;
    unidade_medida: string;
    estatisticas_preco?: EstatisticasPreco | null;
    preco_cliente?: PrecoClienteRange | null;
  }
  
  export interface ItemCarrinho {
    id: number;
    nome: string;
    preco: number;
    quantidade: number;
    estoque_disponivel: number;
  }
  
  export interface ItemVenda {
    produto_id: number;
    quantidade: number;
  }
  
  export interface VendaCreate {
    cliente_id: number;
    itens: ItemVenda[];
    observacao?: string;
  }
  
  export interface VendaResponse {
    sucesso: boolean;
    mensagem: string;
    venda_id: string;
    cliente_nome: string;
    total_venda: number;
    itens_processados: number;
    detalhes: string;
  }