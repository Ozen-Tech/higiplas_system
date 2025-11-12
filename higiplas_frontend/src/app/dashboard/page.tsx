'use client';

import { useEffect, useState } from 'react';
import { Header } from '@/components/dashboard/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiService } from '@/services/apiService';
import { 
  CubeIcon, 
  ExclamationTriangleIcon, 
  BanknotesIcon,
  UserGroupIcon,
  ShoppingCartIcon,
  ChartBarIcon,
  TrendingUpIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircle
} from '@heroicons/react/24/outline';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

interface DashboardKPIs {
  estoque: {
    total_produtos: number;
    produtos_baixo_estoque: number;
    produtos_sem_estoque: number;
    valor_total_estoque: number;
    valor_total_estoque_venda: number;
  };
  vendedores: {
    total_vendedores: number;
    vendedores_ativos_mes: number;
    orcamentos_pendentes: number;
    orcamentos_mes: number;
  };
  vendas: {
    vendas_mes: number;
    vendas_semana: number;
    orcamentos_confirmados_mes: number;
    valor_orcamentos_confirmados: number;
    ticket_medio: number;
    numero_vendas_mes: number;
  };
}

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchKPIs = async () => {
      try {
        setLoading(true);
        const response = await apiService.get('/kpis/');
        setKpis(response?.data || null);
        setError(null);
      } catch (err) {
        console.error('Erro ao buscar KPIs:', err);
        setError('Erro ao carregar dados do dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchKPIs();
    // Atualizar a cada 5 minutos
    const interval = setInterval(fetchKPIs, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <>
        <Header>
          <h1 className="text-xl font-bold">Dashboard</h1>
        </Header>
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
              {[...Array(9)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
              ))}
            </div>
          </div>
        </main>
      </>
    );
  }

  if (error || !kpis) {
    return (
      <>
        <Header>
          <h1 className="text-xl font-bold">Dashboard</h1>
        </Header>
        <main className="flex-1 p-6">
          <Card>
            <CardContent className="p-6 text-center">
              <p className="text-red-600">{error || 'Erro ao carregar dados'}</p>
            </CardContent>
          </Card>
        </main>
      </>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('pt-BR').format(value);
  };

  return (
    <>
      <Header>
        <h1 className="text-xl font-bold">Dashboard</h1>
      </Header>
      <main className="flex-1 p-4 md:p-6 overflow-y-auto">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Boas-vindas */}
          <div>
            <h2 className="text-2xl md:text-3xl font-bold text-gray-800 dark:text-gray-100">
              Olá, {user?.nome || 'Usuário'}! 👋
            </h2>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              Visão geral do seu negócio em tempo real
            </p>
          </div>

          {/* ============= ESTOQUE ============= */}
          <div>
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-4 flex items-center gap-2">
              <CubeIcon className="h-5 w-5" />
              Estoque
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <Card className="border-l-4 border-l-blue-500">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Total de Produtos</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                        {formatNumber(kpis.estoque.total_produtos)}
                      </p>
                    </div>
                    <CubeIcon className="h-8 w-8 text-blue-500" />
                  </div>
                </CardContent>
              </Card>

              <Card className={`border-l-4 ${kpis.estoque.produtos_baixo_estoque > 0 ? 'border-l-yellow-500' : 'border-l-green-500'}`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Baixo Estoque</p>
                      <p className={`text-2xl font-bold ${kpis.estoque.produtos_baixo_estoque > 0 ? 'text-yellow-600 dark:text-yellow-400' : 'text-green-600 dark:text-green-400'}`}>
                        {formatNumber(kpis.estoque.produtos_baixo_estoque)}
                      </p>
                    </div>
                    <ExclamationTriangleIcon className={`h-8 w-8 ${kpis.estoque.produtos_baixo_estoque > 0 ? 'text-yellow-500' : 'text-green-500'}`} />
                  </div>
                </CardContent>
              </Card>

              <Card className={`border-l-4 ${kpis.estoque.produtos_sem_estoque > 0 ? 'border-l-red-500' : 'border-l-gray-300'}`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Sem Estoque</p>
                      <p className={`text-2xl font-bold ${kpis.estoque.produtos_sem_estoque > 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-600 dark:text-gray-400'}`}>
                        {formatNumber(kpis.estoque.produtos_sem_estoque)}
                      </p>
                    </div>
                    <XCircle className={`h-8 w-8 ${kpis.estoque.produtos_sem_estoque > 0 ? 'text-red-500' : 'text-gray-400'}`} />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-purple-500">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Valor (Custo)</p>
                      <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                        {formatCurrency(kpis.estoque.valor_total_estoque)}
                      </p>
                    </div>
                    <BanknotesIcon className="h-8 w-8 text-purple-500" />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-green-500">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Valor (Venda)</p>
                      <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                        {formatCurrency(kpis.estoque.valor_total_estoque_venda)}
                      </p>
                    </div>
                    <TrendingUpIcon className="h-8 w-8 text-green-500" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* ============= VENDEDORES ============= */}
          <div>
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-4 flex items-center gap-2">
              <UserGroupIcon className="h-5 w-5" />
              Vendedores
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="border-l-4 border-l-indigo-500">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Total Vendedores</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                        {formatNumber(kpis.vendedores.total_vendedores)}
                      </p>
                    </div>
                    <UserGroupIcon className="h-8 w-8 text-indigo-500" />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-green-500">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Ativos (Mês)</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                        {formatNumber(kpis.vendedores.vendedores_ativos_mes)}
                      </p>
                    </div>
                    <CheckCircleIcon className="h-8 w-8 text-green-500" />
                  </div>
                </CardContent>
              </Card>

              <Card className={`border-l-4 ${kpis.vendedores.orcamentos_pendentes > 0 ? 'border-l-orange-500' : 'border-l-gray-300'}`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Pendentes</p>
                      <p className={`text-2xl font-bold ${kpis.vendedores.orcamentos_pendentes > 0 ? 'text-orange-600 dark:text-orange-400' : 'text-gray-600 dark:text-gray-400'}`}>
                        {formatNumber(kpis.vendedores.orcamentos_pendentes)}
                      </p>
                    </div>
                    <ClockIcon className={`h-8 w-8 ${kpis.vendedores.orcamentos_pendentes > 0 ? 'text-orange-500' : 'text-gray-400'}`} />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-blue-500 cursor-pointer hover:shadow-lg transition-shadow"
                    onClick={() => router.push('/dashboard/orcamentos')}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Orçamentos (Mês)</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                        {formatNumber(kpis.vendedores.orcamentos_mes)}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">Clique para ver</p>
                    </div>
                    <ShoppingCartIcon className="h-8 w-8 text-blue-500" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* ============= VENDAS ============= */}
          <div>
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-4 flex items-center gap-2">
              <ChartBarIcon className="h-5 w-5" />
              Vendas
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Card className="border-l-4 border-l-green-500">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Vendas do Mês</p>
                      <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                        {formatCurrency(kpis.vendas.vendas_mes)}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {formatNumber(kpis.vendas.numero_vendas_mes)} vendas
                      </p>
                    </div>
                    <TrendingUpIcon className="h-8 w-8 text-green-500" />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-blue-500">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Vendas da Semana</p>
                      <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {formatCurrency(kpis.vendas.vendas_semana)}
                      </p>
                    </div>
                    <ChartBarIcon className="h-8 w-8 text-blue-500" />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-purple-500">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Ticket Médio</p>
                      <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                        {formatCurrency(kpis.vendas.ticket_medio)}
                      </p>
                    </div>
                    <ShoppingCartIcon className="h-8 w-8 text-purple-500" />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-indigo-500">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Orçamentos Confirmados</p>
                      <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                        {formatNumber(kpis.vendas.orcamentos_confirmados_mes)}
                      </p>
                    </div>
                    <CheckCircleIcon className="h-8 w-8 text-indigo-500" />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-emerald-500">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Valor Confirmado (Mês)</p>
                      <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                        {formatCurrency(kpis.vendas.valor_orcamentos_confirmados)}
                      </p>
                    </div>
                    <BanknotesIcon className="h-8 w-8 text-emerald-500" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
