// /src/app/dashboard/history/[productId]/page.tsx
"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation'; // Hook para pegar o ID da URL
import { apiService } from '@/services/apiService';
import ClientLayout from '@/components/ClientLayout';
import { Header } from '@/components/dashboard/Header';
import { useAuth } from '@/contexts/AuthContext';

// Interface para os dados da movimentação
interface Movimentacao {
    id: number;
    tipo_movimentacao: 'ENTRADA' | 'SAIDA';
    quantidade: number;
    observacao: string | null;
    data_movimentacao: string;
    usuario: {
        nome: string;
    } | null;
}

function HistoryPageContent() {
    const params = useParams(); // Pega { productId: '1' } da URL
    const productId = params.productId as string;
    
    const [movimentacoes, setMovimentacoes] = useState<Movimentacao[]>([]);
    const [productName, setProductName] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const { logout } = useAuth();

    useEffect(() => {
        if (!productId) return;
        
        const fetchHistory = async () => {
            try {
                setLoading(true);
                // Aqui assumimos que temos uma rota para pegar dados de um produto específico
                // Se não tiver, podemos buscar a lista e filtrar
                const productData = await apiService.get(`/produtos/${productId}`); // Precisa criar essa rota
                setProductName(productData.nome);

                const historyData = await apiService.get(`/movimentacoes/${productId}`);
                setMovimentacoes(historyData);

            } catch (err) {
                const message = err instanceof Error ? err.message : "Erro desconhecido";
                setError(message);
                if(message.includes('[401]')) logout();
            } finally {
                setLoading(false);
            }
        };
        fetchHistory();
    }, [productId, logout]);

    return (
        <>
            <Header>
                <h1 className="text-xl font-bold">Histórico de Movimentações</h1>
                <div className="flex-1"/>
                {/* Botões do header global */}
            </Header>
            <main className="flex-1 p-6 overflow-y-auto">
                <div className="max-w-7xl mx-auto">
                    <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
                       Produto: <span className="text-blue-600">{productName || 'Carregando...'}</span>
                    </h2>
                    {loading && <p>Carregando histórico...</p>}
                    {error && <p className="text-red-500">{error}</p>}
                    {!loading && !error && (
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                <thead className="bg-gray-50 dark:bg-gray-700">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium uppercase">Data</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium uppercase">Tipo</th>
                                        <th className="px-6 py-3 text-center text-xs font-medium uppercase">Quantidade</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium uppercase">Usuário</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium uppercase">Observação</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                                    {movimentacoes.map((mov) => (
                                        <tr key={mov.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                                            <td className="px-6 py-4">{new Date(mov.data_movimentacao).toLocaleString('pt-BR')}</td>
                                            <td className="px-6 py-4">
                                                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                                    mov.tipo_movimentacao === 'ENTRADA' 
                                                    ? 'bg-green-100 text-green-800' 
                                                    : 'bg-red-100 text-red-800'
                                                }`}>
                                                    {mov.tipo_movimentacao}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-center">{mov.quantidade}</td>
                                            <td className="px-6 py-4">{mov.usuario?.nome || 'N/A'}</td>
                                            <td className="px-6 py-4">{mov.observacao || '-'}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                     {!loading && movimentacoes.length === 0 && <p className="mt-4 text-center">Nenhuma movimentação registrada para este produto.</p>}
                </div>
            </main>
        </>
    );
}

export default function HistoryPageWrapper() {
  // O layout já cuida do ClientLayout
  return <HistoryPageContent />;
}