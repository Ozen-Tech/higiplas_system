// /src/app/dashboard/orcamentos/[id]/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { apiService } from '@/services/apiService';
import { Orcamento } from '@/types'; // Vamos precisar criar/ajustar este tipo
import { ArrowLeftIcon, CheckCircleIcon, DocumentTextIcon, UserIcon, CalendarIcon } from '@heroicons/react/24/outline';

// --- COMPONENTE DE CARREGAMENTO (LOADING) ---
const LoadingSpinner = () => (
  <div className="flex justify-center items-center h-64">
    <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-500"></div>
  </div>
);

// --- COMPONENTE PRINCIPAL DA PÁGINA ---
export default function OrcamentoDetailPage() {
  const router = useRouter();
  const params = useParams();
  const orcamentoId = params.id;

  const [orcamento, setOrcamento] = useState<Orcamento | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFinalizing, setIsFinalizing] = useState(false);

  useEffect(() => {
    if (typeof orcamentoId === 'string') {
      const fetchOrcamento = async () => {
        try {
          setLoading(true);
          const data = await apiService.get(`/orcamentos/${orcamentoId}`);
          setOrcamento(data?.data || null);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Falha ao buscar detalhes do orçamento.');
        } finally {
          setLoading(false);
        }
      };
      fetchOrcamento();
    }
  }, [orcamentoId]);

  const handleFinalizar = async () => {
    if (!orcamentoId || orcamento?.status === 'FINALIZADO') return;
    
    if (!confirm("Tem certeza que deseja finalizar este pedido? Esta ação dará baixa no estoque e não pode ser desfeita.")) {
      return;
    }

    setIsFinalizing(true);
    setError(null);
    try {
      const updatedOrcamento = await apiService.post(`/orcamentos/${orcamentoId}/finalizar`, {});
      setOrcamento(updatedOrcamento?.data || null);
      alert('Pedido finalizado com sucesso e estoque atualizado!');
    } catch (err) {
       const errorMessage = err instanceof Error ? err.message : 'Ocorreu um erro desconhecido.';
       setError(`Falha ao finalizar: ${errorMessage}`);
       alert(`Erro: ${errorMessage}`);
    } finally {
      setIsFinalizing(false);
    }
  };
  
  const totalOrcamento = orcamento?.itens.reduce((acc, item) => acc + (item.quantidade * item.preco_unitario_congelado), 0) || 0;

  return (
    <div className="p-4 md:p-8 space-y-6 animate-fadeIn">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-sm font-semibold text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
        <ArrowLeftIcon className="h-5 w-5" />
        Voltar para Orçamentos
      </button>

      {loading && <LoadingSpinner />}
      
      {error && (
        <div className="bg-red-100 dark:bg-red-900/30 border-l-4 border-red-500 text-red-700 dark:text-red-300 p-4 rounded-md" role="alert">
          <p className="font-bold">Erro</p>
          <p>{error}</p>
        </div>
      )}
      
      {orcamento && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden border border-gray-200 dark:border-gray-700">
          {/* Cabeçalho do Orçamento */}
          <div className="p-6 border-b dark:border-gray-700">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  Orçamento #{String(orcamento.id).padStart(4, '0')}
                </h1>
                <p className="text-gray-500 dark:text-gray-400 mt-1">
                  Cliente: <span className="font-medium text-gray-700 dark:text-gray-300">{orcamento.nome_cliente}</span>
                </p>
              </div>
              <div className={`px-3 py-1 text-sm font-semibold rounded-full flex items-center gap-2 ${
                  orcamento.status === 'FINALIZADO' 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300' 
                    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300'
                }`}
              >
                {orcamento.status === 'FINALIZADO' ? <CheckCircleIcon className="h-4 w-4" /> : <DocumentTextIcon className="h-4 w-4" />}
                {orcamento.status}
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mt-6 text-sm text-gray-600 dark:text-gray-400">
                <div className="flex items-center gap-2"><UserIcon className="h-5 w-5 text-gray-400"/> Vendedor: {orcamento.usuario.nome}</div>
                <div className="flex items-center gap-2"><CalendarIcon className="h-5 w-5 text-gray-400"/> Criado em: {new Date(orcamento.data_criacao).toLocaleDateString('pt-BR')}</div>
                <div className="flex items-center gap-2"><CalendarIcon className="h-5 w-5 text-gray-400"/> Válido até: {orcamento.data_validade ? new Date(orcamento.data_validade + 'T00:00:00').toLocaleDateString('pt-BR') : 'N/A'}</div>
            </div>
          </div>

          {/* Itens do Orçamento */}
          <div className="p-6">
            <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">Itens do Pedido</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700/50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Produto</th>
                    <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Quantidade</th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Preço Unit.</th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Subtotal</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {orcamento.itens.map(item => (
                    <tr key={item.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">{item.produto.nome}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-center">{item.quantidade}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-right">{item.preco_unitario_congelado.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200 font-semibold text-right">{(item.quantidade * item.preco_unitario_congelado).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          {/* Rodapé e Ações */}
          <div className="p-6 bg-gray-50 dark:bg-gray-900/50 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-xl font-bold text-gray-900 dark:text-gray-100">
              <span>Total: </span>
              <span>{totalOrcamento.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
            </div>
            {orcamento.status !== 'FINALIZADO' && (
              <button
                onClick={handleFinalizar}
                disabled={isFinalizing}
                className="w-full md:w-auto flex items-center justify-center gap-2 px-6 py-2 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700 disabled:bg-green-400 disabled:cursor-not-allowed transition-colors"
              >
                {isFinalizing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                    Finalizando...
                  </>
                ) : (
                  <>
                    <CheckCircleIcon className="h-5 w-5" />
                    Finalizar Pedido e Dar Baixa
                  </>
                )}
              </button>
            )}
            {orcamento.status === 'FINALIZADO' && (
                <p className="text-green-600 dark:text-green-400 text-sm font-medium">Pedido concluído e estoque atualizado.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}