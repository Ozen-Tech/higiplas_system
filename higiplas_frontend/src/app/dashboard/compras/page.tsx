"use client";

import { useState, useEffect, useMemo, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { OrdemDeCompra, PurchaseSuggestion, PurchaseSuggestionResponse } from '@/types';
import { apiService } from '@/services/apiService';
import { Header } from '@/components/dashboard/Header';
import { CustomTable, Column } from '@/components/dashboard/CustomTable';
import { PurchaseSuggestionCard } from '@/components/compras/PurchaseSuggestionCard';
import Button from '@/components/Button';
import { Eye, Download, Edit, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

export default function ComprasPage() {
  const [activeTab, setActiveTab] = useState<'sugestoes' | 'historico'>('sugestoes');
  const [suggestions, setSuggestions] = useState<PurchaseSuggestion[]>([]);
  const [suggestionsData, setSuggestionsData] = useState<PurchaseSuggestionResponse | null>(null);
  const [orders, setOrders] = useState<OrdemDeCompra[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProducts, setSelectedProducts] = useState<Set<number>>(new Set());
  const [selectedOrder, setSelectedOrder] = useState<OrdemDeCompra | null>(null);
  const [downloadingId, setDownloadingId] = useState<number | null>(null);
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

  const fetchOrders = useCallback(async () => {
    try {
      const ordersData = await apiService.get('/ordens-compra/');
      setOrders(ordersData?.data || []);
    } catch (error) {
      console.error("Erro ao buscar ordens de compra:", error);
    }
  }, []);

  const handleViewOrder = useCallback(async (ordemId: number) => {
    try {
      const response = await apiService.get(`/ordens-compra/${ordemId}`);
      if (response?.data) {
        setSelectedOrder(response.data);
      }
    } catch (error) {
      toast.error('Erro ao carregar ordem de compra');
      console.error(error);
    }
  }, []);

  const handleEditOrder = useCallback((ordemId: number) => {
    router.push(`/dashboard/compras/editar-oc/${ordemId}`);
  }, [router]);

  const handleDeleteOrder = useCallback(async (ordemId: number) => {
    if (!confirm('Tem certeza que deseja deletar esta ordem de compra?')) {
      return;
    }

    try {
      await apiService.delete(`/ordens-compra/${ordemId}`);
      toast.success('Ordem de compra deletada com sucesso');
      // Recarregar lista
      await fetchOrders();
    } catch (error) {
      toast.error('Erro ao deletar ordem de compra');
      console.error(error);
    }
  }, [fetchOrders]);

  const handleDownloadPDF = useCallback(async (ordemId: number) => {
    setDownloadingId(ordemId);
    toast.loading('Gerando PDF...');
    try {
      const response = await apiService.getBlob(`/ordens-compra/${ordemId}/pdf/`);
      const blob = await response.blob();

      const contentDisposition = response.headers.get('content-disposition');
      let filename = `ordem_compra_${ordemId}.pdf`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch && filenameMatch.length > 1) {
          filename = filenameMatch[1];
        }
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();

      toast.dismiss();
      toast.success('PDF baixado com sucesso!');

      setTimeout(() => {
        window.URL.revokeObjectURL(url);
        link.remove();
      }, 100);
    } catch (error) {
      toast.dismiss();
      toast.error('Erro ao gerar PDF');
      console.error('Erro no download:', error);
    } finally {
      setDownloadingId(null);
    }
  }, []);
  
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
    { header: 'Itens', accessor: 'itens', render: (o) => <span>{o.itens?.length || 0}</span> },
    { 
      header: 'Ações', 
      accessor: 'id', 
      render: (o: OrdemDeCompra) => (
        <div className="flex gap-2">
          <button
            onClick={() => handleViewOrder(o.id)}
            className="p-1 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
            title="Ver detalhes"
          >
            <Eye className="h-4 w-4" />
          </button>
          <button
            onClick={() => handleDownloadPDF(o.id)}
            disabled={downloadingId === o.id}
            className="p-1 text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300 disabled:opacity-50"
            title="Baixar PDF"
          >
            <Download className="h-4 w-4" />
          </button>
          {o.status !== 'RECEBIDA' && (
            <>
              <button
                onClick={() => handleEditOrder(o.id)}
                className="p-1 text-yellow-600 hover:text-yellow-800 dark:text-yellow-400 dark:hover:text-yellow-300"
                title="Editar"
              >
                <Edit className="h-4 w-4" />
              </button>
              <button
                onClick={() => handleDeleteOrder(o.id)}
                className="p-1 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                title="Deletar"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </>
          )}
        </div>
      )
    }
  ], [downloadingId, handleViewOrder, handleDownloadPDF, handleEditOrder, handleDeleteOrder]);

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
                  {orders.length === 0 ? (
                    <div className="text-center p-8 text-gray-500 dark:text-gray-400">
                      <p>Nenhuma ordem de compra encontrada</p>
                    </div>
                  ) : (
                    <CustomTable columns={orderColumns} data={orders} />
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </main>
      
      {/* Modal de Visualização */}
      {selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Ordem de Compra #{selectedOrder.id}</h2>
                <button
                  onClick={() => setSelectedOrder(null)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Fornecedor</p>
                    <p className="font-semibold">{selectedOrder.fornecedor?.nome || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      selectedOrder.status === 'RECEBIDA' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                      selectedOrder.status === 'RASCUNHO' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                    }`}>
                      {selectedOrder.status}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Data de Criação</p>
                    <p className="font-semibold">
                      {selectedOrder.data_criacao ? new Date(selectedOrder.data_criacao).toLocaleDateString('pt-BR') : 'N/A'}
                    </p>
                  </div>
                  {selectedOrder.data_recebimento && (
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Data de Recebimento</p>
                      <p className="font-semibold">
                        {new Date(selectedOrder.data_recebimento).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  )}
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-2">Itens</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                      <thead className="bg-gray-50 dark:bg-gray-700">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Produto</th>
                          <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Quantidade</th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Custo Unit.</th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Subtotal</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                        {selectedOrder.itens?.map((item, idx) => {
                          const subtotal = item.quantidade_solicitada * item.custo_unitario_registrado;
                          return (
                            <tr key={idx}>
                              <td className="px-4 py-2 text-sm">{item.produto?.nome || 'N/A'}</td>
                              <td className="px-4 py-2 text-sm text-center">{item.quantidade_solicitada}</td>
                              <td className="px-4 py-2 text-sm text-right">R$ {item.custo_unitario_registrado.toFixed(2)}</td>
                              <td className="px-4 py-2 text-sm text-right font-semibold">R$ {subtotal.toFixed(2)}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                      <tfoot className="bg-gray-50 dark:bg-gray-700">
                        <tr>
                          <td colSpan={3} className="px-4 py-2 text-right font-bold">Total:</td>
                          <td className="px-4 py-2 text-right font-bold">
                            R$ {selectedOrder.itens?.reduce((acc, item) => 
                              acc + (item.quantidade_solicitada * item.custo_unitario_registrado), 0
                            ).toFixed(2) || '0.00'}
                          </td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>
                
                <div className="flex gap-2 justify-end">
                  <button
                    onClick={() => handleDownloadPDF(selectedOrder.id)}
                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    <Download className="h-4 w-4 inline mr-2" />
                    Baixar PDF
                  </button>
                  {selectedOrder.status !== 'RECEBIDA' && (
                    <>
                      <button
                        onClick={() => {
                          setSelectedOrder(null);
                          handleEditOrder(selectedOrder.id);
                        }}
                        className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
                      >
                        <Edit className="h-4 w-4 inline mr-2" />
                        Editar
                      </button>
                      <button
                        onClick={() => {
                          setSelectedOrder(null);
                          handleDeleteOrder(selectedOrder.id);
                        }}
                        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        <Trash2 className="h-4 w-4 inline mr-2" />
                        Deletar
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}