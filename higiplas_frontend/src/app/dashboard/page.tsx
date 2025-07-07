// /src/app/dashboard/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useProducts } from "@/hooks/useProducts";
import { ProductTable } from "@/components/dashboard/ProductTable";
import { Header } from "@/components/dashboard/Header"; // Agora só usamos um Header
import UploadExcel from "@/components/UploadExcel";
import StockMovementModal from "@/components/StockMovementModal";
import CreateProductModal from "@/components/dashboard/CreateProductModal";
import { Product } from '@/types';
import { useAuth } from "@/contexts/AuthContext"; // Importar useAuth para download

// Componente separado para os botões de ação
function DashboardActions({ onNewProduct, onUploadSuccess }: { onNewProduct: () => void; onUploadSuccess: () => void; }) {
  const [isDownloading, setIsDownloading] = useState(false);
  const { logout } = useAuth(); // Usando o logout do contexto para o fallback do download

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
      
      if (!response.ok) {
        throw new Error('Falha ao gerar o arquivo de Excel.');
      }
      
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

  return (
    <div className="flex items-center gap-2">
      <button onClick={handleDownloadExcel} disabled={isDownloading} className="px-4 py-2 text-sm font-semibold rounded-lg shadow-md bg-gray-500 text-white hover:bg-gray-600 disabled:opacity-50 transition-colors">
        {isDownloading ? "Gerando..." : "Exportar Excel"}
      </button>
      <UploadExcel onUploadSuccess={onUploadSuccess} />
      <button onClick={onNewProduct} className="px-4 py-2 text-sm font-semibold rounded-lg shadow-md bg-blue-600 text-white hover:bg-blue-700 transition-colors">
        + Novo Produto
      </button>
    </div>
  );
}

export default function DashboardPage() {
  const { products, loading, error, fetchProducts, createProduct, updateProduct, removeProduct, moveStock } = useProducts();

  const [searchTerm, setSearchTerm] = useState("");
  const [isMovementModalOpen, setIsMovementModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  useEffect(() => { fetchProducts(); }, [fetchProducts]);

  const filteredProducts = products.filter(p =>
    p.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.codigo.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex flex-col h-screen bg-gray-100 dark:bg-gray-900">
      <Header 
        title="Visão Geral do Estoque"
        actions={
          <DashboardActions
            onNewProduct={() => setIsCreateModalOpen(true)}
            onUploadSuccess={fetchProducts}
          />
        }
      />
        
      <main className="flex-1 overflow-x-hidden overflow-y-auto p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          {/* O input de busca que faltava ser usado */}
          <div className="mb-6">
            <input
              type="text"
              placeholder="Buscar por nome ou código..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full max-w-sm px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
            
          {/* O conteúdo principal que faltava */}
          <div className="bg-white dark:bg-gray-800/50 rounded-lg shadow-md">
            {loading && <p className="p-8 text-center text-gray-500">Carregando produtos...</p>}
            {error && <p className="p-8 text-center text-red-500">{error}</p>}
            {!loading && !error && (
              <ProductTable
                products={filteredProducts}
                onSave={updateProduct}
                onRemove={removeProduct}
                onMoveStock={(product) => { setSelectedProduct(product); setIsMovementModalOpen(true); }}
              />
            )}
          </div>
        </div>
      </main>

      {/* Os modais que faltavam */}
      {selectedProduct && 
        <StockMovementModal 
          isOpen={isMovementModalOpen} 
          onClose={() => setIsMovementModalOpen(false)} 
          onSubmit={(tipo, qtd) => moveStock(selectedProduct.id, tipo, qtd).then(() => setIsMovementModalOpen(false))} 
          productName={selectedProduct.nome} 
        />
      }
      <CreateProductModal 
        isOpen={isCreateModalOpen} 
        onClose={() => setIsCreateModalOpen(false)} 
        onCreate={(data) => createProduct(data).then(() => setIsCreateModalOpen(false))} 
      />
    </div>
  );
}