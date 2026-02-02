"use client";

import { useState, useEffect, useCallback } from 'react';
import { Header } from '@/components/dashboard/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { apiService } from '@/services/apiService';
import { AlertTriangle, Search } from 'lucide-react';
import toast from 'react-hot-toast';

interface ClienteSugestao {
  cliente_id: number;
  cliente_nome: string;
  cnpj: string;
  periodo_analise_dias: number;
  total_produtos_unicos: number;
  sugestoes: SugestaoItem[];
}

interface SugestaoItem {
  produto_id: number;
  produto_nome: string;
  codigo: string;
  cliente_compra_frequente: boolean;
  quantidade_media_compra: number;
  frequencia_compras_dias: number | null;
  ultima_compra: string | null;
  dias_desde_ultima_compra: number | null;
  dias_ate_proxima_compra_esperada: number | null;
  num_compras_periodo: number;
  estoque_atual: number;
  quantidade_sugerida: number;
  preco_custo: number | null;
  preco_medio_cliente: number;
  valor_estimado: number;
  prioridade: 'ALTA' | 'MEDIA' | 'BAIXA';
  precisa_comprar: boolean;
}

interface ClienteVisaoGeral {
  cliente_id: number;
  cliente_nome: string;
  cnpj: string;
  total_notas: number;
  produtos_unicos: number;
  ultima_compra: string | null;
  valor_total_compras: number;
}

interface SugestaoGlobal {
  produto_id: number;
  produto_nome: string;
  codigo: string;
  num_clientes_compram: number;
  quantidade_sugerida: number;
  estoque_atual: number;
  valor_estimado: number;
  prioridade: 'ALTA' | 'MEDIA' | 'BAIXA';
}

export default function SugestoesCompraPage() {
  const [loading, setLoading] = useState(true);
  const [clientesSugestoes, setClientesSugestoes] = useState<ClienteSugestao[]>([]);
  const [sugestoesGlobais, setSugestoesGlobais] = useState<SugestaoGlobal[]>([]);
  const [activeTab, setActiveTab] = useState<'clientes' | 'global'>('clientes');
  const [searchTerm, setSearchTerm] = useState('');
  const [diasAnalise, setDiasAnalise] = useState(90);
  const [selectedCliente, setSelectedCliente] = useState<number | null>(null);

  const fetchSugestoes = useCallback(async () => {
    setLoading(true);
    try {
      // Buscar visão geral de clientes
      const visaoGeralResponse = await apiService.get(`/clientes/todos/visao-geral?dias=${diasAnalise}`);
      const clientes = visaoGeralResponse?.data?.clientes || [];

      // Buscar sugestões para cada cliente que tem compras
      const sugestoesPromises = clientes.map(async (cliente: ClienteVisaoGeral) => {
        try {
          const response = await apiService.get(
            `/clientes/${cliente.cliente_id}/sugestoes-compra?dias_analise=${diasAnalise}`
          );
          return response?.data;
        } catch (error) {
          console.error(`Erro ao buscar sugestões para cliente ${cliente.cliente_id}:`, error);
          return null;
        }
      });

      const sugestoesResults = await Promise.all(sugestoesPromises);
      const sugestoesValidas = sugestoesResults.filter(
        (s) => s && s.sugestoes && s.sugestoes.length > 0
      ) as ClienteSugestao[];

      setClientesSugestoes(sugestoesValidas);

      // Buscar sugestões globais
      try {
        const globalResponse = await apiService.get(
          `/compras/sugestoes/baseado-clientes?dias_analise=${diasAnalise}`
        );
        setSugestoesGlobais(globalResponse?.data?.sugestoes || []);
      } catch {
        // Ignorar erro de sugestões globais
      }
    } catch (error) {
      console.error('Erro ao buscar sugestões:', error);
      toast.error('Erro ao carregar sugestões de compra');
    } finally {
      setLoading(false);
    }
  }, [diasAnalise]);

  useEffect(() => {
    fetchSugestoes();
  }, [fetchSugestoes]);

  const clientesFiltrados = clientesSugestoes.filter((cliente) => {
    if (selectedCliente && cliente.cliente_id !== selectedCliente) return false;
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      cliente.cliente_nome.toLowerCase().includes(term) ||
      cliente.cnpj?.toLowerCase().includes(term) ||
      cliente.sugestoes.some((s) => s.produto_nome.toLowerCase().includes(term))
    );
  });

  const getPrioridadeColor = (prioridade: string) => {
    switch (prioridade) {
      case 'ALTA':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'MEDIA':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
    }
  };

  const totalSugestoes = clientesSugestoes.reduce(
    (acc, cliente) => acc + cliente.sugestoes.filter((s) => s.precisa_comprar).length,
    0
  );

  const valorTotalEstimado = clientesSugestoes.reduce((acc, cliente) => {
    return (
      acc +
      cliente.sugestoes
        .filter((s) => s.precisa_comprar)
        .reduce((sum, s) => sum + s.valor_estimado, 0)
    );
  }, 0);

  return (
    <>
      <Header>
        <h1 className="text-xl font-bold">Sugestões de Compra</h1>
      </Header>
      <main className="flex-1 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Filtros e Estatísticas */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total de Sugestões
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{totalSugestoes}</div>
                <p className="text-xs text-gray-500 mt-1">Produtos a comprar</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Valor Estimado
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  R$ {valorTotalEstimado.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </div>
                <p className="text-xs text-gray-500 mt-1">Investimento necessário</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Clientes Ativos
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{clientesSugestoes.length}</div>
                <p className="text-xs text-gray-500 mt-1">Com padrões identificados</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Período de Análise
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Select value={diasAnalise.toString()} onValueChange={(v) => setDiasAnalise(Number(v))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="30">30 dias</SelectItem>
                    <SelectItem value="60">60 dias</SelectItem>
                    <SelectItem value="90">90 dias</SelectItem>
                    <SelectItem value="180">180 dias</SelectItem>
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('clientes')}
                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'clientes'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Por Cliente ({clientesSugestoes.length})
              </button>
              <button
                onClick={() => setActiveTab('global')}
                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'global'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Visão Global ({sugestoesGlobais.length})
              </button>
            </nav>
          </div>

          {/* Filtros de Busca */}
          <Card>
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                  <Input
                    placeholder="Buscar por cliente, CNPJ ou produto..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select
                  value={selectedCliente?.toString() || 'all'}
                  onValueChange={(v) => setSelectedCliente(v === 'all' ? null : Number(v))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Filtrar por cliente" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos os clientes</SelectItem>
                    {clientesSugestoes.map((cliente) => (
                      <SelectItem key={cliente.cliente_id} value={cliente.cliente_id.toString()}>
                        {cliente.cliente_nome}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Conteúdo das Tabs */}
          {loading ? (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-gray-500">Carregando sugestões...</p>
              </CardContent>
            </Card>
          ) : activeTab === 'clientes' ? (
            <div className="space-y-4">
              {clientesFiltrados.length === 0 ? (
                <Card>
                  <CardContent className="py-12 text-center">
                    <p className="text-gray-500">Nenhuma sugestão encontrada para os filtros selecionados.</p>
                  </CardContent>
                </Card>
              ) : (
                clientesFiltrados.map((cliente) => (
                  <Card key={cliente.cliente_id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="text-lg">{cliente.cliente_nome}</CardTitle>
                          <p className="text-sm text-gray-500 mt-1">CNPJ: {cliente.cnpj}</p>
                        </div>
                        <Badge variant="outline">
                          {cliente.sugestoes.filter((s) => s.precisa_comprar).length} sugestões
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {cliente.sugestoes
                          .filter((s) => s.precisa_comprar || searchTerm)
                          .map((sugestao) => (
                            <div
                              key={sugestao.produto_id}
                              className="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2">
                                    <h4 className="font-semibold">{sugestao.produto_nome}</h4>
                                    <Badge className={getPrioridadeColor(sugestao.prioridade)}>
                                      {sugestao.prioridade}
                                    </Badge>
                                    {sugestao.cliente_compra_frequente && (
                                      <Badge variant="outline" className="text-xs">
                                        Cliente frequente
                                      </Badge>
                                    )}
                                  </div>
                                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 dark:text-gray-400">
                                    <div>
                                      <span className="font-medium">Quantidade sugerida:</span>{' '}
                                      {sugestao.quantidade_sugerida} un
                                    </div>
                                    <div>
                                      <span className="font-medium">Estoque atual:</span>{' '}
                                      {sugestao.estoque_atual} un
                                    </div>
                                    <div>
                                      <span className="font-medium">Última compra:</span>{' '}
                                      {sugestao.dias_desde_ultima_compra !== null
                                        ? `${sugestao.dias_desde_ultima_compra} dias atrás`
                                        : 'N/A'}
                                    </div>
                                    <div>
                                      <span className="font-medium">Valor estimado:</span>{' '}
                                      R$ {sugestao.valor_estimado.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                    </div>
                                  </div>
                                  {sugestao.dias_ate_proxima_compra_esperada !== null &&
                                    sugestao.dias_ate_proxima_compra_esperada <= 7 && (
                                      <div className="mt-2 flex items-center gap-2 text-sm text-orange-600 dark:text-orange-400">
                                        <AlertTriangle size={16} />
                                        <span>
                                          Próxima compra esperada em {sugestao.dias_ate_proxima_compra_esperada} dias
                                        </span>
                                      </div>
                                    )}
                                </div>
                              </div>
                            </div>
                          ))}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {sugestoesGlobais.length === 0 ? (
                <Card>
                  <CardContent className="py-12 text-center">
                    <p className="text-gray-500">Nenhuma sugestão global encontrada.</p>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardHeader>
                    <CardTitle>Sugestões Globais - Produtos Mais Comprados</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {sugestoesGlobais.map((sugestao) => (
                        <div
                          key={sugestao.produto_id}
                          className="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <h4 className="font-semibold">{sugestao.produto_nome}</h4>
                                <Badge className={getPrioridadeColor(sugestao.prioridade)}>
                                  {sugestao.prioridade}
                                </Badge>
                              </div>
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 dark:text-gray-400">
                                <div>
                                  <span className="font-medium">Clientes que compram:</span>{' '}
                                  {sugestao.num_clientes_compram}
                                </div>
                                <div>
                                  <span className="font-medium">Quantidade sugerida:</span>{' '}
                                  {sugestao.quantidade_sugerida} un
                                </div>
                                <div>
                                  <span className="font-medium">Estoque atual:</span> {sugestao.estoque_atual} un
                                </div>
                                <div>
                                  <span className="font-medium">Valor estimado:</span>{' '}
                                  R${' '}
                                  {sugestao.valor_estimado.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      </main>
    </>
  );
}
