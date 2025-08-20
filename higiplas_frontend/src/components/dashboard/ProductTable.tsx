// /src/components/dashboard/ProductTable.tsx
'use client';

import { Product, ProdutoUpdateData } from "@/types";
import { EditableProductTableRow } from './EditableProductTableRow'; // Importamos nosso novo componente

interface ProductTableProps {
  products: Product[];
  onSave: (id: number, data: ProdutoUpdateData) => Promise<void>;
  onRemove: (id: number) => Promise<void>;
  onMoveStock: (product: Product) => void;
}

export function ProductTable({ products, onSave, onRemove, onMoveStock }: ProductTableProps) {
  
  // Headers da tabela - podemos definir aqui para manter o código limpo
  const tableHeaders = [
    { label: 'Produto' },
    { label: 'Código' },
    { label: 'Estoque', className: 'text-center' },
    { label: 'Est. Mínimo', className: 'text-center' },
    { label: 'Preço Custo', className: 'text-right' },
    { label: 'Preço Venda', className: 'text-right' },
    { label: 'Data Cadastro', className: 'text-center' },
    { label: 'Ações', className: 'text-right' },
  ];

  return (
    <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-700/50">
          <tr>
            {tableHeaders.map(header => (
              <th 
                key={header.label} 
                scope="col" 
                className={`px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider ${header.className || ''}`}
              >
                {header.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {products.map((product) => (
            <EditableProductTableRow
              key={product.id}
              product={product}
              onSave={onSave}
              onRemove={onRemove}
              onMoveStock={onMoveStock}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}