"use client";

import { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { OrdemDeCompra, PurchaseSuggestion, PurchaseSuggestionResponse } from '@/types';
import { apiService } from '@/services/apiService';
import { Header } from '@/components/dashboard/Header';
import { CustomTable, Column } from '@/components/dashboard/CustomTable';
import { PurchaseSuggestionCard } from '@/components/compras/PurchaseSuggestionCard';
import Button from '@/components/Button';

export default function ComprasPage() {
  const [activeTab, setActiveTab] = useState<'sugestoes' | 'historico'>('sugestoes');
  const [suggestions, setSuggestions] = useState<PurchaseSuggestion[]>([]);
  const [suggestionsData, setSuggestionsData] = useState<PurchaseSuggestionResponse | null>(null);
  const [orders, setOrders] = useState<OrdemDeCompra[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProducts, setSelectedProducts] = useState<Set<number>>(new Set());
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [suggestionsResponse, ordersData] = await Promise.all([
          apiService.get('/compras/sugestoes'),
          apiService.get('/ordens-compra/'),
        ]);
        
        const suggestionsData: PurchaseSuggestionResponse = suggestionsResponse?.data || {
          total_sugestoes: 0,
          sugestoes_criticas: 0,
          sugestoes_baixas: 0,
          sugestoes: [],
          data_analise: new Date().toISOString()
        };
        
        setSuggestionsData(suggestionsData);
        setSuggestions(suggestionsData.sugestoes || []);
        setOrders(ordersData?.data || []);
      } catch (error) {
        console.error("Erro ao buscar dados de compras:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSelectProduct = (productId: number) => {
    setSelectedProducts(prev => {
      const newSelection = new Set(prev);
      if (newSelection.has(productId)) {
        newSelection.delete(productId);
      } else {
        newSelection.add(productId);
      }
      return newSelection;
    });
  };

  const handleCreateOrder = () => {
    if (selectedProducts.size === 0) {
      alert("Selecione ao menos um produto para criar a ordem de compra.");
      return;
    }
    const ids = Array.from(selectedProducts).join(',');
    router.push(`/dashboard/compras/nova-oc?productIds=${ids}`);
  };
  
  const orderColumns: Column<OrdemDeCompra>[] = useMemo(() => [
    { header: 'ID da OC', accessor: 'id', render: (o) => <span className="font-mono text-xs text-gray-500">#{o.id}</span> },
    { header: 'Fornecedor', accessor: 'fornecedor', render: (o: OrdemDeCompra) => o.fornecedor?.nome || 'N/A' },
    { header: 'Status', accessor: 'status', render: (o) => (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
        o.status === 'RECEBIDA' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
        o.status === 'RASCUNHO' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
        'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
      }`}>
        {o.status}
      </span>
    )},
    { header: 'Data Criação', accessor: 'data_criacao', render: (o: OrdemDeCompra) => o.data_criacao ? new Date(o.data_criacao).toLocaleDateString('pt-BR') : 'N/A' },
    { header: 'Itens', accessor: 'itens', render: (o) => <span>{o.itens?.length || 0}</span> }
  ], []);

  return (
    <>
      <Header>
        <h1 className="text-xl font-bold">Gestão de Compras</h1>
      </Header>
      <main className="flex-1 p-4 md:p-6 overflow-y-auto">
        <div className="max-w-7xl mx-auto space-y-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              <button 
                onClick={() => setActiveTab('sugestoes')} 
                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'sugestoes' 
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                Sugestões de Compra ({suggestionsData?.total_sugestoes || 0})
                {suggestionsData && suggestionsData.sugestoes_criticas > 0 && (
                  <span className="ml-2 bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 text-xs font-semibold px-2 py-0.5 rounded-full">
                    {suggestionsData.sugestoes_criticas} críticos
                  </span>
                )}
              </button>
              <button 
                onClick={() => setActiveTab('historico')} 
                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'historico' 
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                Histórico de Ordens ({orders.length})
              </button>
            </nav>
          </div>

          {loading ? (
            <div className="text-center p-8">Carregando dados...</div>
          ) : (
            <div className="bg-white dark:bg-gray-800 p-4 md:p-6 rounded-lg shadow-md border dark:border-gray-700">
              {activeTab === 'sugestoes' && (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <div>
                      <h3 className="text-lg font-semibold mb-2">Sugestões de Compra Baseadas em Demanda Real</h3>
                      {suggestions.length > 0 && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Análise baseada em {suggestions[0]?.periodo_analise_dias || 90} dias de histórico de vendas
                        </p>
                      )}
                    </div>
                    {selectedProducts.size > 0 && (
                      <Button onClick={handleCreateOrder}>
                        Criar Ordem de Compra ({selectedProducts.size})
                      </Button>
                    )}
                  </div>

                  {suggestions.length === 0 ? (
                    <div className="text-center p-8 text-gray-500 dark:text-gray-400">
                      <p className="text-lg mb-2">Nenhuma sugestão de compra no momento</p>
                      <p className="text-sm">
                        Produtos com estoque adequado ou sem histórico suficiente de vendas não aparecem aqui.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {suggestions.map((suggestion) => (
                        <PurchaseSuggestionCard
                          key={suggestion.produto_id}
                          suggestion={suggestion}
                          onSelect={handleSelectProduct}
                          isSelected={selectedProducts.has(suggestion.produto_id)}
                        />
                      ))}
                    </div>
                  )}
                </div>
              )}
              {activeTab === 'historico' && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">Histórico de Ordens de Compra</h3>
                  <CustomTable columns={orderColumns} data={orders} />
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </>
  );
}