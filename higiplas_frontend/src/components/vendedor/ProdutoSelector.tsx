'use client';

import { useState } from 'react';
import { Produto } from '@/types/vendas';
import { ItemCarrinhoOrcamento } from '@/types/orcamentos';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Search, Plus, Package } from 'lucide-react';

interface ProdutoSelectorProps {
  produtos: Produto[];
  carrinho: ItemCarrinhoOrcamento[];
  onAdicionarProduto: (produto: Produto) => void;
  loading?: boolean;
}

export function ProdutoSelector({
  produtos,
  carrinho,
  onAdicionarProduto,
  loading = false,
}: ProdutoSelectorProps) {
  const [termoBusca, setTermoBusca] = useState('');

  const produtosFiltrados = produtos.filter(p =>
    p.nome.toLowerCase().includes(termoBusca.toLowerCase()) ||
    p.codigo?.toLowerCase().includes(termoBusca.toLowerCase())
  );

  const produtoNoCarrinho = (produtoId: number) => {
    return carrinho.some(item => item.produto_id === produtoId);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Package size={20} /> Produtos Disponíveis
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
          <Input
            placeholder="Buscar por nome ou código..."
            value={termoBusca}
            onChange={(e) => setTermoBusca(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="max-h-96 overflow-y-auto space-y-2">
          {produtosFiltrados.length === 0 ? (
            <p className="text-center text-gray-500 py-4">Nenhum produto encontrado</p>
          ) : (
            produtosFiltrados.map((produto) => (
              <div
                key={produto.id}
                className="p-3 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="font-medium">{produto.nome}</p>
                    <div className="flex gap-4 mt-1 text-sm text-gray-600 dark:text-gray-400">
                      {produto.codigo && (
                        <span>Cód: {produto.codigo}</span>
                      )}
                      <span>Estoque: {produto.estoque_disponivel}</span>
                      <span className="font-semibold text-green-600 dark:text-green-400">
                        R$ {produto.preco.toFixed(2)}
                      </span>
                    </div>
                    {produto.estatisticas_preco && (
                      produto.estatisticas_preco.preco_maior !== null || 
                      produto.estatisticas_preco.preco_medio !== null || 
                      produto.estatisticas_preco.preco_menor !== null
                    ) && (
                      <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                        <div className="flex flex-wrap gap-3 text-xs">
                          {produto.estatisticas_preco.preco_maior !== null && produto.estatisticas_preco.preco_maior !== undefined && (
                            <span className="text-red-600 dark:text-red-400">
                              <span className="font-semibold">Maior:</span> R$ {produto.estatisticas_preco.preco_maior.toFixed(2)}
                            </span>
                          )}
                          {produto.estatisticas_preco.preco_medio !== null && produto.estatisticas_preco.preco_medio !== undefined && (
                            <span className="text-blue-600 dark:text-blue-400">
                              <span className="font-semibold">Médio:</span> R$ {produto.estatisticas_preco.preco_medio.toFixed(2)}
                            </span>
                          )}
                          {produto.estatisticas_preco.preco_menor !== null && produto.estatisticas_preco.preco_menor !== undefined && (
                            <span className="text-green-600 dark:text-green-400">
                              <span className="font-semibold">Menor:</span> R$ {produto.estatisticas_preco.preco_menor.toFixed(2)}
                            </span>
                          )}
                          {produto.estatisticas_preco.total_vendas > 0 && (
                            <span className="text-gray-500 dark:text-gray-400">
                              ({produto.estatisticas_preco.total_vendas} vendas)
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                  <Button
                    size="sm"
                    onClick={() => onAdicionarProduto(produto)}
                    disabled={produtoNoCarrinho(produto.id) || loading}
                    className="gap-2"
                  >
                    {produtoNoCarrinho(produto.id) ? (
                      'Adicionado'
                    ) : (
                      <>
                        <Plus size={14} /> Adicionar
                      </>
                    )}
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}

