'use client';

import { useEffect, useState } from 'react';
import { useSugestoesOrcamento, SugestaoProduto } from '@/hooks/useSugestoesOrcamento';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Sparkles, TrendingUp, DollarSign, ShoppingBag } from 'lucide-react';

interface SugestoesClienteProps {
  clienteId: number | null;
  onAplicarSugestao: (produtoId: number, preco: number, quantidade: number) => void;
}

export function SugestoesCliente({ clienteId, onAplicarSugestao }: SugestoesClienteProps) {
  const { obterSugestoesCliente, loading } = useSugestoesOrcamento();
  const [sugestoes, setSugestoes] = useState<SugestaoProduto[]>([]);

  useEffect(() => {
    if (clienteId) {
      obterSugestoesCliente(clienteId).then((data) => {
        if (data) {
          setSugestoes(data.sugestoes);
        }
      });
    } else {
      setSugestoes([]);
    }
  }, [clienteId, obterSugestoesCliente]);

  if (!clienteId || sugestoes.length === 0) {
    return null;
  }

  return (
    <Card className="mb-4 border-blue-200 bg-blue-50/30">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Sparkles size={16} className="text-blue-500" />
          Histórico de Compras do Cliente
          <Badge variant="secondary" className="ml-2">
            {sugestoes.length} {sugestoes.length === 1 ? 'produto' : 'produtos'}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-sm text-gray-500">Carregando sugestões...</p>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {sugestoes.map((sugestao) => {
              const precoAplicar = sugestao.preco_cliente?.ultimo || sugestao.preco_sistema;
              const quantidadeAplicar = sugestao.quantidade_sugerida || 1;
              
              return (
                <div
                  key={sugestao.produto_id}
                  className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium">
                      {sugestao.produto_nome || `Produto #${sugestao.produto_id}`}
                    </p>
                    <div className="flex flex-wrap items-center gap-3 mt-1 text-xs">
                      {/* Preço do sistema */}
                      <span className="text-gray-500 flex items-center gap-1">
                        <DollarSign size={10} />
                        Sistema: R$ {sugestao.preco_sistema.toFixed(2)}
                      </span>
                      
                      {/* Range de preços do cliente */}
                      {sugestao.preco_cliente && (
                        <span className="text-blue-600 font-medium">
                          Cliente: R$ {sugestao.preco_cliente.minimo?.toFixed(2)} - R$ {sugestao.preco_cliente.maximo?.toFixed(2)}
                        </span>
                      )}
                      
                      {/* Total de vendas */}
                      {sugestao.total_vendas > 0 && (
                        <span className="text-gray-400 flex items-center gap-1">
                          <ShoppingBag size={10} />
                          {sugestao.total_vendas}x vendido
                        </span>
                      )}
                      
                      {/* Quantidade sugerida */}
                      {sugestao.quantidade_sugerida && (
                        <span className="text-green-600 flex items-center gap-1">
                          <TrendingUp size={10} />
                          Qtd média: {sugestao.quantidade_sugerida}
                        </span>
                      )}
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    className="ml-2"
                    onClick={() =>
                      onAplicarSugestao(
                        sugestao.produto_id,
                        precoAplicar,
                        Math.round(quantidadeAplicar)
                      )
                    }
                  >
                    Adicionar
                  </Button>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

