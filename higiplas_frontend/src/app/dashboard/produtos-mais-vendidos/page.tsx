'use client';

import { useState, useEffect } from 'react';
import { ArrowTrendingUpIcon, CurrencyDollarIcon, ShoppingBagIcon, ChartBarIcon } from '@heroicons/react/24/outline';

interface ProdutoMaisVendido {
  produto: string;
  total_quantidade: number;
  total_valor: number;
  numero_vendas: number;
}

export default function ProdutosMaisVendidos() {
  const [produtos, setProdutos] = useState<ProdutoMaisVendido[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ano, setAno] = useState<number | null>(null);
  const [limit, setLimit] = useState(50);

  const fetchProdutosMaisVendidos = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      
      if (!token) {
        throw new Error('Token não encontrado');
      }

      const params = new URLSearchParams();
      if (ano) params.append('ano', ano.toString());
      params.append('limit', limit.toString());

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/ai-pdf/top-selling-products?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error('Erro ao buscar produtos mais vendidos');
      }

      const data = await response.json();
      // A API retorna um objeto com a propriedade 'products'
      setProdutos(data.products || data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProdutosMaisVendidos();
  }, [ano, limit, fetchProdutosMaisVendidos]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('pt-BR').format(value);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">Erro ao carregar dados</div>
          <div className="text-gray-600">{error}</div>
          <button
            onClick={fetchProdutosMaisVendidos}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Produtos Mais Vendidos
        </h1>
        <p className="text-gray-600">
          Visualize os produtos com melhor performance de vendas no último ano
        </p>
      </div>

      {/* Filtros */}
      <div className="mb-6 flex flex-wrap gap-4">
        <div>
          <label htmlFor="ano" className="block text-sm font-medium text-gray-700 mb-1">
            Ano (deixe vazio para últimos 365 dias)
          </label>
          <input
            type="number"
            id="ano"
            value={ano || ''}
            onChange={(e) => setAno(e.target.value ? parseInt(e.target.value) : null)}
            placeholder="Ex: 2024"
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-1">
            Limite de produtos
          </label>
          <select
            id="limit"
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={10}>10 produtos</option>
            <option value={25}>25 produtos</option>
            <option value={50}>50 produtos</option>
            <option value={100}>100 produtos</option>
          </select>
        </div>
      </div>

      {/* Resumo */}
      {produtos.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow border">
            <div className="flex items-center">
              <ShoppingBagIcon className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total de Produtos</p>
                <p className="text-2xl font-semibold text-gray-900">{produtos.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow border">
            <div className="flex items-center">
              <ChartBarIcon className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Qtd. Total Vendida</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {formatNumber(produtos.reduce((sum, p) => sum + p.total_vendido, 0))}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow border">
            <div className="flex items-center">
              <CurrencyDollarIcon className="h-8 w-8 text-yellow-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Valor Total</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {formatCurrency(produtos.reduce((sum, p) => sum + p.valor_total_vendas, 0))}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow border">
            <div className="flex items-center">
              <ArrowTrendingUpIcon className="h-8 w-8 text-purple-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Orçamentos</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {formatNumber(produtos.reduce((sum, p) => sum + p.numero_orcamentos, 0))}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabela de produtos */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Ranking de Produtos
          </h3>
          
          {produtos.length === 0 ? (
            <div className="text-center py-8">
              <ArrowTrendingUpIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhum produto encontrado</h3>
              <p className="mt-1 text-sm text-gray-500">
                Não há dados de vendas para o período selecionado.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Posição
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Produto
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Código
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Preço Unitário
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
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {produtos.map((produto, index) => (
                    <tr key={`${produto.produto}-${index}`} className={index < 3 ? 'bg-yellow-50' : ''}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className={`inline-flex items-center justify-center h-8 w-8 rounded-full text-sm font-medium ${
                            index === 0 ? 'bg-yellow-500 text-white' :
                            index === 1 ? 'bg-gray-400 text-white' :
                            index === 2 ? 'bg-orange-600 text-white' :
                            'bg-gray-200 text-gray-700'
                          }`}>
                            {index + 1}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{produto.produto}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">-</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(produto.total_valor / produto.total_quantidade)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{formatNumber(produto.total_quantidade)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-green-600">{formatCurrency(produto.total_valor)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{produto.numero_vendas}</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}