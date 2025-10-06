// /src/app/dashboard/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useProducts } from "@/hooks/useProducts";
import { ProductTable } from "@/components/dashboard/ProductTable";
import { Header } from "@/components/dashboard/Header";
import { ThemeToggleButton } from "@/components/ThemeToggleButton";
import { useAuth } from "@/contexts/AuthContext";
import StockMovementModal from "@/components/StockMovementModal";
import CreateProductModal from "@/components/dashboard/CreateProductModal";
import UploadExcel from "@/components/UploadExcel";
import { Product } from "@/types";
import Button from "@/components/Button";
import { DashboardCards } from "@/components/dashboard/DashboardCards";

export default function DashboardPage() {
  const { products, loading, error, fetchProducts, createProduct, updateProduct, removeProduct, moveStock } = useProducts();
  const { logout, user } = useAuth(); // <<< Pegamos o 'user' do hook de autenticação
  
  const [isDownloading, setIsDownloading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [isMovementModalOpen, setIsMovementModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  useEffect(() => {
    fetchProducts(true); // Força o fetch ao carregar a página
  }, [fetchProducts]);

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
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Ocorreu um erro');
    } finally {
      setIsDownloading(false);
    }
  };

  const filteredProducts = products.filter(p =>
    p.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.codigo.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  return (
    <> 
      <Header>
        <h1 className="text-xl font-bold text-gray-800 dark:text-gray-100">
          Dashboard
        </h1>
        <div className="flex-1" />
        <div className="flex items-center gap-2 border-l border-gray-300 dark:border-gray-600 ml-2 pl-2">
            <ThemeToggleButton />
            <button onClick={logout} aria-label="Sair" className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-800/50 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
              </svg>
            </button>
        </div>
      </Header>
        
      <main className="flex-1 p-4 md:p-6 overflow-y-auto">
        <div className="max-w-7xl mx-auto space-y-8">
            {/* --- 2. ADICIONAR UMA SEÇÃO DE BOAS-VINDAS E OS CARDS --- */}
            <div>
              <h2 className="text-2xl md:text-3xl font-bold text-gray-800 dark:text-gray-100">
                Olá, {user?.nome || 'Usuário'}! 👋
              </h2>
              <p className="text-gray-500 dark:text-gray-400 mt-1">Aqui está um resumo do seu estoque hoje.</p>
              <div className="mt-6">
                <DashboardCards />
              </div>
            </div>

            {/* --- 3. AGRUPAR A TABELA E AÇÕES EM UM CARD SEPARADO --- */}
            <div className="bg-white dark:bg-gray-800 p-4 md:p-6 rounded-lg shadow-md border dark:border-gray-700">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                    Visão Geral do Estoque
                  </h3>
                  <div className="flex flex-col sm:flex-row items-center gap-2 w-full md:w-auto">
                    <input
                        type="text"
                        placeholder="Buscar por nome ou código..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full md:w-auto px-4 py-2 border rounded-md bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600"
                    />
                    <Button onClick={() => setIsCreateModalOpen(true)}>+ Novo Produto</Button>
                  </div>
              </div>
            
              {loading && <p className="p-8 text-center">Carregando...</p>}
              {error && <p className="p-8 text-center text-red-500">{error}</p>}
              {!loading && !error && 
                <ProductTable
                  products={filteredProducts}
                  onSave={updateProduct}
                  onRemove={removeProduct}
                  onMoveStock={(product) => { setSelectedProduct(product); setIsMovementModalOpen(true); }}
                />
              }

              <div className="mt-6 flex flex-col sm:flex-row gap-4">
                  <UploadExcel onUploadSuccess={() => fetchProducts(true)} />
                  <Button onClick={handleDownloadExcel} disabled={isDownloading} variant="secondary">
                    {isDownloading ? "Gerando..." : "Exportar para Excel"}
                  </Button>
              </div>
            </div>
        </div>
      </main>

      {/* Os modais permanecem, pois são específicos desta página */}
      {selectedProduct && <StockMovementModal 
        isOpen={isMovementModalOpen} 
        onClose={() => setIsMovementModalOpen(false)} 
        onSubmit={(tipo, qtd, obs) => moveStock(selectedProduct.id, tipo, qtd, obs).then(() => setIsMovementModalOpen(false))} 
        productName={selectedProduct.nome}
      />}
      <CreateProductModal 
        isOpen={isCreateModalOpen} 
        onClose={() => setIsCreateModalOpen(false)} 
        onCreate={(data) => createProduct(data)}
      />
    </>
  );
}