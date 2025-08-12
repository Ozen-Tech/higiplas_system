// /src/hooks/useProducts.ts

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Product, ProdutoCreateData, ProdutoUpdateData } from '@/types';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';

// Interface para produto da API
interface ApiProduct {
  id: number;
  nome: string;
  codigo_barras?: string;
  categoria?: string;
  descricao?: string;
  preco_compra?: number;
  preco_venda?: number;
  unidade?: string;
  estoque_minimo?: number;
  empresa_id: number;
  estoque_atual?: number;
  data_validade?: string;
  data_criacao: string;
}

// Funções de mapeamento de dados
const mapProductFromApi = (apiProduct: ApiProduct): Product => ({
  id: apiProduct.id,
  nome: apiProduct.nome,
  codigo: apiProduct.codigo_barras || '',
  categoria: apiProduct.categoria || '',
  descricao: apiProduct.descricao,
  preco_custo: apiProduct.preco_compra || 0,
  preco_venda: apiProduct.preco_venda || 0,
  unidade_medida: apiProduct.unidade || '',
  estoque_minimo: apiProduct.estoque_minimo,
  empresa_id: apiProduct.empresa_id,
  quantidade_em_estoque: apiProduct.estoque_atual || 0,
  data_validade: apiProduct.data_validade,
  creationDate: apiProduct.data_criacao,
});

const mapToApiData = (data: Partial<ProdutoCreateData | ProdutoUpdateData>): Record<string, unknown> => ({
  nome: data.nome,
  descricao: data.descricao,
  preco_compra: data.preco_custo,
  preco_venda: data.preco_venda,
  unidade: data.unidade_medida,
  categoria: data.categoria,
  codigo_barras: data.codigo,
  estoque_minimo: data.estoque_minimo,
  data_validade: data.data_validade,
});


export function useProducts() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<Product[]>([]);

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
      setProducts(data.map(mapProductFromApi));
      setError(null);
    } catch (err) {
      handleApiError(err);
    } finally {
      setLoading(false);
    }
  }, [products.length, handleApiError]);

  const createProduct = async (newProductData: ProdutoCreateData) => {
    const promise = apiService.post('/produtos/', mapToApiData(newProductData)).then(() => {
      // Força a busca de produtos apenas após o sucesso
      return fetchProducts(true);
    });

    toast.promise(promise, {
      loading: 'Criando produto...',
      success: 'Produto criado com sucesso!',
      error: (err) => `Erro ao criar: ${err.message}`,
    });
  };

  const removeProduct = async (productId: number) => {
    if (!confirm("Tem certeza que deseja remover este produto? A ação não pode ser desfeita.")) return;
    
    const promise = apiService.delete(`/produtos/${productId}`).then(() => {
      // Atualiza o estado localmente para uma resposta mais rápida na UI
      setProducts(current => current.filter(p => p.id !== productId));
    });

    toast.promise(promise, {
        loading: 'Removendo produto...',
        success: 'Produto removido com sucesso!',
        error: (err) => `Erro ao remover: ${err.message}`,
    });
  };

  const moveStock = async (productId: number, tipo: 'entrada' | 'saida', quantidade: number, observacao?: string) => {
    const promise = apiService.post('/movimentacoes/', {
      produto_id: productId,
      tipo_movimentacao: tipo.toUpperCase(),
      quantidade,
      observacao,
    }).then(() => {
      // Força a busca de produtos para atualizar o estoque
      return fetchProducts(true);
    });

    toast.promise(promise, {
        loading: 'Registrando movimentação...',
        success: 'Estoque atualizado com sucesso!',
        error: (err) => `Erro na movimentação: ${err.message}`,
    });
  };

  const updateProduct = async (productId: number, updateData: ProdutoUpdateData) => {
    try {
      await apiService.put(`/produtos/${productId}`, mapToApiData(updateData));
      await fetchProducts(true); // Força a atualização para refletir as mudanças
      toast.success('Produto atualizado com sucesso!');
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro desconhecido";
      toast.error(`Erro ao salvar produto: ${message}`);
    }
  };

  const searchProducts = async (query: string): Promise<Product[]> => {
    if (!query.trim()) {
      setSearchResults([]);
      return [];
    }

    try {
      const data = await apiService.get(`/produtos/buscar/?q=${encodeURIComponent(query)}`);
      const results = data.map(mapProductFromApi);
      setSearchResults(results);
      return results;
    } catch (err) {
      handleApiError(err);
      return [];
    }
  };

  return {
    products, loading, error, searchResults, fetchProducts,
    createProduct, updateProduct, removeProduct, moveStock, searchProducts,
  };
}