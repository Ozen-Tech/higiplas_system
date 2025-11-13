'use client';

import { useEffect, useState } from 'react';
import { useSugestoesOrcamento, SugestaoProduto } from '@/hooks/useSugestoesOrcamento';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Sparkles, TrendingUp } from 'lucide-react';

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
    <Card className="mb-4">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Sparkles size={16} className="text-blue-500" />
          Sugestões Inteligentes
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
            {sugestoes.map((sugestao) => (
              <div
                key={sugestao.produto_id}
                className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded-lg"
              >
                <div className="flex-1">
                  <p className="text-sm font-medium">Produto #{sugestao.produto_id}</p>
                  <div className="flex items-center gap-4 mt-1 text-xs text-gray-600 dark:text-gray-400">
                    {sugestao.ultimo_preco && (
                      <span>Último preço: R$ {sugestao.ultimo_preco.toFixed(2)}</span>
                    )}
                    {sugestao.quantidade_sugerida && (
                      <span className="flex items-center gap-1">
                        <TrendingUp size={12} />
                        Qtd sugerida: {sugestao.quantidade_sugerida}
                      </span>
                    )}
                  </div>
                </div>
                {sugestao.ultimo_preco && sugestao.quantidade_sugerida && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      onAplicarSugestao(
                        sugestao.produto_id,
                        sugestao.ultimo_preco!,
                        Math.round(sugestao.quantidade_sugerida!)
                      )
                    }
                  >
                    Aplicar
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

