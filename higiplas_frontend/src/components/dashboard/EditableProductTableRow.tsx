// /src/components/dashboard/EditableProductTableRow.tsx
'use client';

import { useState, ChangeEvent } from 'react';
import { Product, ProdutoUpdateData } from '@/types';
import Link from 'next/link';

interface EditableProductTableRowProps {
  product: Product;
  onSave: (id: number, data: ProdutoUpdateData) => Promise<void>;
  onRemove: (id: number) => Promise<void>;
  onMoveStock: (product: Product) => void;
}

export function EditableProductTableRow({ product, onSave, onRemove, onMoveStock }: EditableProductTableRowProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState<ProdutoUpdateData>({});

  const handleEditClick = () => {
    setEditedData({
      nome: product.nome,
      codigo: product.codigo,
      categoria: product.categoria,
      estoque_minimo: product.estoque_minimo,
      data_validade: product.data_validade,
      preco_venda: product.preco_venda,
      preco_custo: product.preco_custo,
    });
    setIsEditing(true);
  };

  const handleCancelClick = () => {
    setIsEditing(false);
    setEditedData({});
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    const finalValue = type === 'number' ? (value === '' ? null : parseFloat(value)) : value;
    setEditedData(prev => ({ ...prev, [name]: finalValue }));
  };

  const handleSave = async () => {
    await onSave(product.id, editedData);
    setIsEditing(false);
  };
  
  // Classes para os inputs de edição
  const inputClasses = "w-full rounded-md border-yellow-400 bg-yellow-50 dark:bg-gray-700 px-2 py-1 text-sm shadow-sm focus:border-indigo-500 focus:ring-indigo-500";
  const textCenterInputClasses = `${inputClasses} text-center`;

  return (
    <tr className="bg-white dark:bg-neutral-800 hover:bg-gray-50 dark:hover:bg-neutral-700/50 transition-colors duration-150">
      {/* Coluna Nome */}
      <td className="px-4 py-3 text-sm">
        {isEditing ? (
          <input type="text" name="nome" value={editedData.nome || ''} onChange={handleInputChange} className={inputClasses} />
        ) : (
          <span className="font-medium text-gray-900 dark:text-gray-100">{product.nome}</span>
        )}
      </td>
      {/* Coluna Código */}
      <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
        {isEditing ? (
          <input type="text" name="codigo" value={editedData.codigo || ''} onChange={handleInputChange} className={`${inputClasses} w-28`} />
        ) : (
          product.codigo
        )}
      </td>
      {/* Coluna Estoque */}
      <td className="px-4 py-3 text-sm text-center font-bold text-gray-800 dark:text-gray-200">
        {product.quantidade_em_estoque}
      </td>
      {/* Coluna Estoque Mínimo */}
      <td className="px-4 py-3 text-sm text-center text-gray-500 dark:text-gray-400">
        {isEditing ? (
            <input type="number" name="estoque_minimo" value={editedData.estoque_minimo ?? ''} onChange={handleInputChange} className={`${textCenterInputClasses} w-20`} />
        ) : (
            product.estoque_minimo ?? 'N/A'
        )}
      </td>
      {/* Coluna Preço de Venda */}
       <td className="px-4 py-3 text-sm text-right text-gray-500 dark:text-gray-400">
        {isEditing ? (
            <input type="number" step="0.01" name="preco_venda" value={editedData.preco_venda ?? ''} onChange={handleInputChange} className={`${inputClasses} text-right w-24`} />
        ) : (
            product.preco_venda.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
        )}
      </td>
      {/* Ações */}
      <td className="px-4 py-3 text-right text-sm font-medium">
        <div className="flex justify-end items-center gap-2 md:gap-4">
          {isEditing ? (
            <>
              <button onClick={handleSave} className="font-semibold text-green-600 hover:text-green-500">Salvar</button>
              <button onClick={handleCancelClick} className="font-semibold text-gray-500 hover:text-gray-400">Cancelar</button>
            </>
          ) : (
            <>
              <Link href={`/dashboard/history/${product.id}`} className="font-semibold text-gray-500 hover:text-gray-400">Histórico</Link>
              <button onClick={handleEditClick} className="font-semibold text-indigo-600 hover:text-indigo-500">Editar</button>
              <button onClick={() => onMoveStock(product)} className="font-semibold text-blue-600 hover:text-blue-500">Movimentar</button>
              <button onClick={() => onRemove(product.id)} className="font-semibold text-red-600 hover:text-red-500">Remover</button>
            </>
          )}
        </div>
      </td>
    </tr>
  );
}