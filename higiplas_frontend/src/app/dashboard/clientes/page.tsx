'use client';

import { useState, useEffect, useCallback } from 'react';
import { Header } from '@/components/dashboard/Header';
import { useClientesV2 } from '@/hooks/useClientesV2';
import { ClienteCreateModal } from '@/components/clientes/ClienteCreateModal';
import { ClienteEditModal } from '@/components/clientes/ClienteEditModal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Search, Filter, Package, FileText, X, UserPlus, Pencil } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';

interface ClienteComprasData {
  cliente_id: number;
  cliente_nome: string;
  cnpj: string;
  total_notas: number;
  produtos_unicos: number;
  ultima_compra: string | null;
  valor_total_compras: number;
}

interface ProdutoMaisComprado {
  produto_id: number;
  produto_nome: string;
  codigo: string;
  total_quantidade: number;
  total_valor: number;
  num_compras: number;
  preco_medio: number;
}

interface HistoricoCompra {
  nota_fiscal: string;
  data_emissao: string;
  produtos: Array<{
    produto_id: number;
    produto_nome: string;
    codigo: string;
    quantidade: number;
    preco_unitario: number;
    valor_total: number;
  }>;
  valor_total: number;
}

export default function ClientesAdminPage() {
  const { user } = useAuth();
  const { clientes, fetchClientes, loading: loadingClientes } = useClientesV2();
  
  const [activeTab, setActiveTab] = useState<'cadastro' | 'visao-geral' | 'produtos' | 'historico'>('cadastro');
  const [searchTerm, setSearchTerm] = useState('');
  const [searchCadastro, setSearchCadastro] = useState('');
  const [diasAnalise, setDiasAnalise] = useState(90);
  const [clientesCompras, setClientesCompras] = useState<ClienteComprasData[]>([]);
  const [loadingCompras, setLoadingCompras] = useState(false);
  const [selectedCliente, setSelectedCliente] = useState<number | null>(null);
  const [produtosMaisComprados, setProdutosMaisComprados] = useState<ProdutoMaisComprado[]>([]);
  const [historicoCompras, setHistoricoCompras] = useState<HistoricoCompra[]>([]);
  const [loadingDetalhes, setLoadingDetalhes] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editClienteId, setEditClienteId] = useState<number | null>(null);

  const isAdmin = user?.perfil?.toUpperCase() === 'ADMIN' || user?.perfil?.toUpperCase() === 'GESTOR';

  const fetchClientesCompras = useCallback(async () => {
    setLoadingCompras(true);
    try {
      const response = await apiService.get(`/clientes/todos/visao-geral?dias=${diasAnalise}`);
      setClientesCompras(response?.data?.clientes || []);
    } catch (error) {
      console.error('Erro ao buscar dados de compras:', error);
      toast.error('Erro ao carregar dados de compras dos clientes');
    } finally {
      setLoadingCompras(false);
    }
  }, [diasAnalise]);

  // Carregar lista de clientes (cadastro) uma vez quando admin acessa
  useEffect(() => {
    if (isAdmin) {
      fetchClientes({ limit: 1000, skip: 0 });
    }
  }, [isAdmin, fetchClientes]);

  // Carregar visão de compras quando mudar período
  useEffect(() => {
    if (isAdmin) {
      fetchClientesCompras();
    }
  }, [isAdmin, diasAnalise, fetchClientesCompras]);

  const fetchProdutosMaisComprados = async (clienteId: number) => {
    setLoadingDetalhes(true);
    try {
      const response = await apiService.get(`/clientes/${clienteId}/produtos-mais-comprados?limit=10`);
      setProdutosMaisComprados(response?.data?.produtos_mais_comprados || []);
    } catch (error) {
      console.error('Erro ao buscar produtos mais comprados:', error);
      toast.error('Erro ao carregar produtos mais comprados');
    } finally {
      setLoadingDetalhes(false);
    }
  };

  const fetchHistoricoCompras = async (clienteId: number) => {
    setLoadingDetalhes(true);
    try {
      const response = await apiService.get(`/clientes/${clienteId}/historico-compras?dias=${diasAnalise}`);
      setHistoricoCompras(response?.data?.compras_por_nota || []);
    } catch (error) {
      console.error('Erro ao buscar histórico de compras:', error);
      toast.error('Erro ao carregar histórico de compras');
    } finally {
      setLoadingDetalhes(false);
    }
  };

  const handleViewCliente = async (clienteId: number) => {
    setSelectedCliente(clienteId);
    setActiveTab('produtos');
    await fetchProdutosMaisComprados(clienteId);
  };

  const handleViewHistorico = async (clienteId: number) => {
    setSelectedCliente(clienteId);
    setActiveTab('historico');
    await fetchHistoricoCompras(clienteId);
  };

  const clienteSelecionado = clientes.find((c) => c.id === selectedCliente);
  const clienteComprasSelecionado = clientesCompras.find((c) => c.cliente_id === selectedCliente);

  const clientesFiltrados = clientesCompras.filter((cliente) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      cliente.cliente_nome.toLowerCase().includes(term) ||
      cliente.cnpj?.toLowerCase().includes(term)
    );
  });

  const clientesCadastroFiltrados = clientes.filter((c) => {
    if (!searchCadastro.trim()) return true;
    const term = searchCadastro.toLowerCase();
    return (
      c.nome.toLowerCase().includes(term) ||
      c.telefone?.toLowerCase().includes(term) ||
      c.bairro?.toLowerCase().includes(term) ||
      c.cidade?.toLowerCase().includes(term)
    );
  });

  const recarregarClientes = useCallback(() => {
    fetchClientes({ limit: 1000, skip: 0 });
  }, [fetchClientes]);

  if (!isAdmin) {
    return (
      <>
        <Header>
          <h1 className="text-xl font-bold">Acesso Negado</h1>
        </Header>
        <main className="flex-1 p-6">
          <Card>
            <CardContent className="p-6 text-center">
              <p className="text-red-600">Apenas administradores ou gestores podem acessar esta página.</p>
            </CardContent>
          </Card>
        </main>
      </>
    );
  }

  return (
    <>
      <Header>
        <h1 className="text-xl font-bold">Clientes</h1>
      </Header>
      <ClienteCreateModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSuccess={() => { recarregarClientes(); setCreateModalOpen(false); }}
      />
      <ClienteEditModal
        open={editClienteId !== null}
        clienteId={editClienteId}
        onClose={() => setEditClienteId(null)}
        onSuccess={() => { recarregarClientes(); setEditClienteId(null); }}
      />
      <main className="flex-1 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Filtros */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter size={20} /> Filtros
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                  <Input
                    placeholder="Buscar por nome ou CNPJ..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={diasAnalise.toString()} onValueChange={(v) => setDiasAnalise(Number(v))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Período de análise" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="30">Últimos 30 dias</SelectItem>
                    <SelectItem value="60">Últimos 60 dias</SelectItem>
                    <SelectItem value="90">Últimos 90 dias</SelectItem>
                    <SelectItem value="180">Últimos 180 dias</SelectItem>
                  </SelectContent>
                </Select>
                {selectedCliente && (
                  <Button variant="outline" onClick={() => setSelectedCliente(null)}>
                    <X size={16} className="mr-2" />
                    Limpar seleção
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Tabs */}
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('cadastro')}
                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'cadastro'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Cadastro ({clientes.length})
              </button>
              <button
                onClick={() => setActiveTab('visao-geral')}
                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'visao-geral'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Análise de Compras ({clientesFiltrados.length})
              </button>
              {selectedCliente && (
                <>
                  <button
                    onClick={() => handleViewCliente(selectedCliente)}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'produtos'
                        ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Produtos Mais Comprados
                  </button>
                  <button
                    onClick={() => handleViewHistorico(selectedCliente)}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'historico'
                        ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Histórico de NF-e
                  </button>
                </>
              )}
            </nav>
          </div>

          {/* Conteúdo das Tabs */}
          {activeTab === 'cadastro' && (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0">
                <CardTitle>Cadastro de Clientes</CardTitle>
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                    <Input
                      placeholder="Buscar por nome, telefone, bairro..."
                      value={searchCadastro}
                      onChange={(e) => setSearchCadastro(e.target.value)}
                      className="pl-10 w-64"
                    />
                  </div>
                  <Button onClick={() => setCreateModalOpen(true)} className="gap-2">
                    <UserPlus size={18} />
                    Novo Cliente
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {loadingClientes ? (
                  <div className="text-center py-12 text-gray-500">Carregando clientes...</div>
                ) : clientesCadastroFiltrados.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    {clientes.length === 0
                      ? 'Nenhum cliente cadastrado. Clique em Novo Cliente para cadastrar.'
                      : 'Nenhum cliente encontrado com o filtro informado.'}
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Nome</TableHead>
                          <TableHead>Telefone</TableHead>
                          <TableHead>Bairro</TableHead>
                          <TableHead>Cidade</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead className="text-right">Ações</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {clientesCadastroFiltrados.map((c) => (
                          <TableRow key={c.id}>
                            <TableCell className="font-medium">{c.nome}</TableCell>
                            <TableCell className="font-mono text-sm">{c.telefone || '—'}</TableCell>
                            <TableCell>{c.bairro || '—'}</TableCell>
                            <TableCell>{c.cidade || '—'}</TableCell>
                            <TableCell>
                              <Badge variant={c.status === 'ATIVO' ? 'default' : 'secondary'}>
                                {c.status}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-right">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setEditClienteId(c.id)}
                                title="Editar cliente"
                              >
                                <Pencil size={16} />
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {activeTab === 'visao-geral' && (
            <Card>
              <CardHeader>
                <CardTitle>Clientes com Compras Registradas</CardTitle>
                <p className="text-sm text-gray-500 mt-1">
                  Dados baseados apenas em NF-e processadas (verificadas)
                </p>
              </CardHeader>
              <CardContent>
                {loadingCompras ? (
                  <div className="text-center py-12">
                    <p className="text-gray-500">Carregando dados de compras...</p>
                  </div>
                ) : clientesFiltrados.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <p>Nenhum cliente com compras no período selecionado.</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Cliente</TableHead>
                          <TableHead>CNPJ</TableHead>
                          <TableHead>Total de NF-e</TableHead>
                          <TableHead>Produtos Únicos</TableHead>
                          <TableHead>Última Compra</TableHead>
                          <TableHead>Valor Total</TableHead>
                          <TableHead className="text-center">Ações</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {clientesFiltrados.map((cliente) => (
                          <TableRow key={cliente.cliente_id}>
                            <TableCell className="font-medium">{cliente.cliente_nome}</TableCell>
                            <TableCell className="font-mono text-sm">{cliente.cnpj || 'N/A'}</TableCell>
                            <TableCell>
                              <Badge variant="outline">{cliente.total_notas}</Badge>
                            </TableCell>
                            <TableCell>
                              <Badge variant="outline">{cliente.produtos_unicos}</Badge>
                            </TableCell>
                            <TableCell>
                              {cliente.ultima_compra
                                ? new Date(cliente.ultima_compra).toLocaleDateString('pt-BR')
                                : 'N/A'}
                            </TableCell>
                            <TableCell className="font-medium">
                              R$ {cliente.valor_total_compras.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center justify-center gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleViewCliente(cliente.cliente_id)}
                                  title="Ver produtos mais comprados"
                                >
                                  <Package size={16} />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleViewHistorico(cliente.cliente_id)}
                                  title="Ver histórico de NF-e"
                                >
                                  <FileText size={16} />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {activeTab === 'produtos' && selectedCliente && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Produtos Mais Comprados</CardTitle>
                    <p className="text-sm text-gray-500 mt-1">
                      {clienteSelecionado?.nome || clienteComprasSelecionado?.cliente_nome} - CNPJ:{' '}
                      {clienteComprasSelecionado?.cnpj}
                    </p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {loadingDetalhes ? (
                  <div className="text-center py-12">
                    <p className="text-gray-500">Carregando produtos...</p>
                  </div>
                ) : produtosMaisComprados.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <p>Nenhum produto encontrado para este cliente.</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Produto</TableHead>
                          <TableHead>Código</TableHead>
                          <TableHead>Total Comprado</TableHead>
                          <TableHead>Nº de Compras</TableHead>
                          <TableHead>Valor Total</TableHead>
                          <TableHead>Preço Médio</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {produtosMaisComprados.map((produto) => (
                          <TableRow key={produto.produto_id}>
                            <TableCell className="font-medium">{produto.produto_nome}</TableCell>
                            <TableCell className="font-mono text-sm">{produto.codigo || 'N/A'}</TableCell>
                            <TableCell>{produto.total_quantidade.toLocaleString('pt-BR')} un</TableCell>
                            <TableCell>
                              <Badge variant="outline">{produto.num_compras}</Badge>
                            </TableCell>
                            <TableCell className="font-medium">
                              R$ {produto.total_valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                            </TableCell>
                            <TableCell>
                              R$ {produto.preco_medio.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {activeTab === 'historico' && selectedCliente && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Histórico de NF-e Processadas</CardTitle>
                    <p className="text-sm text-gray-500 mt-1">
                      {clienteSelecionado?.nome || clienteComprasSelecionado?.cliente_nome} - CNPJ:{' '}
                      {clienteComprasSelecionado?.cnpj}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Total: {historicoCompras.length} nota(s) fiscal(is) - Apenas dados verificados de NF-e
                    </p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {loadingDetalhes ? (
                  <div className="text-center py-12">
                    <p className="text-gray-500">Carregando histórico...</p>
                  </div>
                ) : historicoCompras.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <p>Nenhuma NF-e encontrada para este cliente no período selecionado.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {historicoCompras.map((compra, idx) => (
                      <Card key={idx} className="border-l-4 border-l-blue-500">
                        <CardHeader className="pb-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <CardTitle className="text-base">
                                NF-e {compra.nota_fiscal}
                              </CardTitle>
                              <p className="text-sm text-gray-500 mt-1">
                                {new Date(compra.data_emissao).toLocaleDateString('pt-BR', {
                                  day: '2-digit',
                                  month: '2-digit',
                                  year: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </p>
                            </div>
                            <Badge variant="default" className="text-base">
                              R$ {compra.valor_total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                            </Badge>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2">
                            {compra.produtos.map((produto, pIdx) => (
                              <div
                                key={pIdx}
                                className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-800 last:border-0"
                              >
                                <div className="flex-1">
                                  <p className="font-medium">{produto.produto_nome}</p>
                                  <p className="text-sm text-gray-500">
                                    Código: {produto.codigo || 'N/A'} | Quantidade: {produto.quantidade} un
                                  </p>
                                </div>
                                <div className="text-right">
                                  <p className="font-medium">
                                    R$ {produto.valor_total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                  </p>
                                  <p className="text-sm text-gray-500">
                                    R$ {produto.preco_unitario.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}/un
                                  </p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </>
  );
}
