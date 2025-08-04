// /src/hooks/useProducts.ts

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Product, ProdutoCreateData, ProdutoUpdateData } from '@/types';
import { apiService } from '@/services/apiService';

export function useProducts() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Envolvemos a função de erro em useCallback para estabilizar sua referência
  const handleApiError = useCallback((err: unknown) => {
    const errorMessage = err instanceof Error ? err.message : "Ocorreu um erro desconhecido.";

    // Verifica se o erro é de autenticação (401 Unauthorized)
    if (errorMessage.includes("[401]")) {
      localStorage.removeItem("authToken");
      router.push('/');
      setError("Sessão expirou. Faça login novamente.");
    } else {
      setError(errorMessage);
    }
  }, [router]);

  const fetchProducts = useCallback(async (force = false) => {
    // Só faz a chamada se ainda não tiver produtos ou se for forçado
    if (products.length > 0 && !force) {
        return;
    }
    
    setLoading(true);
    try {
      const data = await apiService.get('/produtos/');
      setProducts(data);
      setError(null);
    } catch (err) {
      handleApiError(err);
    } finally {
      setLoading(false);
    }
  }, [products.length, handleApiError]);

  const createProduct = async (newProductData: ProdutoCreateData) => {
    try {
      await apiService.post('/produtos/', newProductData);
      await fetchProducts();
      alert("Produto criado com sucesso!");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro desconhecido";
      alert(`Erro ao criar produto: ${message}`);
    }
  };

  const updateProduct = async (productId: number, updateData: ProdutoUpdateData) => {
    try {
      await apiService.put(`/produtos/${productId}`, updateData);
      await fetchProducts();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro desconhecido";
      alert(`Erro ao salvar produto: ${message}`);
    }
  };

  const removeProduct = async (productId: number) => {
    if (!confirm("Tem certeza que deseja remover este produto? A ação não pode ser desfeita.")) return;
    try {
      await apiService.delete(`/produtos/${productId}`);
      setProducts(current => current.filter(p => p.id !== productId));
      alert("Produto removido com sucesso!");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro desconhecido";
      alert(`Erro ao remover produto: ${message}`);
    }
  };

  const moveStock = async (productId: number, tipo: 'entrada' | 'saida', quantidade: number) => {
    try {
      await apiService.post('/movimentacoes/', {
        produto_id: productId,
        tipo_movimentacao: tipo.toUpperCase(),
        quantidade,
      });
      await fetchProducts();
      alert("Movimentação registrada com sucesso!");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro desconhecido";
      alert(`Erro na movimentação: ${message}`);
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