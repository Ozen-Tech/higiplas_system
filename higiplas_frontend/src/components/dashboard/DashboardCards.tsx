// /src/components/dashboard/DashboardCards.tsx
'use client';

import { useEffect, useState } from 'react';
import { apiService } from '@/services/apiService';
import { CubeIcon, ExclamationTriangleIcon, BanknotesIcon } from '@heroicons/react/24/outline';

interface KpiData {
  total_produtos: number;
  produtos_baixo_estoque: number;
  valor_total_estoque: number;
}

export function DashboardCards() {
  const [data, setData] = useState<KpiData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchKpis = async () => {
      try {
        const kpiData = await apiService.get('/kpis/');
        setData(kpiData?.data || null);
      } catch (error) {
        console.error("Erro ao buscar KPIs:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchKpis();
  }, []);

  if (loading) {
    return <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-pulse">
        {[...Array(3)].map((_, i) => <div key={i} className="h-28 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>)}
    </div>;
  }
  
  if (!data) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Card 1: Total de Produtos */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border-l-4 border-blue-500">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Itens Únicos</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">{data.total_produtos}</p>
          </div>
          <CubeIcon className="h-10 w-10 text-blue-500" />
        </div>
      </div>
      
      {/* Card 2: Produtos com Baixo Estoque */}
      <div className={`bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border-l-4 ${data.produtos_baixo_estoque > 0 ? 'border-red-500' : 'border-green-500'}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Itens com Baixo Estoque</p>
            <p className={`text-3xl font-bold ${data.produtos_baixo_estoque > 0 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>{data.produtos_baixo_estoque}</p>
          </div>
          <ExclamationTriangleIcon className={`h-10 w-10 ${data.produtos_baixo_estoque > 0 ? 'text-red-500' : 'text-green-500'}`} />
        </div>
      </div>
      
      {/* Card 3: Valor Total do Estoque */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border-l-4 border-purple-500">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Valor do Estoque (Custo)</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">
              {data.valor_total_estoque.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            </p>
          </div>
          <BanknotesIcon className="h-10 w-10 text-purple-500" />
        </div>
      </div>
    </div>
  );
}