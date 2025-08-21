"use client";

import { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
// Importe os novos tipos de OrdemDeCompra junto com o Product
import { Product, OrdemDeCompra } from '@/types';
import { apiService } from '@/services/apiService';
import { Header } from '@/components/dashboard/Header';
import { CustomTable, Column } from '@/components/dashboard/CustomTable';
import Button from '@/components/Button';

export default function ComprasPage() {
  const [activeTab, setActiveTab] = useState<'baixoEstoque' | 'historico'>('baixoEstoque');
  const [lowStockProducts, setLowStockProducts] = useState<Product[]>([]);
  // Use o novo tipo importado para o estado das ordens de compra
  const [orders, setOrders] = useState<OrdemDeCompra[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProducts, setSelectedProducts] = useState<Set<number>>(new Set());
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [lowStockData, ordersData] = await Promise.all([
          apiService.get('/produtos/baixo-estoque/'),
          apiService.get('/ordens-compra/'),
        ]);
        setLowStockProducts(lowStockData?.data || []);
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

  const lowStockColumns: Column<Product>[] = useMemo(() => [
    { header: '', accessor: 'actions', render: (p: Product) => <input type="checkbox" checked={selectedProducts.has(p.id)} onChange={() => handleSelectProduct(p.id)} className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" /> },
    { header: 'Produto', accessor: 'nome', render: (p) => <span className="font-medium text-gray-900 dark:text-gray-100">{p.nome}</span> },
    { header: 'Código', accessor: 'codigo' },
    { header: 'Estoque Atual', accessor: 'quantidade_em_estoque', render: (p) => <span className="font-bold text-red-600 dark:text-red-400">{p.quantidade_em_estoque}</span> },
    { header: 'Estoque Mínimo', accessor: 'estoque_minimo' },
  ], [selectedProducts]);
  
  const orderColumns: Column<OrdemDeCompra>[] = useMemo(() => [
    { header: 'ID da OC', accessor: 'id', render: (o) => <span className="font-mono text-xs text-gray-500">#{o.id}</span> },
    { header: 'Fornecedor', accessor: 'fornecedor', render: (o: OrdemDeCompra) => o.fornecedor.nome },
    { header: 'Status', accessor: 'status', render: (o) => (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
        o.status === 'RECEBIDA' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
        o.status === 'RASCUNHO' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
        'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
      }`}>
        {o.status}
      </span>
    )},
    { header: 'Data Criação', accessor: 'data_criacao', render: (o: OrdemDeCompra) => new Date(o.data_criacao).toLocaleDateString('pt-BR') },
    { header: 'Itens', accessor: 'itens', render: (o) => <span>{o.itens.length}</span> }
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
              <button onClick={() => setActiveTab('baixoEstoque')} className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'baixoEstoque' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
                Ponto de Pedido ({lowStockProducts.length})
              </button>
              <button onClick={() => setActiveTab('historico')} className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'historico' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
                Histórico de Ordens
              </button>
            </nav>
          </div>

          {loading ? <div className="text-center p-8">Carregando dados...</div> : (
            <div className="bg-white dark:bg-gray-800 p-4 md:p-6 rounded-lg shadow-md border dark:border-gray-700">
              {activeTab === 'baixoEstoque' && (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold">Produtos Precisando de Reposição</h3>
                    <Button onClick={handleCreateOrder} disabled={selectedProducts.size === 0}>
                      Criar Ordem de Compra ({selectedProducts.size})
                    </Button>
                  </div>
                  <CustomTable columns={lowStockColumns} data={lowStockProducts} />
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