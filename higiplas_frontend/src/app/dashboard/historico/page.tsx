'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/dashboard/Header';
import { apiService } from '@/services/apiService';
import { ClockIcon, ArrowUpIcon, ArrowDownIcon, UserIcon } from '@heroicons/react/24/outline';

interface Movimentacao {
  id: number;
  produto: {
    id: number;
    nome: string;
    codigo: string;
  };
  tipo_movimentacao: 'ENTRADA' | 'SAIDA';
  quantidade: number;
  data_movimentacao: string;
  usuario?: {
    nome: string;
  };
  observacao?: string;
  nota_fiscal?: string;
}

function HistoricoGeralContent() {
  const [movimentacoes, setMovimentacoes] = useState<Movimentacao[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filtroTipo, setFiltroTipo] = useState<'TODOS' | 'ENTRADA' | 'SAIDA'>('TODOS');
  const [searchTerm, setSearchTerm] = useState('');
  const { logout } = useAuth();

  useEffect(() => {
    const fetchHistoricoGeral = async () => {
      try {
        setLoading(true);
        const response = await apiService.get('/movimentacoes/historico-geral');
        // O backend retorna {movimentacoes: [...], estatisticas: {...}}
        const movimentacoesData = response?.data?.movimentacoes || [];
        
        // Mapear os dados para o formato esperado pelo frontend
        const movimentacoesMapeadas = movimentacoesData.map((mov: Record<string, unknown>) => {
          try {
            return {
              id: mov.id || 0,
              produto: {
                id: mov.produto_id || 0,
                nome: mov.produto_nome || 'Nome não disponível',
                codigo: mov.produto_codigo || 'N/A'
              },
              tipo_movimentacao: mov.tipo_movimentacao || 'ENTRADA',
              quantidade: mov.quantidade || 0,
              data_movimentacao: mov.data_movimentacao || new Date().toISOString(),
              usuario: {
                nome: mov.usuario_nome || 'N/A'
              },
              observacao: mov.observacao || null,
              nota_fiscal: mov.nota_fiscal || null
            };
          } catch (error) {
            console.error('Erro ao mapear movimentação:', error, mov);
            return null;
          }
        }).filter(Boolean); // Remove itens nulos
        
        setMovimentacoes(movimentacoesMapeadas);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Erro desconhecido";
        setError(message);
        if(message.includes('[401]')) logout();
      } finally {
        setLoading(false);
      }
    };
    
    fetchHistoricoGeral();
  }, [logout]);

  const movimentacoesFiltradas = movimentacoes.filter(mov => {
    try {
      if (!mov || !mov.produto) return false;
      const matchesTipo = filtroTipo === 'TODOS' || mov.tipo_movimentacao === filtroTipo;
      const matchesSearch = (mov.produto?.nome || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (mov.produto?.codigo || '').toLowerCase().includes(searchTerm.toLowerCase());
      return matchesTipo && matchesSearch;
    } catch (error) {
      console.error('Erro ao filtrar movimentação:', error, mov);
      return false;
    }
  });

  const formatDate = (dateString: string) => {
    try {
      if (!dateString) return 'Data não disponível';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'Data inválida';
      return date.toLocaleString('pt-BR');
    } catch (error) {
      console.error('Erro ao formatar data:', error, dateString);
      return 'Data inválida';
    }
  };

  const getTipoIcon = (tipo: string) => {
    return tipo === 'ENTRADA' ? (
      <ArrowUpIcon className="h-4 w-4 text-green-600" />
    ) : (
      <ArrowDownIcon className="h-4 w-4 text-red-600" />
    );
  };

  const getTipoColor = (tipo: string) => {
    return tipo === 'ENTRADA' 
      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
      : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
  };

  return (
    <>
      <Header>
        <h1 className="text-xl font-bold">Histórico Geral de Movimentações</h1>
        <div className="flex-1"/>
      </Header>
      
      <main className="flex-1 p-6 overflow-y-auto">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Filtros */}
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
            <div className="flex flex-col md:flex-row gap-4 items-center">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Buscar por produto ou código..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setFiltroTipo('TODOS')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    filtroTipo === 'TODOS'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-300 dark:hover:bg-gray-500'
                  }`}
                >
                  Todos
                </button>
                <button
                  onClick={() => setFiltroTipo('ENTRADA')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    filtroTipo === 'ENTRADA'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-300 dark:hover:bg-gray-500'
                  }`}
                >
                  Entradas
                </button>
                <button
                  onClick={() => setFiltroTipo('SAIDA')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    filtroTipo === 'SAIDA'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-300 dark:hover:bg-gray-500'
                  }`}
                >
                  Saídas
                </button>
              </div>
            </div>
          </div>

          {/* Estatísticas */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
              <div className="flex items-center">
                <ClockIcon className="h-8 w-8 text-blue-600 mr-3" />
                <div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {movimentacoesFiltradas.length}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total de Movimentações</p>
                </div>
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
              <div className="flex items-center">
                <ArrowUpIcon className="h-8 w-8 text-green-600 mr-3" />
                <div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {movimentacoesFiltradas.filter(m => m.tipo_movimentacao === 'ENTRADA').length}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Entradas</p>
                </div>
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
              <div className="flex items-center">
                <ArrowDownIcon className="h-8 w-8 text-red-600 mr-3" />
                <div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {movimentacoesFiltradas.filter(m => m.tipo_movimentacao === 'SAIDA').length}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Saídas</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tabela de Movimentações */}
          {loading && <p className="text-center py-8">Carregando histórico...</p>}
          {error && <p className="text-red-500 text-center py-8">{error}</p>}
          
          {!loading && !error && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Data
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Produto
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Tipo
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Quantidade
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Usuário
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Observação
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {movimentacoesFiltradas.map((mov) => (
                      <tr key={mov.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                          {formatDate(mov.data_movimentacao)}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                          <div>
                            <div className="font-medium">{mov.produto?.nome || 'Nome não disponível'}</div>
                            <div className="text-gray-500 dark:text-gray-400 text-xs">
                              Código: {mov.produto?.codigo || 'N/A'}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTipoColor(mov.tipo_movimentacao)}`}>
                            {getTipoIcon(mov.tipo_movimentacao)}
                            <span className="ml-1">{mov.tipo_movimentacao}</span>
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center text-sm text-gray-900 dark:text-gray-100">
                          {mov.quantidade}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                          <div className="flex items-center">
                            <UserIcon className="h-4 w-4 text-gray-400 mr-2" />
                            {mov.usuario?.nome || 'N/A'}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                          {mov.observacao || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {movimentacoesFiltradas.length === 0 && (
                <div className="text-center py-8">
                  <ClockIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
                    Nenhuma movimentação encontrada
                  </h3>
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Tente ajustar os filtros ou aguarde novas movimentações.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </>
  );
}

export default function HistoricoGeralPage() {
  return <HistoricoGeralContent />;
}