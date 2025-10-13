'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  ArrowTrendingUpIcon,
  CurrencyDollarIcon,
  ShoppingBagIcon,
  ChartBarIcon,
  CalendarIcon,
  UserGroupIcon,
  ExclamationTriangleIcon,
  FunnelIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
/*
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';
*/

// Interfaces atualizadas
interface ProdutoMaisVendido {
  produto_id: number;
  nome: string;
  codigo: string;
  categoria: string;
  preco_atual: number;
  estoque_atual: number;
  total_quantidade_vendida: number;
  valor_total_vendido: number;
  numero_vendas: number;
  quantidade_media_por_venda: number;
  frequencia_vendas_por_dia: number;
  primeira_venda: string;
  ultima_venda: string;
  dias_desde_ultima_venda: number;
  ticket_medio: number;
  rotatividade_estoque: number;
  status_estoque: string;
}

interface EstatisticasGerais {
  total_produtos_analisados: number;
  periodo_analise_dias: number;
  data_inicio: string;
  data_fim: string;
  total_quantidade_vendida: number;
  total_valor_vendido: number;
  ticket_medio: number;
  produto_mais_vendido: string | null;
  categoria_mais_vendida: string | null;
}

interface FiltrosAplicados {
  periodo_dias?: number;
  data_inicio?: string;
  data_fim?: string;
  limite?: number;
  ordenar_por?: string;
  vendedor_id?: number | null;
  categoria?: string;
  produto_id?: number;
}

interface ApiResponse {
  produtos: ProdutoMaisVendido[];
  estatisticas: EstatisticasGerais;
  filtros_aplicados: FiltrosAplicados;
}

interface TendenciaMensal {
  mes_ano: string;
  produto_nome: string;
  quantidade_vendida: number;
  valor_vendido: number;
}

interface ComparativoVendedor {
  vendedor_id: number;
  vendedor_nome: string;
  total_quantidade_vendida: number;
  total_valor_vendido: number;
  produtos_diferentes_vendidos: number;
  numero_vendas: number;
  ticket_medio: number;
}

export default function ProdutosMaisVendidos() {
  // Estados principais
  const [dados, setDados] = useState<ApiResponse | null>(null);
  const [tendencias, setTendencias] = useState<TendenciaMensal[]>([]);
  const [comparativoVendedores, setComparativoVendedores] = useState<ComparativoVendedor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Estados de filtros
  const [filtros, setFiltros] = useState({
    periodo_dias: 365,
    data_inicio: '',
    data_fim: '',
    limite: 50,
    ordenar_por: 'quantidade',
    vendedor_id: null as number | null
  });
  
  // Estados de visualização
  const [abaSelecionada, setAbaSelecionada] = useState<'produtos' | 'tendencias' | 'vendedores'>('produtos');
  const [mostrarFiltros, setMostrarFiltros] = useState(false);

  const fetchDados = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      
      if (!token) {
        throw new Error('Token não encontrado');
      }

      // Construir parâmetros da query
      const params = new URLSearchParams();
      if (filtros.periodo_dias) params.append('periodo_dias', filtros.periodo_dias.toString());
      if (filtros.data_inicio) params.append('data_inicio', filtros.data_inicio);
      if (filtros.data_fim) params.append('data_fim', filtros.data_fim);
      if (filtros.limite) params.append('limite', filtros.limite.toString());
      if (filtros.ordenar_por) params.append('ordenar_por', filtros.ordenar_por);
      if (filtros.vendedor_id) params.append('vendedor_id', filtros.vendedor_id.toString());

      // Buscar produtos mais vendidos
      const responseProdutos = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/produtos-mais-vendidos/?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!responseProdutos.ok) {
        throw new Error('Erro ao buscar produtos mais vendidos');
      }

      const dadosProdutos = await responseProdutos.json();
      setDados(dadosProdutos);

      // Buscar tendências
      const responseTendencias = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/produtos-mais-vendidos/tendencias?periodo_meses=6`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (responseTendencias.ok) {
        const dadosTendencias = await responseTendencias.json();
        setTendencias(dadosTendencias.tendencias || []);
      }

      // Buscar comparativo de vendedores
      const responseVendedores = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/produtos-mais-vendidos/comparativo-vendedores?periodo_dias=30`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (responseVendedores.ok) {
        const dadosVendedores = await responseVendedores.json();
        setComparativoVendedores(dadosVendedores || []);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }, [filtros]);

  useEffect(() => {
    fetchDados();
  }, [fetchDados]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('pt-BR').format(value);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ALTA_ROTACAO': return 'bg-green-100 text-green-800 border-green-200';
      case 'MEDIA_ROTACAO': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'BAIXA_ROTACAO': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'PARADO': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'ALTA_ROTACAO': return 'Alta Rotação';
      case 'MEDIA_ROTACAO': return 'Média Rotação';
      case 'BAIXA_ROTACAO': return 'Baixa Rotação';
      case 'PARADO': return 'Parado';
      default: return 'Indefinido';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando dados de vendas...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center bg-white p-8 rounded-lg shadow-lg max-w-md">
          <ExclamationTriangleIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Erro ao carregar dados</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchDados}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  if (!dados) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <ArrowTrendingUpIcon className="h-8 w-8 text-blue-600 mr-3" />
                Produtos Mais Vendidos
              </h1>
              <p className="mt-2 text-gray-600">
                Análise baseada em {formatNumber(dados.estatisticas.total_produtos_analisados)} produtos 
                nos últimos {dados.estatisticas.periodo_analise_dias} dias
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setMostrarFiltros(!mostrarFiltros)}
                className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <FunnelIcon className="h-4 w-4 mr-2" />
                Filtros
              </button>
              <button
                onClick={fetchDados}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <ArrowPathIcon className="h-4 w-4 mr-2" />
                Atualizar
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filtros Expandidos */}
        {mostrarFiltros && (
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Filtros de Análise</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Período (dias)
                </label>
                <select
                  value={filtros.periodo_dias}
                  onChange={(e) => setFiltros({...filtros, periodo_dias: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={30}>30 dias</option>
                  <option value={90}>90 dias</option>
                  <option value={180}>6 meses</option>
                  <option value={365}>1 ano</option>
                  <option value={730}>2 anos</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ordenar por
                </label>
                <select
                  value={filtros.ordenar_por}
                  onChange={(e) => setFiltros({...filtros, ordenar_por: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="quantidade">Quantidade</option>
                  <option value="valor">Valor Total</option>
                  <option value="frequencia">Frequência</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Limite
                </label>
                <select
                  value={filtros.limite}
                  onChange={(e) => setFiltros({...filtros, limite: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={10}>10 produtos</option>
                  <option value={25}>25 produtos</option>
                  <option value={50}>50 produtos</option>
                  <option value={100}>100 produtos</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data Início
                </label>
                <input
                  type="date"
                  value={filtros.data_inicio}
                  onChange={(e) => setFiltros({...filtros, data_inicio: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data Fim
                </label>
                <input
                  type="date"
                  value={filtros.data_fim}
                  onChange={(e) => setFiltros({...filtros, data_fim: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        )}

        {/* Cards de Métricas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <ShoppingBagIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Vendido</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(dados.estatisticas.total_quantidade_vendida)}
                </p>
                <p className="text-xs text-gray-500">unidades</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <CurrencyDollarIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Valor Total</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(dados.estatisticas.total_valor_vendido)}
                </p>
                <p className="text-xs text-gray-500">em vendas</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <ChartBarIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Ticket Médio</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(dados.estatisticas.ticket_medio)}
                </p>
                <p className="text-xs text-gray-500">por venda</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="p-3 bg-orange-100 rounded-lg">
                <ArrowTrendingUpIcon className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Produtos Ativos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dados.estatisticas.total_produtos_analisados}
                </p>
                <p className="text-xs text-gray-500">com vendas</p>
              </div>
            </div>
          </div>
        </div>

        {/* Abas de Navegação */}
        <div className="bg-white rounded-lg shadow-sm border mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              <button
                onClick={() => setAbaSelecionada('produtos')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  abaSelecionada === 'produtos'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Ranking de Produtos
              </button>
              <button
                onClick={() => setAbaSelecionada('tendencias')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  abaSelecionada === 'tendencias'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Tendências
              </button>
              <button
                onClick={() => setAbaSelecionada('vendedores')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  abaSelecionada === 'vendedores'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Performance Vendedores
              </button>
            </nav>
          </div>

          <div className="p-6">
            {/* Aba Produtos */}
            {abaSelecionada === 'produtos' && (
              <div>
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Top {dados.produtos.length} Produtos Mais Vendidos
                  </h3>
                  <p className="text-gray-600">
                    Ordenado por {filtros.ordenar_por === 'quantidade' ? 'quantidade vendida' : 
                                 filtros.ordenar_por === 'valor' ? 'valor total' : 'frequência de vendas'}
                  </p>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          #
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Produto
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Categoria
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Qtd. Vendida
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Valor Total
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Nº Vendas
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Ticket Médio
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Estoque
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {dados.produtos.map((produto, index) => (
                        <tr key={produto.produto_id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                                index < 3 ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-600'
                              }`}>
                                {index + 1}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{produto.nome}</div>
                              <div className="text-sm text-gray-500">{produto.codigo}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {produto.categoria}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatNumber(produto.total_quantidade_vendida)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {formatCurrency(produto.valor_total_vendido)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {produto.numero_vendas}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatCurrency(produto.ticket_medio)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(produto.status_estoque)}`}>
                              {getStatusText(produto.status_estoque)}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{produto.estoque_atual}</div>
                            <div className="text-xs text-gray-500">
                              {produto.dias_desde_ultima_venda} dias
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Aba Tendências */}
            {abaSelecionada === 'tendencias' && (
              <div>
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Tendências de Vendas (Últimos 6 Meses)
                  </h3>
                  <p className="text-gray-600">
                    Evolução das vendas por mês para análise de sazonalidade
                  </p>
                </div>

                {tendencias.length > 0 ? (
                  <div className="h-96">
                    {/* GRÁFICO TEMPORARIAMENTE COMENTADO - RECHARTS NÃO INSTALADO */}
                    <div className="text-center py-12">
                      <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500">Gráfico de tendências indisponível (Recharts necessário)</p>
                    </div>
                    {/*
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={tendencias}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="mes_ano" />
                        <YAxis />
                        <Tooltip
                          formatter={(value, name) => [
                            name === 'quantidade_vendida' ? formatNumber(value as number) : formatCurrency(value as number),
                            name === 'quantidade_vendida' ? 'Quantidade' : 'Valor'
                          ]}
                        />
                        <Line
                          type="monotone"
                          dataKey="quantidade_vendida"
                          stroke="#3B82F6"
                          strokeWidth={2}
                          name="quantidade_vendida"
                        />
                        <Line
                          type="monotone"
                          dataKey="valor_vendido"
                          stroke="#10B981"
                          strokeWidth={2}
                          name="valor_vendido"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                    */}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">Nenhum dado de tendência disponível</p>
                  </div>
                )}
              </div>
            )}

            {/* Aba Vendedores */}
            {abaSelecionada === 'vendedores' && (
              <div>
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Performance dos Vendedores (Últimos 30 Dias)
                  </h3>
                  <p className="text-gray-600">
                    Comparativo de vendas entre vendedores
                  </p>
                </div>

                {comparativoVendedores.length > 0 ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Tabela de Vendedores */}
                    <div>
                      <h4 className="text-md font-medium text-gray-900 mb-4">Ranking de Vendedores</h4>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Vendedor
                              </th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Valor Total
                              </th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Vendas
                              </th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Ticket Médio
                              </th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {comparativoVendedores.map((vendedor, index) => (
                              <tr key={vendedor.vendedor_id}>
                                <td className="px-4 py-4">
                                  <div className="flex items-center">
                                    <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-medium mr-3 ${
                                      index < 3 ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-600'
                                    }`}>
                                      {index + 1}
                                    </span>
                                    <span className="text-sm font-medium text-gray-900">
                                      {vendedor.vendedor_nome}
                                    </span>
                                  </div>
                                </td>
                                <td className="px-4 py-4 text-sm font-medium text-gray-900">
                                  {formatCurrency(vendedor.total_valor_vendido)}
                                </td>
                                <td className="px-4 py-4 text-sm text-gray-900">
                                  {vendedor.numero_vendas}
                                </td>
                                <td className="px-4 py-4 text-sm text-gray-900">
                                  {formatCurrency(vendedor.ticket_medio)}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Gráfico de Vendedores */}
                    <div>
                      <h4 className="text-md font-medium text-gray-900 mb-4">Distribuição de Vendas</h4>
                      <div className="h-64">
                        {/* GRÁFICO TEMPORARIAMENTE COMENTADO - RECHARTS NÃO INSTALADO */}
                        <div className="text-center py-12">
                          <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                          <p className="text-gray-500">Gráfico de vendedores indisponível (Recharts necessário)</p>
                        </div>
                        {/*
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={comparativoVendedores.slice(0, 8)}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis
                              dataKey="vendedor_nome"
                              angle={-45}
                              textAnchor="end"
                              height={80}
                            />
                            <YAxis />
                            <Tooltip formatter={(value) => formatCurrency(value as number)} />
                            <Bar dataKey="total_valor_vendido" fill="#3B82F6" />
                          </BarChart>
                        </ResponsiveContainer>
                        */}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <UserGroupIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">Nenhum dado de vendedor disponível</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Informações Adicionais */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Informações do Período</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-center">
              <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
              <div>
                <p className="text-sm text-gray-500">Período Analisado</p>
                <p className="text-sm font-medium text-gray-900">
                  {new Date(dados.estatisticas.data_inicio).toLocaleDateString('pt-BR')} até{' '}
                  {new Date(dados.estatisticas.data_fim).toLocaleDateString('pt-BR')}
                </p>
              </div>
            </div>
            
            <div className="flex items-center">
              <ArrowTrendingUpIcon className="h-5 w-5 text-gray-400 mr-2" />
              <div>
                <p className="text-sm text-gray-500">Produto Mais Vendido</p>
                <p className="text-sm font-medium text-gray-900">
                  {dados.estatisticas.produto_mais_vendido || 'N/A'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center">
              <ShoppingBagIcon className="h-5 w-5 text-gray-400 mr-2" />
              <div>
                <p className="text-sm text-gray-500">Categoria Mais Vendida</p>
                <p className="text-sm font-medium text-gray-900">
                  {dados.estatisticas.categoria_mais_vendida || 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}