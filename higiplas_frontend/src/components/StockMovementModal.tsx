"use client";

import { useState, useEffect } from "react";

interface StockMovementModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (tipo: "entrada" | "saida", quantidade: number, observacao?: string) => void;
  productName: string;
}

export default function StockMovementModal({
  isOpen,
  onClose,
  onSubmit,
  productName,
}: StockMovementModalProps) {
  const [tipo, setTipo] = useState<"entrada" | "saida">("entrada");
  const [quantidade, setQuantidade] = useState<number>(1);
  const [observacao, setObservacao] = useState<string>("");
  const [error, setError] = useState<string>("");

  // Resetar campos quando abrir modal
  useEffect(() => {
    if (isOpen) {
      setTipo("entrada");
      setQuantidade(1);
      setObservacao("");
      setError("");
    }
  }, [isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (quantidade < 1) {
      setError("Quantidade deve ser maior que zero.");
      return;
    }

    setError("");
    onSubmit(tipo, quantidade, observacao.trim() || undefined);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Movimentar Estoque</h2>
        <p className="mb-4">
          Produto: <span className="font-semibold">{productName}</span>
        </p>

        <form onSubmit={handleSubmit} noValidate>
          <div className="mb-4">
            <label
              htmlFor="tipo"
              className="block text-sm font-medium text-gray-700"
            >
              Tipo de Movimentação
            </label>
            <select
              id="tipo"
              value={tipo}
              onChange={(e) => setTipo(e.target.value as "entrada" | "saida")}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="entrada">Entrada</option>
              <option value="saida">Saída</option>
            </select>
          </div>

          <div className="mb-4">
            <label
              htmlFor="quantidade"
              className="block text-sm font-medium text-gray-700"
            >
              Quantidade
            </label>
            <input
              type="number"
              id="quantidade"
              min={1}
              value={quantidade}
              onChange={(e) => {
                const val = parseInt(e.target.value, 10);
                if (!isNaN(val) && val > 0) {
                  setQuantidade(val);
                  setError("");
                } else {
                  setQuantidade(1);
                  setError("Quantidade deve ser maior que zero.");
                }
              }}
              className="mt-1 block w-full pl-3 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              required
            />
          </div>

          <div className="mb-4">
            <label
              htmlFor="observacao"
              className="block text-sm font-medium text-gray-700"
            >
              Observação (opcional)
            </label>
            <textarea
              id="observacao"
              rows={3}
              value={observacao}
              onChange={(e) => setObservacao(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm resize-none"
              placeholder="Ex: Nota fiscal, motivo da movimentação, etc."
            />
          </div>

          {error && (
            <p className="text-red-600 text-sm mb-4 font-semibold">{error}</p>
          )}

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