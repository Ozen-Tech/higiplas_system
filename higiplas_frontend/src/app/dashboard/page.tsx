// /src/app/dashboard/page.tsx
"use client";

import { useEffect, useState, useMemo } from "react";
import { useProducts } from "@/hooks/useProducts";
import { ProductTable } from "@/components/dashboard/ProductTable";
import { Header } from "@/components/dashboard/Header";
import { ThemeToggleButton } from "@/components/ThemeToggleButton";
import { useAuth } from "@/contexts/AuthContext";
import StockMovementModal from "@/components/StockMovementModal";
import CreateProductModal from "@/components/dashboard/CreateProductModal";
import UploadExcel from "@/components/UploadExcel";
import { Product } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Package, 
  AlertTriangle, 
  TrendingDown, 
  DollarSign, 
  Sparkles,
  Search,
  RefreshCw,
  Download,
  Plus,
  BarChart3,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { apiService } from "@/services/apiService";
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';

interface KpiData {
  total_produtos: number;
  produtos_baixo_estoque: number;
  valor_total_estoque: number;
}

interface AIInsight {
  content: string;
  loading: boolean;
}

export default function DashboardPage() {
  const { products, loading, error, fetchProducts, createProduct, updateProduct, removeProduct, moveStock } = useProducts();
  const { logout } = useAuth();
  
  const [isDownloading, setIsDownloading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [isMovementModalOpen, setIsMovementModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [kpiData, setKpiData] = useState<KpiData | null>(null);
  const [kpiLoading, setKpiLoading] = useState(true);
  const [aiInsight, setAiInsight] = useState<AIInsight>({ content: '', loading: false });
  const [filterStatus, setFilterStatus] = useState<'all' | 'critical' | 'low' | 'ok'>('all');
  const [refreshing, setRefreshing] = useState(false);
  const [aiInsightMinimized, setAiInsightMinimized] = useState(false);

  useEffect(() => {
    fetchProducts(true);
    fetchKPIs();
    fetchAIInsight();
  }, [fetchProducts]);

  const fetchKPIs = async () => {
    try {
      const response = await apiService.get('/kpis/');
      setKpiData(response?.data || null);
    } catch (error) {
      console.error("Erro ao buscar KPIs:", error);
    } finally {
      setKpiLoading(false);
    }
  };

  const fetchAIInsight = async () => {
    setAiInsight({ content: '', loading: true });
    try {
      const response = await apiService.post('/insights/ask', { 
        question: 'Analise o estoque atual e me dê os 3 principais insights e alertas críticos que preciso saber AGORA. Seja direto e objetivo.' 
      });
      setAiInsight({ content: response?.data?.answer || '', loading: false });
    } catch (error) {
      console.error("Erro ao buscar insights da IA:", error);
      setAiInsight({ content: '', loading: false });
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await Promise.all([
      fetchProducts(true),
      fetchKPIs(),
      fetchAIInsight()
    ]);
    setRefreshing(false);
    toast.success('Dados atualizados!');
  };

  const handleDownloadExcel = async () => {
    setIsDownloading(true);
    const token = localStorage.getItem("authToken");
    if (!token) {
      alert("Sessão expirada. Por favor, faça login novamente.");
      logout();
      return;
    }
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${API_BASE_URL}/produtos/download/excel`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Falha ao gerar o arquivo de Excel.');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "higiplas_produtos.xlsx";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Excel exportado com sucesso!');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Ocorreu um erro');
    } finally {
      setIsDownloading(false);
    }
  };

  // Cálculos de estatísticas
  const stats = useMemo(() => {
    const critical = products.filter(p => p.quantidade_em_estoque <= (p.estoque_minimo || 0));
    const low = products.filter(p => 
      p.quantidade_em_estoque > (p.estoque_minimo || 0) && 
      p.quantidade_em_estoque <= ((p.estoque_minimo || 0) * 1.5)
    );
    const ok = products.filter(p => p.quantidade_em_estoque > ((p.estoque_minimo || 0) * 1.5));
    
    const totalValue = products.reduce((sum, p) => {
      return sum + (p.quantidade_em_estoque * (p.preco_custo || 0));
    }, 0);

    const recentMovements = products.filter(p => {
      // Produtos com movimentação recente (últimos 7 dias) - simulado
      return p.quantidade_em_estoque > 0;
    });

    return {
      critical: critical.length,
      low: low.length,
      ok: ok.length,
      totalValue,
      recentMovements: recentMovements.length,
      criticalProducts: critical.slice(0, 5)
    };
  }, [products]);

  const filteredProducts = useMemo(() => {
    let filtered = products.filter(p =>
      p.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.codigo.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (filterStatus === 'critical') {
      filtered = filtered.filter(p => p.quantidade_em_estoque <= (p.estoque_minimo || 0));
    } else if (filterStatus === 'low') {
      filtered = filtered.filter(p => 
        p.quantidade_em_estoque > (p.estoque_minimo || 0) && 
        p.quantidade_em_estoque <= ((p.estoque_minimo || 0) * 1.5)
      );
    } else if (filterStatus === 'ok') {
      filtered = filtered.filter(p => p.quantidade_em_estoque > ((p.estoque_minimo || 0) * 1.5));
    }

    return filtered;
  }, [products, searchTerm, filterStatus]);
  
  return (
    <> 
      <Header>
        <div className="flex items-center justify-between w-full">
          <div>
            <h1 className="text-xl font-bold text-gray-800 dark:text-gray-100">
              Estoque Inteligente
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Visão completa e insights em tempo real
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Atualizar
            </Button>
            <ThemeToggleButton />
            <button 
              onClick={logout} 
              aria-label="Sair" 
              className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-800/50 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
              </svg>
            </button>
          </div>
        </div>
      </Header>
        
      <main className="flex-1 p-4 md:p-6 overflow-y-auto bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-7xl mx-auto space-y-6">
          
          {/* KPIs Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total de Produtos */}
            <Card className="border-l-4 border-l-blue-500 hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total de Produtos</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                      {kpiLoading ? '...' : (kpiData?.total_produtos || products.length)}
                    </p>
                  </div>
                  <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full">
                    <Package className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Produtos Críticos */}
            <Card className={`border-l-4 ${stats.critical > 0 ? 'border-l-red-500' : 'border-l-green-500'} hover:shadow-lg transition-shadow`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Críticos</p>
                    <p className={`text-3xl font-bold mt-1 ${stats.critical > 0 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
                      {stats.critical}
                    </p>
                    {stats.critical > 0 && (
                      <p className="text-xs text-red-600 dark:text-red-400 mt-1">Ação necessária!</p>
                    )}
                  </div>
                  <div className={`p-3 rounded-full ${stats.critical > 0 ? 'bg-red-100 dark:bg-red-900/30' : 'bg-green-100 dark:bg-green-900/30'}`}>
                    <AlertTriangle className={`h-6 w-6 ${stats.critical > 0 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`} />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Produtos com Estoque Baixo */}
            <Card className="border-l-4 border-l-yellow-500 hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Atenção</p>
                    <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mt-1">
                      {stats.low}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Próximo do mínimo</p>
                  </div>
                  <div className="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-full">
                    <TrendingDown className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Valor Total do Estoque */}
            <Card className="border-l-4 border-l-purple-500 hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Valor Total</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                      {stats.totalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Em estoque</p>
                  </div>
                  <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-full">
                    <DollarSign className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Insights da IA */}
          <Card className="border-l-4 border-l-gradient-to-b from-blue-500 to-purple-600 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                    <Sparkles className="h-5 w-5 text-white" />
                  </div>
                  <CardTitle className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    Insights da IA - Rozana
                  </CardTitle>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={fetchAIInsight}
                    disabled={aiInsight.loading}
                    title="Atualizar insights"
                  >
                    <RefreshCw className={`h-4 w-4 ${aiInsight.loading ? 'animate-spin' : ''}`} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setAiInsightMinimized(!aiInsightMinimized)}
                    title={aiInsightMinimized ? "Expandir" : "Minimizar"}
                  >
                    {aiInsightMinimized ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronUp className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </CardHeader>
            {!aiInsightMinimized && (
              <CardContent>
                {aiInsight.loading ? (
                  <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <span>Analisando estoque...</span>
                  </div>
                ) : aiInsight.content ? (
                  <div className="prose dark:prose-invert max-w-none prose-sm">
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => <p className="mb-2 last:mb-0 text-gray-700 dark:text-gray-300">{children}</p>,
                        ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                        strong: ({ children }) => <strong className="font-bold text-gray-900 dark:text-gray-100">{children}</strong>,
                      }}
                    >
                      {aiInsight.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p className="text-gray-500 dark:text-gray-400">Clique em atualizar para ver insights</p>
                )}
              </CardContent>
            )}
          </Card>

          {/* Alertas Críticos */}
          {stats.critical > 0 && (
            <Card className="border-2 border-red-500 bg-red-50 dark:bg-red-900/20">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400" />
                  <CardTitle className="text-lg font-bold text-red-900 dark:text-red-100">
                    🚨 Alertas Críticos - Ação Imediata Necessária
                  </CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {stats.criticalProducts.map((product) => (
                    <div 
                      key={product.id}
                      className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border border-red-200 dark:border-red-800"
                    >
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 dark:text-gray-100">{product.nome}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Estoque: {product.quantidade_em_estoque} | Mínimo: {product.estoque_minimo || 0}
                        </p>
                      </div>
                      <Badge variant="destructive" className="ml-4">
                        Crítico
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Tabela de Produtos */}
          <Card>
            <CardHeader>
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <CardTitle className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  Produtos em Estoque
                </CardTitle>
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full md:w-auto">
                  {/* Filtros */}
                  <div className="flex gap-2">
                    <Button
                      variant={filterStatus === 'all' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setFilterStatus('all')}
                    >
                      Todos ({products.length})
                    </Button>
                    <Button
                      variant={filterStatus === 'critical' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setFilterStatus('critical')}
                      className="border-red-500 text-red-600 hover:bg-red-50"
                    >
                      Críticos ({stats.critical})
                    </Button>
                    <Button
                      variant={filterStatus === 'low' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setFilterStatus('low')}
                      className="border-yellow-500 text-yellow-600 hover:bg-yellow-50"
                    >
                      Atenção ({stats.low})
                    </Button>
                  </div>
                  
                  {/* Busca */}
                  <div className="relative flex-1 sm:flex-initial">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <input
                      type="text"
                      placeholder="Buscar produto..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border rounded-md bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <Button onClick={() => setIsCreateModalOpen(true)} size="default">
                    <Plus className="h-4 w-4 mr-2" />
                    Novo Produto
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading && (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              )}
              {error && (
                <div className="p-8 text-center text-red-500">
                  <p>{error}</p>
                </div>
              )}
              {!loading && !error && (
                <>
                  <div className="mb-4 flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                    <span>Mostrando {filteredProducts.length} de {products.length} produtos</span>
                    {filterStatus !== 'all' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setFilterStatus('all')}
                      >
                        Limpar filtro
                      </Button>
                    )}
                  </div>
                  <ProductTable
                    products={filteredProducts}
                    onSave={updateProduct}
                    onRemove={removeProduct}
                    onMoveStock={(product) => { 
                      setSelectedProduct(product); 
                      setIsMovementModalOpen(true); 
                    }}
                  />
                </>
              )}
            </CardContent>
          </Card>

          {/* Ações Rápidas */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-bold text-gray-900 dark:text-gray-100">
                Ações Rápidas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                <UploadExcel onUploadSuccess={() => { fetchProducts(true); fetchKPIs(); }} />
                <Button 
                  onClick={handleDownloadExcel} 
                  disabled={isDownloading}
                  variant="outline"
                >
                  <Download className="h-4 w-4 mr-2" />
                  {isDownloading ? "Gerando..." : "Exportar Excel"}
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => window.location.href = '/dashboard/insights'}
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  Chat com IA
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => window.location.href = '/dashboard/compras'}
                >
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Sugestões de Compra
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Modais */}
      {selectedProduct && (
        <StockMovementModal 
          isOpen={isMovementModalOpen} 
          onClose={() => setIsMovementModalOpen(false)} 
          onSubmit={(tipo, qtd, obs) => moveStock(selectedProduct.id, tipo, qtd, obs).then(() => {
            setIsMovementModalOpen(false);
            fetchProducts(true);
            fetchKPIs();
            fetchAIInsight();
          })} 
          productName={selectedProduct.nome}
        />
      )}
      <CreateProductModal 
        isOpen={isCreateModalOpen} 
        onClose={() => setIsCreateModalOpen(false)} 
        onCreate={(data) => createProduct(data).then(() => {
          fetchProducts(true);
          fetchKPIs();
          fetchAIInsight();
        })}
      />
    </>
  );
}
