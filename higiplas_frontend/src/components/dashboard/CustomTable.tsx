// /src/components/dashboard/CustomTable.tsx
import React from 'react';

interface Column {
  header: string;
  accessor: string;
  render?: (item: any) => React.ReactNode;
}

interface CustomTableProps {
  columns: Column[];
  data: any[];
  renderMobileCard?: (item: any) => React.ReactNode;
}

export const CustomTable = ({ columns, data, renderMobileCard }: CustomTableProps) => {
  if (data.length === 0) {
    return <p className="text-center p-8 text-gray-500">Nenhum dado encontrado.</p>;
  }

  return (
    <div>
      {/* Tabela para Telas Médias e Maiores */}
      <div className="hidden md:block">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              {columns.map(col => (
                <th key={col.accessor} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{col.header}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {data.map((item) => (
              <tr key={item.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                {columns.map(col => (
                  <td key={col.accessor} className="px-6 py-4 whitespace-nowrap text-sm">
                    {col.render ? col.render(item) : item[col.accessor]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Lista de Cards para Telas Pequenas */}
      <div className="block md:hidden p-4 space-y-4">
        {data.map(item => (
          <div key={item.id} className="bg-white dark:bg-gray-800/50 rounded-lg shadow p-4 border-l-4 border-blue-500">
            {renderMobileCard ? renderMobileCard(item) : <div>Dados do Item #{item.id}</div>}
          </div>
        ))}
      </div>
    </div>
  );
};