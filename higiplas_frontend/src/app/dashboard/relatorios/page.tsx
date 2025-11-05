'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/dashboard/Header';
import { reportsService, StockReport } from '@/services/reportsService';
import { 
  DocumentArrowDownIcon, 
  CalendarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

type ReportType = 'weekly' | 'monthly' | 'custom';

function RelatoriosContent() {
  const [reportType, setReportType] = useState<ReportType>('weekly');
  const [report, setReport] = useState<StockReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { logout } = useAuth();

  // Estados para filtros
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [year, setYear] = useState(new Date().getFullYear());

  const loadReport = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      
      let data: StockReport;
      
      if (reportType === 'weekly') {
        const dates = reportsService.getLastWeekDates();
        data = await reportsService.fetchWeeklyStockReport({
          start_date: dates.start_date,
          end_date: dates.end_date,
          format: 'json'
        });
      } else if (reportType === 'monthly') {
        data = await reportsService.fetchMonthlyStockReport({
          month,
          year,
          format: 'json'
        });
      } else {
        if (!startDate || !endDate) {
          setError('Selecione as datas inicial e final');
          setLoading(false);
          return;
        }
        data = await reportsService.fetchCustomStockReport(startDate, endDate, 'json');
      }
      
      setReport(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao carregar relatório';
      setError(message);
      if (message.includes('[401]')) logout();
    } finally {
      setLoading(false);
    }
  }, [reportType, month, year, startDate, endDate, logout]);

  useEffect(() => {
    loadReport();
  }, [loadReport]);

  const handleDownload = async (format: 'pdf' | 'xlsx') => {
    try {
      setLoading(true);
      
      if (reportType === 'weekly') {
        const dates = reportsService.getLastWeekDates();
        await reportsService.downloadWeeklyStockReport(format, dates);
      } else if (reportType === 'monthly') {
        // Implementar download mensal
        alert('Download mensal em desenvolvimento');
      } else {
        if (!startDate || !endDate) {
          alert('Selecione as datas inicial e final');
          return;
        }
        // Implementar download customizado
        alert('Download customizado em desenvolvimento');
      }
    } catch (err) {
      alert('Erro ao baixar relatório: ' + (err instanceof Error ? err.message : 'Erro desconhecido'));
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  return (
    <>
      <Header />
      <main className="min-h-screen bg-gray-50 dark:bg-gray-900 pt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Cabeçalho */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Relatórios de Estoque
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Visualize e exporte relatórios detalhados das movimentações de estoque
            </p>
          </div>

          {/* Seletor de Tipo de Relatório */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Tipo de Relatório
            </h2>
            <div className="flex flex-wrap gap-4">
              <button
                onClick={() => setReportType('weekly')}
                className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                  reportType === 'weekly'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                }`}
              >
                <CalendarIcon className="h-5 w-5 inline mr-2" />
                Últimos 7 Dias
              </button>
              <button
                onClick={() => setReportType('monthly')}
                className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                  reportType === 'monthly'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                }`}
              >
                <CalendarIcon className="h-5 w-5 inline mr-2" />
                Mensal
              </button>
              <button
                onClick={() => setReportType('custom')}
                className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                  reportType === 'custom'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                }`}
              >
                <CalendarIcon className="h-5 w-5 inline mr-2" />
                Período Customizado
              </button>
            </div>

            {/* Filtros por tipo */}
            {reportType === 'monthly' && (
              <div className="mt-4 flex gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Mês
                  </label>
                  <select
                    value={month}
                    onChange={(e) => setMonth(Number(e.target.value))}
                    className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                      <option key={m} value={m}>
                        {new Date(2000, m - 1).toLocaleDateString('pt-BR', { month: 'long' })}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Ano
                  </label>
                  <input
                    type="number"
                    value={year}
                    onChange={(e) => setYear(Number(e.target.value))}
                    className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                <div className="flex items-end">
                  <button
                    onClick={loadReport}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                  >
                    Gerar Relatório
                  </button>
                </div>
              </div>
            )}

            {reportType === 'custom' && (
              <div className="mt-4 flex gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Data Inicial
                  </label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Data Final
                  </label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                <div className="flex items-end">
                  <button
                    onClick={loadReport}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                  >
                    Gerar Relatório
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Botões de Download */}
          {report && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Exportar Relatório
              </h2>
              <div className="flex gap-4">
                <button
                  onClick={() => handleDownload('pdf')}
                  disabled={loading}
                  className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition flex items-center gap-2 disabled:opacity-50"
                >
                  <DocumentArrowDownIcon className="h-5 w-5" />
                  Baixar PDF
                </button>
                <button
                  onClick={() => handleDownload('xlsx')}
                  disabled={loading}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center gap-2 disabled:opacity-50"
                >
                  <DocumentArrowDownIcon className="h-5 w-5" />
                  Baixar Excel
                </button>
              </div>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Carregando relatório...</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* Resumo do Relatório */}
          {report && !loading && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                  <div className="flex items-center">
                    <DocumentTextIcon className="h-8 w-8 text-blue-600 mr-3" />
                    <div>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {report.total_movimentacoes}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Total de Movimentações</p>
                    </div>
                  </div>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                  <div className="flex items-center">
                    <ArrowUpIcon className="h-8 w-8 text-green-600 mr-3" />
                    <div>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {report.resumo.entradas}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Total de Entradas</p>
                    </div>
                  </div>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                  <div className="flex items-center">
                    <ArrowDownIcon className="h-8 w-8 text-red-600 mr-3" />
                    <div>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {report.resumo.saidas}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Total de Saídas</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Tabela de Detalhes */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Detalhes das Movimentações
                  </h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {report.periodo}
                  </p>
                </div>
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
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Antes
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Depois
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Origem
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Usuário
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                      {report.detalhes.map((mov) => (
                        <tr key={mov.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                            {formatDate(mov.data)}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                            <div>
                              <div className="font-medium">{mov.produto}</div>
                              <div className="text-gray-500 dark:text-gray-400 text-xs">
                                Código: {mov.codigo_produto}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                mov.tipo === 'ENTRADA'
                                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                                  : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                              }`}
                            >
                              {mov.tipo}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center text-sm text-gray-900 dark:text-gray-100">
                            {mov.quantidade}
                          </td>
                          <td className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                            {mov.quantidade_antes ?? '-'}
                          </td>
                          <td className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                            {mov.quantidade_depois ?? '-'}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                            {mov.origem || '-'}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                            {mov.usuario}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {report.detalhes.length === 0 && (
                  <div className="text-center py-12">
                    <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
                      Nenhuma movimentação encontrada
                    </h3>
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                      Não há movimentações no período selecionado.
                    </p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </main>
    </>
  );
}

export default function RelatoriosPage() {
  return <RelatoriosContent />;
}
