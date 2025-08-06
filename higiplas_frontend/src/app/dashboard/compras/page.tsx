"use client";

import { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { Product } from '@/types';
import { apiService } from '@/services/apiService';
import { Header } from '@/components/dashboard/Header';
// Importe os tipos que acabamos de exportar
import { CustomTable, Column } from '@/components/dashboard/CustomTable';
import Button from '@/components/Button';

// Supondo que você crie tipos para OrdemDeCompra também
interface OrdemDeCompra {
  id: number;
  status: string;
  data_criacao: string;
  fornecedor: { nome: string };
  itens: any[]; // Simplificado por brevidade
}

export default function ComprasPage() {
  const [activeTab, setActiveTab] = useState<'baixoEstoque' | 'historico'>('baixoEstoque');
  const [lowStockProducts, setLowStockProducts] = useState<Product[]>([]);
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
        setLowStockProducts(lowStockData);
        setOrders(ordersData);
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

  // APLIQUE O TIPO EXPLÍCITO AQUI
  const lowStockColumns: Column<Product>[] = useMemo(() => [
    { header: '', accessor: 'actions', render: (p: Product) => <input type="checkbox" checked={selectedProducts.has(p.id)} onChange={() => handleSelectProduct(p.id)} /> },
    { header: 'Produto', accessor: 'nome' },
    { header: 'Código', accessor: 'codigo' },
    { header: 'Estoque Atual', accessor: 'quantidade_em_estoque' },
    { header: 'Estoque Mínimo', accessor: 'estoque_minimo' },
  ], [selectedProducts]);

  // E APLIQUE O TIPO EXPLÍCITO AQUI TAMBÉM
  const orderColumns: Column<OrdemDeCompra>[] = useMemo(() => [
    { header: 'ID', accessor: 'id' },
    { header: 'Fornecedor', accessor: 'fornecedor', render: (o: OrdemDeCompra) => o.fornecedor.nome },
    { header: 'Status', accessor: 'status' },
    { header: 'Data Criação', accessor: 'data_criacao', render: (o: OrdemDeCompra) => new Date(o.data_criacao).toLocaleDateString('pt-BR') },
    // Adicionar botão de detalhes no futuro
  ], []);

  return (
    <>
      <Header>
        <h1 className="text-xl font-bold">Gestão de Compras</h1>
      </Header>
      <main className="flex-1 p-6 overflow-y-auto">
        <div className="max-w-7xl mx-auto space-y-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              <button onClick={() => setActiveTab('baixoEstoque')} className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'baixoEstoque' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
                Ponto de Pedido
              </button>
              <button onClick={() => setActiveTab('historico')} className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'historico' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
                Histórico de Ordens
              </button>
            </nav>
          </div>

          {loading ? <p>Carregando...</p> : (
            <div>
              {activeTab === 'baixoEstoque' && (
                <div>
                  <div className="flex justify-end mb-4">
                    <Button onClick={handleCreateOrder} disabled={selectedProducts.size === 0}>
                      Criar Ordem de Compra ({selectedProducts.size})
                    </Button>
                  </div>
                  <CustomTable columns={lowStockColumns} data={lowStockProducts} />
                </div>
              )}
              {activeTab === 'historico' && (
                <CustomTable columns={orderColumns} data={orders} />
              )}
            </div>
          )}
        </div>
      </main>
    </>
  );
}