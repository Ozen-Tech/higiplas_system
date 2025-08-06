"use client";

import React from 'react';

// MOVA ESTAS INTERFACES PARA FORA E EXPORTE-AS
export interface ItemWithId {
  id: number | string;
}

export interface Column<T> {
  header: string;
  // O acessor agora é fortemente tipado para as chaves de T ou a string 'actions'
  accessor: keyof T | 'actions';
  render?: (item: T) => React.ReactNode;
}

// A interface das props continua a mesma, mas usa o tipo Column<T> exportado
interface CustomTableProps<T> {
  columns: Column<T>[];
  data: T[];
  renderMobileCard?: (item: T) => React.ReactNode;
}

export const CustomTable = <T extends ItemWithId>({ columns, data, renderMobileCard }: CustomTableProps<T>) => {
  if (!data || data.length === 0) {
    return <p className="text-center p-8 text-gray-500">Nenhum dado encontrado.</p>;
  }

  return (
    // O resto do componente permanece exatamente o mesmo
    <div>
      {/* Tabela para Desktop */}
      <div className="hidden md:block">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              {columns.map(col => (
                <th key={String(col.accessor)} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{col.header}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {data.map((item) => (
              <tr key={item.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                {columns.map(col => (
                  <td key={String(col.accessor)} className="px-6 py-4 whitespace-nowrap text-sm">
                    {col.render ? col.render(item) : (item[col.accessor as keyof T] as React.ReactNode)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

       {/* Cards para Mobile (sem alterações) */}
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