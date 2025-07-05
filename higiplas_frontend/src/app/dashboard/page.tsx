// /src/app/dashboard/page.tsx

"use client";

import { useEffect, useState } from "react";
import { useRouter } from 'next/navigation';

import { useProducts } from "@/hooks/useProducts";
import { ProductTable } from "@/components/dashboard/ProductTable";
import { Header } from "@/components/Header"; // Importando o Header global
import { DashboardHeader } from "@/components/dashboard/DashboardHeader"; // O header específico da página
import StockMovementModal from "@/components/StockMovementModal";
import CreateProductModal from "@/components/dashboard/CreateProductModal";
import { Product } from '@/types';

export default function DashboardPage() {
  const router = useRouter();
  const { products, loading, error, fetchProducts, createProduct, updateProduct, removeProduct, moveStock } = useProducts();

  const [searchTerm, setSearchTerm] = useState("");
  const [isMovementModalOpen, setIsMovementModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  useEffect(() => { fetchProducts(); }, [fetchProducts]);

  const handleLogout = () => {
    if (confirm("Tem certeza que deseja sair?")) {
      localStorage.removeItem("authToken");
      router.push('/');
    }
  };

  const filteredProducts = products.filter(p =>
    p.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.codigo.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
      {/* <Sidebar />  Um espaço reservado para uma futura barra lateral de navegação */}

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onLogoutClick={handleLogout} />
        
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            <DashboardHeader
              onNewProductClick={() => setIsCreateModalOpen(true)}
              onUploadSuccess={fetchProducts}
              onLogoutClick={() => {
                if (confirm("Tem certeza que deseja sair?")) {
                  handleLogout();
                }
              }}
            />

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
      </div>

      {/* Modais */}
      {selectedProduct && <StockMovementModal isOpen={isMovementModalOpen} onClose={() => setIsMovementModalOpen(false)} onSubmit={(tipo, qtd) => moveStock(selectedProduct.id, tipo, qtd).then(() => setIsMovementModalOpen(false))} productName={selectedProduct.nome} />}
      <CreateProductModal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} onCreate={(data) => createProduct(data).then(() => setIsCreateModalOpen(false))} />
    </div>
  );
}