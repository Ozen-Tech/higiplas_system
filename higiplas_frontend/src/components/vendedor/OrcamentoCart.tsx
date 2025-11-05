// /src/components/vendedor/OrcamentoCart.tsx
// Carrinho de itens do orçamento

'use client';

import { Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export interface ItemCarrinho {
  produto_id: number;
  nome: string;
  preco_original: number;
  preco_unitario_editavel: number;
  quantidade: number;
  estoque_disponivel: number;
}

interface OrcamentoCartProps {
  items: ItemCarrinho[];
  onUpdateItem: (produtoId: number, campo: 'quantidade' | 'preco', valor: number) => void;
  onRemoveItem: (produtoId: number) => void;
}

export function OrcamentoCart({
  items,
  onUpdateItem,
  onRemoveItem,
}: OrcamentoCartProps) {
  const total = items.reduce(
    (acc, item) => acc + item.preco_unitario_editavel * item.quantidade,
    0
  );

  if (items.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Carrinho de Itens</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-gray-500 py-8">Nenhum item adicionado</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Carrinho de Itens</span>
          <span className="text-lg font-bold text-blue-600">
            {items.length} {items.length === 1 ? 'item' : 'itens'}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 max-h-[60vh] overflow-y-auto">
        {items.map((item) => (
          <div
            key={item.produto_id}
            className="p-4 border rounded-lg bg-gray-50 dark:bg-gray-800 space-y-3"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-sm">{item.nome}</p>
                <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                  <span>Estoque: {item.estoque_disponivel}</span>
                  {item.preco_original !== item.preco_unitario_editavel && (
                    <span className="text-orange-600">
                      Preço original: R$ {item.preco_original.toFixed(2)}
                    </span>
                  )}
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onRemoveItem(item.produto_id)}
                className="text-red-500 hover:text-red-700 hover:bg-red-50"
              >
                <Trash2 size={16} />
              </Button>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block">
                  Quantidade
                </label>
                <Input
                  type="number"
                  min="1"
                  value={item.quantidade}
                  onChange={(e) =>
                    onUpdateItem(item.produto_id, 'quantidade', parseInt(e.target.value) || 1)
                  }
                  className="text-sm"
                />
                {item.quantidade > item.estoque_disponivel && (
                  <p className="text-xs text-orange-500 mt-1">
                    Estoque insuficiente
                  </p>
                )}
              </div>
              <div>
                <label className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block">
                  Preço Unit. (R$)
                </label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={item.preco_unitario_editavel}
                  onChange={(e) =>
                    onUpdateItem(
                      item.produto_id,
                      'preco',
                      parseFloat(e.target.value) || 0
                    )
                  }
                  className="text-sm"
                />
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t">
              <span className="text-xs text-gray-500">Subtotal:</span>
              <span className="font-semibold text-blue-600">
                R$ {(item.preco_unitario_editavel * item.quantidade).toFixed(2)}
              </span>
            </div>
          </div>
        ))}
      </CardContent>

      <div className="border-t p-4 bg-gray-50 dark:bg-gray-800">
        <div className="flex items-center justify-between">
          <span className="text-lg font-semibold">Total:</span>
          <span className="text-2xl font-bold text-blue-600">
            R$ {total.toFixed(2)}
          </span>
        </div>
      </div>
    </Card>
  );
}

