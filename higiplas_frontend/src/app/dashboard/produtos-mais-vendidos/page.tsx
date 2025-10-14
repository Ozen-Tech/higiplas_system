'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  ArrowTrendingUpIcon,
  CurrencyDollarIcon,
  ShoppingBagIcon,
  ChartBarIcon,
  CalendarIcon,
  UserGroupIcon,
  ExclamationTriangleIcon,
  FunnelIcon,
  ArrowPathIcon,
  TrophyIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';

// Interfaces atualizadas
interface ProdutoMaisVendido {
  produto_id: number;
  nome: string;
  codigo: string;
  categoria: string;
  preco_atual: number;
  estoque_atual: number;
  total_quantidade_vendida: number;
  valor_total_vendido: number;
  numero_vendas: number;
  quantidade_media_por_venda: number;
  frequencia_vendas_por_dia: number;
  primeira_venda: string;
  ultima_venda: string;
  dias_desde_ultima_venda: number;
  ticket_medio: number;
  rotatividade_estoque: number;
  status_estoque: string;
}

interface EstatisticasGerais {
  total_produtos_analisados: number;
  periodo_analise_dias: number;
  data_inicio: string;
  data_fim: string;
  total_quantidade_vendida: number;
  total_valor_vendido: number;
  ticket_medio: number;
  produto_mais_vendido: string | null;
  categoria_mais_vendida: string | null;
}

interface FiltrosAplicados {
  periodo_dias?: number;
  data_inicio?: string;
  data_fim?: string;
  limite?: number;
  ordenar_por?: string;
  vendedor_id?: number | null;
  categoria?: string;
  produto_id?: number;
}

interface ApiResponse {
  produtos: ProdutoMaisVendido[];
  estatisticas: EstatisticasGerais;
  filtros_aplicados: FiltrosAplicados;
}

interface TendenciaMensal {
  mes_ano: string;
  produto_nome: string;
  quantidade_vendida: number;
  valor_vendido: number;
}

interface ComparativoVendedor {
  vendedor_id: number;
  vendedor_nome: string;
  total_quantidade_vendida: number;
  total_valor_vendido: number;
  produtos_diferentes_vendidos: number;
  numero_vendas: number;
  ticket_medio: number;
}

export default function ProdutosMaisVendidos() {
  // Estados principais
  const [dados, setDados] = useState<ApiResponse | null>(null);
  const [tendencias, setTendencias] = useState<TendenciaMensal[]>([]);
  const [comparativoVendedores, setComparativoVendedores] = useState<ComparativoVendedor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Estados de filtros
  const [filtros, setFiltros] = useState({
    periodo_dias: 365,
    data_inicio: '',
    data_fim: '',
    limite: 50,
    ordenar_por: 'quantidade',
    vendedor_id: null as number | null
  });

  // Estados de visualização
  const [mostrarFiltros, setMostrarFiltros] = useState(false);

  const fetchDados = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      
      if (!token) {
        throw new Error('Token não encontrado');
      }

      // Construir parâmetros da query
      const params = new URLSearchParams();
      if (filtros.periodo_dias) params.append('periodo_dias', filtros.periodo_dias.toString());
      if (filtros.data_inicio) params.append('data_inicio', filtros.data_inicio);
      if (filtros.data_fim) params.append('data_fim', filtros.data_fim);
      if (filtros.limite) params.append('limite', filtros.limite.toString());
      if (filtros.ordenar_por) params.append('ordenar_por', filtros.ordenar_por);
      if (filtros.vendedor_id) params.append('vendedor_id', filtros.vendedor_id.toString());

      // Buscar produtos mais vendidos
      const responseProdutos = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/produtos-mais-vendidos/?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!responseProdutos.ok) {
        throw new Error('Erro ao buscar produtos mais vendidos');
      }

      const dadosProdutos = await responseProdutos.json();
      setDados(dadosProdutos);

      // Buscar tendências
      const responseTendencias = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/produtos-mais-vendidos/tendencias?periodo_meses=6`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (responseTendencias.ok) {
        const dadosTendencias = await responseTendencias.json();
        setTendencias(dadosTendencias.tendencias || []);
      }

      // Buscar comparativo de vendedores
      const responseVendedores = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/produtos-mais-vendidos/comparativo-vendedores?periodo_dias=30`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (responseVendedores.ok) {
        const dadosVendedores = await responseVendedores.json();
        setComparativoVendedores(dadosVendedores || []);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }, [filtros]);

  useEffect(() => {
    fetchDados();
  }, [fetchDados]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('pt-BR').format(value);
  };

  const getStatusVariant = (status: string): "default" | "secondary" | "destructive" | "outline" | "success" | "warning" | "info" => {
    switch (status) {
      case 'ALTA_ROTACAO': return 'success';
      case 'MEDIA_ROTACAO': return 'info';
      case 'BAIXA_ROTACAO': return 'warning';
      case 'PARADO': return 'destructive';
      default: return 'secondary';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'ALTA_ROTACAO': return 'Alta Rotação';
      case 'MEDIA_ROTACAO': return 'Média Rotação';
      case 'BAIXA_ROTACAO': return 'Baixa Rotação';
      case 'PARADO': return 'Parado';
      default: return 'Indefinido';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
        <Card className="w-64">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
              <p className="text-sm text-muted-foreground">Carregando dados de vendas...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
        <Card className="w-96">
          <CardHeader>
            <div className="flex items-center justify-center mb-4">
              <ExclamationTriangleIcon className="h-12 w-12 text-destructive" />
            </div>
            <CardTitle className="text-center">Erro ao carregar dados</CardTitle>
            <CardDescription className="text-center">{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={fetchDados} className="w-full">
              <ArrowPathIcon className="h-4 w-4 mr-2" />
              Tentar novamente
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!dados) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-primary to-blue-600 rounded-xl shadow-lg">
                <TrophyIcon className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent flex items-center">
                  Produtos Mais Vendidos
                </h1>
                <p className="mt-1 text-sm text-muted-foreground">
                  Análise de {formatNumber(dados.estatisticas.total_produtos_analisados)} produtos
                  nos últimos {dados.estatisticas.periodo_analise_dias} dias
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                onClick={() => setMostrarFiltros(!mostrarFiltros)}
              >
                <FunnelIcon className="h-4 w-4 mr-2" />
                Filtros
              </Button>
              <Button onClick={fetchDados}>
                <ArrowPathIcon className="h-4 w-4 mr-2" />
                Atualizar
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Filtros Expandidos */}
        {mostrarFiltros && (
          <Card>
            <CardHeader>
              <CardTitle>Filtros de Análise</CardTitle>
              <CardDescription>Personalize a análise de produtos mais vendidos</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="periodo">Período (dias)</Label>
                  <Select
                    value={filtros.periodo_dias.toString()}
                    onValueChange={(value) => setFiltros({...filtros, periodo_dias: parseInt(value)})}
                  >
                    <SelectTrigger id="periodo">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="30">30 dias</SelectItem>
                      <SelectItem value="90">90 dias</SelectItem>
                      <SelectItem value="180">6 meses</SelectItem>
                      <SelectItem value="365">1 ano</SelectItem>
                      <SelectItem value="730">2 anos</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ordenar">Ordenar por</Label>
                  <Select
                    value={filtros.ordenar_por}
                    onValueChange={(value) => setFiltros({...filtros, ordenar_por: value})}
                  >
                    <SelectTrigger id="ordenar">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="quantidade">Quantidade</SelectItem>
                      <SelectItem value="valor">Valor Total</SelectItem>
                      <SelectItem value="frequencia">Frequência</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="limite">Limite</Label>
                  <Select
                    value={filtros.limite.toString()}
                    onValueChange={(value) => setFiltros({...filtros, limite: parseInt(value)})}
                  >
                    <SelectTrigger id="limite">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="10">10 produtos</SelectItem>
                      <SelectItem value="25">25 produtos</SelectItem>
                      <SelectItem value="50">50 produtos</SelectItem>
                      <SelectItem value="100">100 produtos</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="data-inicio">Data Início</Label>
                  <Input
                    id="data-inicio"
                    type="date"
                    value={filtros.data_inicio}
                    onChange={(e) => setFiltros({...filtros, data_inicio: e.target.value})}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="data-fim">Data Fim</Label>
                  <Input
                    id="data-fim"
                    type="date"
                    value={filtros.data_fim}
                    onChange={(e) => setFiltros({...filtros, data_fim: e.target.value})}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Cards de Métricas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="hover:shadow-lg transition-shadow duration-300">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Vendido</p>
                  <p className="text-3xl font-bold mt-2">
                    {formatNumber(dados.estatisticas.total_quantidade_vendida)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">unidades</p>
                </div>
                <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
                  <ShoppingBagIcon className="h-8 w-8 text-blue-600 dark:text-blue-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow duration-300">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Valor Total</p>
                  <p className="text-3xl font-bold mt-2">
                    {formatCurrency(dados.estatisticas.total_valor_vendido)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">em vendas</p>
                </div>
                <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl">
                  <CurrencyDollarIcon className="h-8 w-8 text-green-600 dark:text-green-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow duration-300">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Ticket Médio</p>
                  <p className="text-3xl font-bold mt-2">
                    {formatCurrency(dados.estatisticas.ticket_medio)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">por venda</p>
                </div>
                <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-xl">
                  <ChartBarIcon className="h-8 w-8 text-purple-600 dark:text-purple-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow duration-300">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Produtos Ativos</p>
                  <p className="text-3xl font-bold mt-2">
                    {dados.estatisticas.total_produtos_analisados}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">com vendas</p>
                </div>
                <div className="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-xl">
                  <SparklesIcon className="h-8 w-8 text-orange-600 dark:text-orange-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Abas de Navegação */}
        <Card>
          <Tabs defaultValue="produtos" className="w-full">
            <CardHeader className="pb-3">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="produtos">
                  Ranking de Produtos
                </TabsTrigger>
                <TabsTrigger value="tendencias">
                  Tendências
                </TabsTrigger>
                <TabsTrigger value="vendedores">
                  Performance Vendedores
                </TabsTrigger>
              </TabsList>
            </CardHeader>

            <CardContent>
                <TabsContent value="produtos" className="mt-0">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-1">
                      Top {dados.produtos.length} Produtos Mais Vendidos
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Ordenado por {filtros.ordenar_por === 'quantidade' ? 'quantidade vendida' :
                                   filtros.ordenar_por === 'valor' ? 'valor total' : 'frequência de vendas'}
                    </p>
                  </div>

                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-[50px]">#</TableHead>
                          <TableHead>Produto</TableHead>
                          <TableHead>Categoria</TableHead>
                          <TableHead className="text-right">Qtd. Vendida</TableHead>
                          <TableHead className="text-right">Valor Total</TableHead>
                          <TableHead className="text-right">Nº Vendas</TableHead>
                          <TableHead className="text-right">Ticket Médio</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead className="text-right">Estoque</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {dados.produtos.map((produto, index) => (
                          <TableRow key={produto.produto_id}>
                            <TableCell>
                              <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold ${
                                index === 0 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' :
                                index === 1 ? 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300' :
                                index === 2 ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400' :
                                'bg-muted text-muted-foreground'
                              }`}>
                                {index + 1}
                              </div>
                            </TableCell>
                            <TableCell>
                              <div>
                                <div className="font-medium">{produto.nome}</div>
                                <div className="text-sm text-muted-foreground">{produto.codigo}</div>
                              </div>
                            </TableCell>
                            <TableCell>
                              <Badge variant="outline">{produto.categoria}</Badge>
                            </TableCell>
                            <TableCell className="text-right font-medium">
                              {formatNumber(produto.total_quantidade_vendida)}
                            </TableCell>
                            <TableCell className="text-right font-medium">
                              {formatCurrency(produto.valor_total_vendido)}
                            </TableCell>
                            <TableCell className="text-right">
                              {produto.numero_vendas}
                            </TableCell>
                            <TableCell className="text-right">
                              {formatCurrency(produto.ticket_medio)}
                            </TableCell>
                            <TableCell>
                              <Badge variant={getStatusVariant(produto.status_estoque)}>
                                {getStatusText(produto.status_estoque)}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-right">
                              <span className={produto.estoque_atual < 10 ? 'text-destructive font-medium' : ''}>
                                {formatNumber(produto.estoque_atual)}
                              </span>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="tendencias" className="mt-0">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-1">
                      Tendências de Vendas (Últimos 6 Meses)
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Evolução das vendas por mês para análise de sazonalidade
                    </p>
                  </div>

                  {tendencias.length > 0 ? (
                    <div className="h-96 p-4 bg-muted/30 rounded-lg">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={tendencias}>
                          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                          <XAxis
                            dataKey="mes_ano"
                            className="text-xs"
                          />
                          <YAxis className="text-xs" />
                          <Tooltip
                            formatter={(value, name) => [
                              name === 'quantidade_vendida' ? formatNumber(value as number) : formatCurrency(value as number),
                              name === 'quantidade_vendida' ? 'Quantidade' : 'Valor'
                            ]}
                            contentStyle={{
                              backgroundColor: 'hsl(var(--background))',
                              border: '1px solid hsl(var(--border))',
                              borderRadius: '0.5rem'
                            }}
                          />
                          <Line
                            type="monotone"
                            dataKey="quantidade_vendida"
                            stroke="hsl(var(--primary))"
                            strokeWidth={3}
                            name="quantidade_vendida"
                            dot={{ fill: 'hsl(var(--primary))', r: 4 }}
                          />
                          <Line
                            type="monotone"
                            dataKey="valor_vendido"
                            stroke="hsl(142, 76%, 36%)"
                            strokeWidth={3}
                            name="valor_vendido"
                            dot={{ fill: 'hsl(142, 76%, 36%)', r: 4 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <ChartBarIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground">Nenhum dado de tendência disponível</p>
                    </div>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="vendedores" className="mt-0">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-1">
                      Performance dos Vendedores (Últimos 30 Dias)
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Comparativo de vendas entre vendedores
                    </p>
                  </div>

                  {comparativoVendedores.length > 0 ? (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {/* Tabela de Vendedores */}
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base">Ranking de Vendedores</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="rounded-md border">
                            <Table>
                              <TableHeader>
                                <TableRow>
                                  <TableHead>Vendedor</TableHead>
                                  <TableHead className="text-right">Valor Total</TableHead>
                                  <TableHead className="text-right">Vendas</TableHead>
                                  <TableHead className="text-right">Ticket Médio</TableHead>
                                </TableRow>
                              </TableHeader>
                              <TableBody>
                                {comparativoVendedores.map((vendedor, index) => (
                                  <TableRow key={vendedor.vendedor_id}>
                                    <TableCell>
                                      <div className="flex items-center gap-3">
                                        <div className={`flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold ${
                                          index === 0 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' :
                                          index === 1 ? 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300' :
                                          index === 2 ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400' :
                                          'bg-muted text-muted-foreground'
                                        }`}>
                                          {index + 1}
                                        </div>
                                        <span className="font-medium">
                                          {vendedor.vendedor_nome}
                                        </span>
                                      </div>
                                    </TableCell>
                                    <TableCell className="text-right font-medium">
                                      {formatCurrency(vendedor.total_valor_vendido)}
                                    </TableCell>
                                    <TableCell className="text-right">
                                      {vendedor.numero_vendas}
                                    </TableCell>
                                    <TableCell className="text-right">
                                      {formatCurrency(vendedor.ticket_medio)}
                                    </TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </div>
                        </CardContent>
                      </Card>

                      {/* Gráfico de Vendedores */}
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base">Distribuição de Vendas</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                              <BarChart data={comparativoVendedores.slice(0, 8)}>
                                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                                <XAxis
                                  dataKey="vendedor_nome"
                                  angle={-45}
                                  textAnchor="end"
                                  height={80}
                                  className="text-xs"
                                />
                                <YAxis className="text-xs" />
                                <Tooltip
                                  formatter={(value) => formatCurrency(value as number)}
                                  contentStyle={{
                                    backgroundColor: 'hsl(var(--background))',
                                    border: '1px solid hsl(var(--border))',
                                    borderRadius: '0.5rem'
                                  }}
                                />
                                <Bar
                                  dataKey="total_valor_vendido"
                                  fill="hsl(var(--primary))"
                                  radius={[8, 8, 0, 0]}
                                />
                              </BarChart>
                            </ResponsiveContainer>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <UserGroupIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground">Nenhum dado de vendedor disponível</p>
                    </div>
                  )}
                </div>
              </TabsContent>
            </CardContent>
          </Tabs>
        </Card>

        {/* Informações Adicionais */}
        <Card>
          <CardHeader>
            <CardTitle>Informações do Período</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <CalendarIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Período Analisado</p>
                  <p className="text-sm font-medium">
                    {new Date(dados.estatisticas.data_inicio).toLocaleDateString('pt-BR')} até{' '}
                    {new Date(dados.estatisticas.data_fim).toLocaleDateString('pt-BR')}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                  <ArrowTrendingUpIcon className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Produto Mais Vendido</p>
                  <p className="text-sm font-medium">
                    {dados.estatisticas.produto_mais_vendido || 'N/A'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <ShoppingBagIcon className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Categoria Mais Vendida</p>
                  <p className="text-sm font-medium">
                    {dados.estatisticas.categoria_mais_vendida || 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}