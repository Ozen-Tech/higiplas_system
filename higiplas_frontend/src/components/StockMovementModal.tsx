"use client";

import { useState } from 'react';

// Definindo a "forma" dos dados que nosso componente espera receber (props)
interface StockMovementModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (tipo: 'entrada' | 'saida', quantidade: number) => void;
  productName: string;
}

export default function StockMovementModal({ isOpen, onClose, onSubmit, productName }: StockMovementModalProps) {
  const [tipo, setTipo] = useState<'entrada' | 'saida'>('entrada');
  const [quantidade, setQuantidade] = useState(1);

  if (!isOpen) {
    return null; // Se o modal não estiver aberto, não renderiza nada.
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(tipo, quantidade);
  };

  return (
    // Fundo semi-transparente que cobre a tela
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      {/* O card do modal */}
      <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Movimentar Estoque</h2>
        <p className="mb-4">Produto: <span className="font-semibold">{productName}</span></p>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="tipo" className="block text-sm font-medium text-gray-700">Tipo de Movimentação</label>
            <select
              id="tipo"
              value={tipo}
              onChange={(e) => setTipo(e.target.value as 'entrada' | 'saida')}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="entrada">Entrada</option>
              <option value="saida">Saída</option>
            </select>
          </div>

          <div className="mb-6">
            <label htmlFor="quantidade" className="block text-sm font-medium text-gray-700">Quantidade</label>
            <input
                type="number"
                id="quantidade"
                value={quantidade}
                onChange={(e) => {
                    // Converte o valor do input para um número
                    const num = parseInt(e.target.value, 10);
                    // Se o resultado for um número válido (não NaN) e maior que zero, atualiza o estado.
                    // Senão, mantém o valor anterior ou um valor padrão como 1.
                    if (!isNaN(num) && num > 0) {
                    setQuantidade(num);
                    } else {
                    // Se o usuário apagar tudo, podemos resetar para 1 ou deixar como está.
                    // Resetar para 1 é mais seguro.
                    setQuantidade(1); 
                    }
                }}
                min="1"
                className="mt-1 block w-full pl-3 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                required
                />
          </div>

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Confirmar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}