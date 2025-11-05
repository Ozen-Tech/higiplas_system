// /src/components/vendedor/ProductSearch.tsx
// Componente de busca rápida de produtos (sem filtro de estoque)

'use client';

import { useState, useEffect } from 'react';
import { Search, PlusCircle, Package } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Product } from '@/types';

interface ProductSearchProps {
  produtos: Product[];
  onSelectProduct: (product: Product) => void;
  loading?: boolean;
}

export function ProductSearch({ produtos, onSelectProduct, loading = false }: ProductSearchProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);

  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredProducts([]);
      return;
    }

    const term = searchTerm.toLowerCase();
    const filtered = produtos.filter(
      (p) =>
        p.nome.toLowerCase().includes(term) ||
        p.codigo.toLowerCase().includes(term) ||
        p.categoria.toLowerCase().includes(term)
    ).slice(0, 10); // Limita a 10 resultados para performance

    setFilteredProducts(filtered);
  }, [searchTerm, produtos]);

  const handleSelectProduct = (product: Product) => {
    onSelectProduct(product);
    setSearchTerm('');
    setFilteredProducts([]);
  };

  return (
    <div className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
        <Input
          type="text"
          placeholder="Buscar produto por nome, código ou categoria..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10 pr-4"
          disabled={loading}
        />
      </div>

      {/* Resultados da busca */}
      {searchTerm && filteredProducts.length > 0 && (
        <Card className="absolute z-50 w-full mt-2 max-h-96 overflow-y-auto shadow-lg">
          <CardContent className="p-2">
            <div className="space-y-1">
              {filteredProducts.map((product) => (
                <button
                  key={product.id}
                  onClick={() => handleSelectProduct(product)}
                  className="w-full text-left p-3 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors flex items-center justify-between group"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <Package size={16} className="text-gray-400 flex-shrink-0" />
                      <p className="font-semibold text-sm truncate">{product.nome}</p>
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                      <span>Código: {product.codigo}</span>
                      <span>Estoque: {product.quantidade_em_estoque}</span>
                      <span className="font-semibold text-green-600">
                        R$ {product.preco_venda.toFixed(2)}
                      </span>
                    </div>
                  </div>
                  <PlusCircle
                    size={20}
                    className="text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 ml-2"
                  />
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Mensagem quando não há resultados */}
      {searchTerm && filteredProducts.length === 0 && !loading && (
        <Card className="absolute z-50 w-full mt-2 shadow-lg">
          <CardContent className="p-4 text-center text-gray-500">
            <p>Nenhum produto encontrado</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

