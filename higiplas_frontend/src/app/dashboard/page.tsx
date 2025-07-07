// /src/app/dashboard/page.tsx
"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/dashboard/Header";
import { ProductTable } from "@/components/dashboard/ProductTable";
import { ThemeToggleButton } from "@/components/ThemeToggleButton";
import { useAuth } from "@/contexts/AuthContext";
import UploadExcel from "@/components/UploadExcel";
import { useProducts } from "@/hooks/useProducts";
import StockMovementModal from "@/components/StockMovementModal";
import CreateProductModal from "@/components/dashboard/CreateProductModal";
import { Product } from '@/types';
import ClientLayout from "@/components/ClientLayout";


// O wrapper para proteção de rota continua exatamente o mesmo. É a abordagem correta.
export default function DashboardPageWrapper() {
  return (
    <ClientLayout>
      <DashboardPage />
    </ClientLayout>
  );
}

// O conteúdo real da página
function DashboardPage() {
  const { products, loading, error, fetchProducts, createProduct, updateProduct, removeProduct, moveStock } = useProducts();
  const { logout } = useAuth();
  
  const [isDownloading, setIsDownloading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [isMovementModalOpen, setIsMovementModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  useEffect(() => { fetchProducts(); }, [fetchProducts]);

  const handleDownloadExcel = async () => {
    setIsDownloading(true);
    const token = localStorage.getItem("authToken");
    if (!token) {
      alert("Sessão expirada. Por favor, faça login novamente.");
      logout();
      setIsDownloading(false);
      return;
    }
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/produtos/download/excel`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Falha ao gerar o arquivo de Excel.');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "higiplas_produtos_estoque.xlsx";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);
      alert(error instanceof Error ? error.message : "Ocorreu um erro desconhecido.");
    } finally {
      setIsDownloading(false);
    }
  };

  const filteredProducts = products.filter(p =>
    p.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.codigo.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  return (
    <div className="flex flex-col h-screen bg-gray-100 dark:bg-gray-900">
      
      {/* A PÁGINA MONTA SEU PRÓPRIO HEADER USANDO O CONTAINER SIMPLES */}
      <Header>
        <h1 className="text-xl font-bold text-gray-800 dark:text-gray-100 hidden sm:block">
            Visão Geral do Estoque
        </h1>
        <div className="flex-1" /> {/* Espaçador para empurrar os botões para a direita */}
        <div className="flex items-center gap-2">
            <button onClick={handleDownloadExcel} disabled={isDownloading} className="px-3 py-2 text-sm font-semibold rounded-lg bg-gray-500 text-white hover:bg-gray-600 disabled:opacity-50 transition-colors">
              Exportar
            </button>
            <UploadExcel onUploadSuccess={fetchProducts} />
            <button onClick={() => setIsCreateModalOpen(true)} className="px-3 py-2 text-sm font-semibold rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors">
              + Novo
            </button>
        </div>
        <div className="flex items-center gap-2 border-l border-gray-300 dark:border-gray-600 ml-2 pl-2">
            <ThemeToggleButton />
            <button onClick={logout} aria-label="Sair" className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-800/50 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
              </svg>
            </button>
        </div>
      </Header>
        
      <main className="flex-1 overflow-x-hidden overflow-y-auto p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
            <div className="mb-6">
              <input
                  type="text"
                  placeholder="Buscar por nome ou código..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full max-w-sm px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="bg-white dark:bg-gray-800/50 rounded-lg shadow-md">
                {loading && <p className="p-8 text-center text-gray-500">Carregando...</p>}
                {error && <p className="p-8 text-center text-red-500">{error}</p>}
                {!loading && !error && 
                  <ProductTable
                    products={filteredProducts}
                    onSave={updateProduct}
                    onRemove={removeProduct}
                    onMoveStock={(product) => { setSelectedProduct(product); setIsMovementModalOpen(true); }}
                  />
                }
            </div>
        </div>
      </main>

      {/* MODAIS */}
      {selectedProduct && <StockMovementModal 
        isOpen={isMovementModalOpen} 
        onClose={() => setIsMovementModalOpen(false)} 
        onSubmit={(tipo, qtd) => moveStock(selectedProduct.id, tipo, qtd).then(() => setIsMovementModalOpen(false))} 
        productName={selectedProduct.nome}
      />}
      <CreateProductModal 
        isOpen={isCreateModalOpen} 
        onClose={() => setIsCreateModalOpen(false)} 
        onCreate={(data) => createProduct(data).then(() => setIsCreateModalOpen(false))}
      />
    </div>
  );
}