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

// Componente separado para os botões de ação
function DashboardActions({ onNewProduct, onUploadSuccess }: { onNewProduct: () => void; onUploadSuccess: () => void; }) {
  const [isDownloading, setIsDownloading] = useState(false);
  
  const handleDownloadExcel = async () => { /* Sua lógica de download aqui... */ };

  return (
    <div className="flex items-center gap-2">
      <button onClick={handleDownloadExcel} disabled={isDownloading} className="...">
        {isDownloading ? "Gerando..." : "Exportar Excel"}
      </button>
      <UploadExcel onUploadSuccess={onUploadSuccess} />
      <button onClick={onNewProduct} className="...">
        + Novo Produto
      </button>
    </div>
  );
}

export default function DashboardPage() {
  // a lógica de logout foi movida para o AuthContext!
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
        {/* O Header agora é o componente principal de layout da página */}
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
            {/* O input de busca pode vir para cá */}
            <div className="mb-6">
              <input /* ... */ />
            </div>
            
            <div className="bg-white dark:bg-gray-800/50 rounded-lg shadow-md">
                {/* ... sua tabela e modais ... */}
            </div>
          </div>
        </main>
    </div>
  );
}