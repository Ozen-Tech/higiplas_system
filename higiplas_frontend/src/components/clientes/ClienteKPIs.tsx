'use client';

import { useEffect, useState } from 'react';
import { useClienteKPIs, ClienteKPIs } from '@/hooks/useClienteKPIs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, ShoppingBag, Calendar, Package } from 'lucide-react';

interface ClienteKPIsProps {
  clienteId: number;
}

export function ClienteKPIsComponent({ clienteId }: ClienteKPIsProps) {
  const { fetchKPIs, loading } = useClienteKPIs();
  const [kpis, setKpis] = useState<ClienteKPIs | null>(null);

  useEffect(() => {
    if (clienteId) {
      fetchKPIs(clienteId).then(setKpis);
    }
  }, [clienteId, fetchKPIs]);

  if (loading) {
    return <div className="text-sm text-gray-500">Carregando KPIs...</div>;
  }

  if (!kpis) {
    return null;
  }

  return (
    <div className="space-y-4 mt-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">KPIs do Cliente</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp size={16} className="text-blue-600" />
                <span className="text-xs text-gray-600 dark:text-gray-400">Total Vendido</span>
              </div>
              <p className="text-lg font-bold text-blue-600">
                R$ {kpis.total_vendido.toFixed(2)}
              </p>
            </div>

            <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <ShoppingBag size={16} className="text-green-600" />
                <span className="text-xs text-gray-600 dark:text-gray-400">Pedidos</span>
              </div>
              <p className="text-lg font-bold text-green-600">{kpis.numero_pedidos}</p>
            </div>

            {kpis.ticket_medio && (
              <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <Package size={16} className="text-purple-600" />
                  <span className="text-xs text-gray-600 dark:text-gray-400">Ticket Médio</span>
                </div>
                <p className="text-lg font-bold text-purple-600">
                  R$ {kpis.ticket_medio.toFixed(2)}
                </p>
              </div>
            )}

            {kpis.frequencia_compras_dias && (
              <div className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <Calendar size={16} className="text-orange-600" />
                  <span className="text-xs text-gray-600 dark:text-gray-400">Frequência</span>
                </div>
                <p className="text-lg font-bold text-orange-600">
                  {kpis.frequencia_compras_dias.toFixed(0)} dias
                </p>
              </div>
            )}
          </div>

          {kpis.produtos_mais_comprados.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold mb-2">Produtos Mais Comprados</h4>
              <div className="space-y-2">
                {kpis.produtos_mais_comprados.slice(0, 5).map((produto) => (
                  <div
                    key={produto.produto_id}
                    className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded"
                  >
                    <div>
                      <p className="text-sm font-medium">{produto.produto_nome}</p>
                      <p className="text-xs text-gray-500">
                        {produto.numero_pedidos} {produto.numero_pedidos === 1 ? 'pedido' : 'pedidos'}
                      </p>
                    </div>
                    <Badge variant="secondary">
                      {produto.quantidade_total} un
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

