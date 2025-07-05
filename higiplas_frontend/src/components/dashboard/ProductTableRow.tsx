// /app/components/dashboard/ProductTableRow.tsx

import { Product, ProdutoUpdateData } from "@/types";
import { useState, ChangeEvent } from "react";

interface ProductTableRowProps {
  product: Product;
  onSave: (id: number, data: ProdutoUpdateData) => Promise<void>;
  onRemove: (id: number) => Promise<void>;
  onMoveStock: (product: Product) => void;
}

export function ProductTableRow({ product, onSave, onRemove, onMoveStock }: ProductTableRowProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState<Partial<Product>>(product);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    const finalValue = type === 'number' ? (value === '' ? null : parseFloat(value)) : value;
    setEditedData(prev => ({ ...prev, [name]: finalValue }));
  };

  const handleSave = async () => {
    await onSave(product.id, editedData);
    setIsEditing(false);
  };

  const getRowClassName = (p: Product) => {
    const classes = [];
    // Prioridade 1: Vencido
    if (p.data_validade) {
      const hoje = new Date();
      hoje.setHours(0, 0, 0, 0);
      const validade = new Date(p.data_validade + "T00:00:00");
      const diasRestantes = (validade.getTime() - hoje.getTime()) / (1000 * 3600 * 24);
      if (diasRestantes < 0) {
        classes.push("bg-red-100 dark:bg-red-900/20");
        return classes.join(" ");
      }
      if (diasRestantes <= 30) classes.push("bg-orange-100 dark:bg-orange-900/20");
    }
    // Prioridade 2: Estoque baixo
    if (p.quantidade_em_estoque <= (p.estoque_minimo ?? 0)) {
      classes.push("bg-yellow-100 dark:bg-yellow-900/20");
    }
    return classes.join(" ");
  };

  const inputClasses = "border rounded px-2 py-1 w-full bg-yellow-100 dark:bg-gray-600 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none";
  const textCenterInputClasses = `${inputClasses} text-center`;

  return (
    <tr className={`bg-white dark:bg-neutral-800 hover:bg-gray-50 dark:hover:bg-neutral-700/50 transition-colors duration-150 ${getRowClassName(product)}`}>
      {/* Nome */}
      <td className="px-6 py-4 whitespace-nowrap text-sm">
        {isEditing ? <input type="text" name="nome" value={editedData.nome || ''} onChange={handleInputChange} className={inputClasses}/> : <span className="font-medium text-gray-900 dark:text-gray-100">{product.nome}</span>}
      </td>
      {/* Código */}
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
        {isEditing ? <input type="text" name="codigo" value={editedData.codigo || ''} onChange={handleInputChange} className={`${inputClasses} w-28`}/> : product.codigo}
      </td>
      {/* Estoque Mínimo */}
      <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500 dark:text-gray-400">
        {isEditing ? <input type="number" name="estoque_minimo" value={editedData.estoque_minimo ?? ''} onChange={handleInputChange} className={`${textCenterInputClasses} w-20`}/> : product.estoque_minimo ?? 0}
      </td>
      {/* Qtde em Estoque */}
      <td className="px-6 py-4 whitespace-nowrap text-sm text-center font-bold text-gray-800 dark:text-gray-200">{product.quantidade_em_estoque}</td>
      {/* Data de Validade */}
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
        {isEditing ? <input type="date" name="data_validade" value={editedData.data_validade?.split('T')[0] || ''} onChange={handleInputChange} className={inputClasses}/> : (product.data_validade ? new Date(product.data_validade + 'T00:00:00').toLocaleDateString("pt-BR") : "-")}
      </td>
      {/* Ações */}
      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-4">
        {isEditing ? (
          <>
            <button onClick={handleSave} className="text-green-600 hover:text-green-500 font-semibold">Salvar</button>
            <button onClick={() => setIsEditing(false)} className="text-gray-500 hover:text-gray-300 font-semibold">Cancelar</button>
          </>
        ) : (
          <>
            <button onClick={() => setIsEditing(true)} className="text-indigo-600 hover:text-indigo-500 font-semibold">Editar</button>
            <button onClick={() => onMoveStock(product)} className="text-blue-600 hover:text-blue-500 font-semibold">Movimentar</button>
            <button onClick={() => onRemove(product.id)} className="text-red-600 hover:text-red-500 font-semibold">Remover</button>
          </>
        )}
      </td>
    </tr>
  );
}