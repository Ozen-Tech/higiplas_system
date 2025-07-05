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
      setError("A quantidade deve ser maior que zero.");
      return;
    }
    setError("");
    onSubmit(tipo, quantidade, observacao.trim() || undefined);
  };

  if (!isOpen) return null;

  // --- Classes de estilo reutilizáveis para os inputs ---
  const inputBaseClasses = "mt-1 block w-full border rounded-md shadow-sm focus:outline-none focus:ring-2 sm:text-sm";
  const inputColorClasses = "border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-indigo-500 focus:border-indigo-500";
  const labelClasses = "block text-sm font-medium text-gray-700 dark:text-gray-300";

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 transition-opacity">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-full max-w-md border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold mb-2 text-gray-900 dark:text-gray-100">Movimentar Estoque</h2>
        <p className="mb-6 text-gray-600 dark:text-gray-400">
          Produto: <span className="font-semibold text-gray-800 dark:text-gray-200">{productName}</span>
        </p>

        <form onSubmit={handleSubmit} noValidate>
          <div className="space-y-4">
            <div>
              <label htmlFor="tipo" className={labelClasses}>
                Tipo de Movimentação
              </label>
              <select
                id="tipo"
                value={tipo}
                onChange={(e) => setTipo(e.target.value as "entrada" | "saida")}
                className={`${inputBaseClasses} ${inputColorClasses} pl-3 pr-10 py-2 text-base`}
              >
                <option value="entrada">Entrada</option>
                <option value="saida">Saída</option>
              </select>
            </div>

            <div>
              <label htmlFor="quantidade" className={labelClasses}>
                Quantidade
              </label>
              <input
                type="number"
                id="quantidade"
                min={1}
                value={quantidade}
                onChange={(e) => setQuantidade(Math.max(1, parseInt(e.target.value, 10) || 1))}
                className={`${inputBaseClasses} ${inputColorClasses} px-3 py-2`}
                required
              />
            </div>

            <div>
              <label htmlFor="observacao" className={labelClasses}>
                Observação (opcional)
              </label>
              <textarea
                id="observacao"
                rows={3}
                value={observacao}
                onChange={(e) => setObservacao(e.target.value)}
                className={`${inputBaseClasses} ${inputColorClasses} px-3 py-2 resize-none`}
                placeholder="Ex: Nota fiscal, motivo da movimentação, etc."
              />
            </div>
          </div>

          {error && (
            <p className="text-red-500 text-sm mt-4 font-semibold">{error}</p>
          )}

          <div className="mt-8 flex justify-end space-x-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-100 rounded-md hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
            >
              Confirmar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}