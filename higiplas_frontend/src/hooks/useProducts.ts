// /app/hooks/useProducts.ts

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Product, ProdutoCreateData, ProdutoUpdateData } from '@/types';
import { apiService } from '@/services/apiService'; // Usando nosso serviço de API

export function useProducts() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleApiError = (err: any) => {
    if (err.message.includes("401")) {
      localStorage.removeItem("authToken");
      router.push('/');
      setError("Sessão expirou. Faça login novamente.");
    } else {
      setError(err.message);
    }
  };

  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.get('/produtos/');
      setProducts(data);
      setError(null);
    } catch (err: any) {
      handleApiError(err);
    } finally {
      setLoading(false);
    }
  }, [router]);

  const createProduct = async (newProductData: ProdutoCreateData) => {
    try {
      await apiService.post('/produtos/', newProductData);
      await fetchProducts(); // Revalida a lista
      alert("Produto criado com sucesso!");
    } catch (err: any) {
      alert(`Erro ao criar produto: ${err.message}`);
    }
  };

  const updateProduct = async (productId: number, updateData: ProdutoUpdateData) => {
    try {
      await apiService.put(`/produtos/${productId}`, updateData);
      await fetchProducts(); // Revalida a lista
    } catch (err: any) {
      alert(`Erro ao salvar produto: ${err.message}`);
    }
  };

  const removeProduct = async (productId: number) => {
    if (!confirm("Tem certeza que deseja remover este produto? A ação não pode ser desfeita.")) return;
    try {
      await apiService.delete(`/produtos/${productId}`);
      setProducts(current => current.filter(p => p.id !== productId));
      alert("Produto removido com sucesso!");
    } catch (err: any) {
      alert(`Erro ao remover produto: ${err.message}`);
    }
  };

  const moveStock = async (productId: number, tipo: 'entrada' | 'saida', quantidade: number) => {
    try {
      await apiService.post('/movimentacoes/', {
        produto_id: productId,
        tipo_movimentacao: tipo.toUpperCase(),
        quantidade,
      });
      await fetchProducts(); // Revalida a lista
      alert("Movimentação registrada com sucesso!");
    } catch (err: any) {
      alert(`Erro na movimentação: ${err.message}`);
    }
  };

  return {
    products,
    loading,
    error,
    fetchProducts,
    createProduct,
    updateProduct,
    removeProduct,
    moveStock,
  };
}