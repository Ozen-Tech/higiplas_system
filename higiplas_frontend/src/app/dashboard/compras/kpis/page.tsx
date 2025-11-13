'use client';

import { useState, useEffect } from 'react';
import { Header } from '@/components/dashboard/Header';
import { useComprasKPIs, ComprasKPIs } from '@/hooks/useComprasKPIs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { BarChart3, AlertTriangle, Package } from 'lucide-react';

export default function ComprasKPIsPage() {
  const { fetchKPIs, loading } = useComprasKPIs();
  const [kpis, setKpis] = useState<ComprasKPIs | null>(null);
  const [periodoMeses, setPeriodoMeses] = useState(12);

  useEffect(() => {
    fetchKPIs(periodoMeses).then(setKpis);
  }, [periodoMeses, fetchKPIs]);

  return (
    <>
      <Header>
        <div className="flex items-center justify-between w-full">
          <h1 className="text-xl font-bold">KPIs de Compras</h1>
          <Select value={periodoMeses.toString()} onValueChange={(v) => setPeriodoMeses(parseInt(v))}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="3">Últimos 3 meses</SelectItem>
              <SelectItem value="6">Últimos 6 meses</SelectItem>
              <SelectItem value="12">Últimos 12 meses</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </Header>
      <main className="flex-1 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {loading ? (
            <div className="text-center py-12">
              <p className="text-gray-500">Carregando KPIs...</p>
            </div>
          ) : kpis ? (
            <>
              {/* Cards de Resumo */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <BarChart3 size={16} />
                      Eficiência de Compras
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Taxa de Acerto</span>
                        <span className="font-bold">
                          {kpis.eficiencia_compras?.taxa_acerto_percentual?.toFixed(1) || 0}%
                        </span>
                      </div>
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>Comprados: {kpis.eficiencia_compras?.produtos_comprados || 0}</span>
                        <span>Vendidos: {kpis.eficiencia_compras?.produtos_vendidos || 0}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <AlertTriangle size={16} />
                      Estoque Parado
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Custo Total</span>
                        <span className="font-bold text-red-600">
                          R$ {kpis.estoque_parado?.custo_total_parado?.toFixed(2) || '0.00'}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500">
                        {kpis.estoque_parado?.total_produtos_parados || 0} produtos parados
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <Package size={16} />
                      Classificação ABC
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Produtos Classe A</span>
                        <Badge variant="default">
                          {kpis.abc_curva?.filter(p => p.classificacao === 'A').length || 0}
                        </Badge>
                      </div>
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>Total analisado: {kpis.abc_curva?.length || 0}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Tabela ABC */}
              {kpis.abc_curva && kpis.abc_curva.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Classificação ABC de Produtos</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Produto</TableHead>
                            <TableHead>Código</TableHead>
                            <TableHead>Classificação</TableHead>
                            <TableHead className="text-right">% Vendas</TableHead>
                            <TableHead className="text-right">% Estoque</TableHead>
                            <TableHead className="text-right">Valor Total</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {kpis.abc_curva.map((produto) => (
                            <TableRow key={produto.produto_id}>
                              <TableCell className="font-medium">{produto.produto_nome}</TableCell>
                              <TableCell>{produto.produto_codigo || 'N/A'}</TableCell>
                              <TableCell>
                                <Badge
                                  variant={
                                    produto.classificacao === 'A'
                                      ? 'default'
                                      : produto.classificacao === 'B'
                                      ? 'secondary'
                                      : 'outline'
                                  }
                                >
                                  {produto.classificacao}
                                </Badge>
                              </TableCell>
                              <TableCell className="text-right">
                                {produto.percentual_vendas.toFixed(2)}%
                              </TableCell>
                              <TableCell className="text-right">
                                {produto.percentual_estoque.toFixed(2)}%
                              </TableCell>
                              <TableCell className="text-right">
                                R$ {produto.valor_total_vendas.toFixed(2)}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Produtos Parados */}
              {kpis.estoque_parado && kpis.estoque_parado.produtos_parados.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Produtos Parados (Top 20)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Produto</TableHead>
                            <TableHead>Código</TableHead>
                            <TableHead className="text-right">Quantidade</TableHead>
                            <TableHead className="text-right">Custo Total</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {kpis.estoque_parado.produtos_parados.map((produto) => (
                            <TableRow key={produto.produto_id}>
                              <TableCell className="font-medium">{produto.produto_nome}</TableCell>
                              <TableCell>{produto.produto_codigo || 'N/A'}</TableCell>
                              <TableCell className="text-right">{produto.quantidade_estoque}</TableCell>
                              <TableCell className="text-right text-red-600">
                                R$ {produto.custo_total.toFixed(2)}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="p-6 text-center">
                <p className="text-gray-500">Nenhum dado disponível para o período selecionado.</p>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </>
  );
}

