import { Product, ProdutoUpdateData } from "@/types";
import { useState, ChangeEvent } from "react";
import Link from 'next/link';

interface ProductTableRowProps {
  product: Product;
  onSave: (id: number, data: ProdutoUpdateData) => Promise<void>;
  onRemove: (id: number) => Promise<void>;
  onMoveStock: (product: Product) => void;
}

export function ProductTableRow({ product, onSave, onRemove, onMoveStock }: ProductTableRowProps) {
  const [isEditing, setIsEditing] = useState(false);
  // Garante que editedData sempre tem os dados mais recentes do produto quando o modo de edição começa
  const [editedData, setEditedData] = useState<ProdutoUpdateData>({});

  const handleEditClick = () => {
    setEditedData({
        nome: product.nome,
        codigo: product.codigo,
        estoque_minimo: product.estoque_minimo,
        data_validade: product.data_validade,
    });
    setIsEditing(true);
  };
  
  const handleCancelClick = () => {
    setIsEditing(false);
    setEditedData({}); // Limpa os dados editados
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    // Lida com números e datas
    const finalValue = type === 'number' ? (value === '' ? null : parseFloat(value)) : value;
    setEditedData(prev => ({ ...prev, [name]: finalValue }));
  };

  const handleSave = async () => {
    await onSave(product.id, editedData);
    setIsEditing(false);
  };

  const getRowClassName = (product: Product) => { // Renomeei o parâmetro para 'product' para clareza
    const classes = [];

    // Prioridade 1: Vencido ou perto de vencer
    if (product.data_validade) {
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0); // Zera o tempo para comparar apenas as datas

        // Adiciona T00:00:00 para evitar problemas de fuso horário
        const validade = new Date(product.data_validade + "T00:00:00"); 

        const diasRestantes = (validade.getTime() - hoje.getTime()) / (1000 * 3600 * 24);

        if (diasRestantes < 0) {
            // Se já venceu, a classe de vencimento tem prioridade máxima
            return "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300"; 
        }
        if (diasRestantes <= 30) {
            classes.push("bg-orange-100 dark:bg-orange-900/30"); // Próximo ao vencimento
        }
    }
    
    // Prioridade 2: Estoque baixo (se não estiver vencido)
    if (product.quantidade_em_estoque <= (product.estoque_minimo ?? 0)) {
        classes.push("bg-yellow-100 dark:bg-yellow-900/30"); // Estoque baixo
    }

    return classes.join(" "); // Retorna a string de classes CSS
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
      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
        {isEditing ? (
          <>
            <button onClick={handleSave} className="text-green-600 hover:text-green-500 font-semibold px-2">Salvar</button>
            <button onClick={handleCancelClick} className="text-gray-500 hover:text-gray-300 font-semibold px-2">Cancelar</button>
          </>
        ) : (
          <>
            {/* --- LINK PARA HISTÓRICO ADICIONADO AQUI --- */}
            <Link href={`/dashboard/history/${product.id}`} className="text-gray-500 hover:text-gray-400 font-semibold px-2">
              Histórico
            </Link>
            <button onClick={handleEditClick} className="text-indigo-600 hover:text-indigo-500 font-semibold px-2">Editar</button>
            <button onClick={() => onMoveStock(product)} className="text-blue-600 hover:text-blue-500 font-semibold px-2">Movimentar</button>
            <button onClick={() => onRemove(product.id)} className="text-red-600 hover:text-red-500 font-semibold px-2">Remover</button>
          </>
        )}
      </td>
    </tr>
  );
}