"use client";

import { PurchaseSuggestion } from '@/types';
import { useRouter } from 'next/navigation';

interface PurchaseSuggestionCardProps {
  suggestion: PurchaseSuggestion;
  onSelect?: (produtoId: number) => void;
  isSelected?: boolean;
}

export function PurchaseSuggestionCard({ 
  suggestion, 
  onSelect, 
  isSelected = false 
}: PurchaseSuggestionCardProps) {
  const router = useRouter();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'CRÍTICO':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 border-red-300 dark:border-red-700';
      case 'BAIXO':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 border-yellow-300 dark:border-yellow-700';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 border-gray-300 dark:border-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'CRÍTICO':
        return '🔴';
      case 'BAIXO':
        return '🟡';
      default:
        return '🟢';
    }
  };

  const handleCreateOrder = () => {
    router.push(`/dashboard/compras/nova-oc?productIds=${suggestion.produto_id}&quantidade=${suggestion.quantidade_sugerida}`);
  };

  return (
    <div className={`border rounded-lg p-4 dark:bg-gray-800 dark:border-gray-700 ${
      isSelected ? 'ring-2 ring-blue-500 border-blue-500' : ''
    }`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xl">{getStatusIcon(suggestion.status)}</span>
            <h3 className="font-semibold text-lg text-gray-900 dark:text-gray-100">
              {suggestion.produto_nome}
            </h3>
            <span className={`px-2 py-1 text-xs font-semibold rounded-full border ${getStatusColor(suggestion.status)}`}>
              {suggestion.status}
            </span>
          </div>
          {suggestion.codigo && (
            <p className="text-sm text-gray-500 dark:text-gray-400">Código: {suggestion.codigo}</p>
          )}
          {suggestion.categoria && (
            <p className="text-sm text-gray-500 dark:text-gray-400">Categoria: {suggestion.categoria}</p>
          )}
          {suggestion.fornecedor_nome && (
            <p className="text-sm text-gray-500 dark:text-gray-400">Fornecedor: {suggestion.fornecedor_nome}</p>
          )}
        </div>
        {onSelect && (
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => onSelect(suggestion.produto_id)}
            className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Estoque Atual</p>
          <p className="text-lg font-bold text-red-600 dark:text-red-400">
            {suggestion.estoque_atual}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Estoque Mínimo</p>
          <p className="text-lg font-semibold text-gray-700 dark:text-gray-300">
            {suggestion.estoque_minimo_calculado}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Demanda Média Diária</p>
          <p className="text-lg font-semibold text-gray-700 dark:text-gray-300">
            {suggestion.demanda_media_diaria.toFixed(2)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Dias de Cobertura</p>
          <p className={`text-lg font-semibold ${
            suggestion.dias_cobertura_atual < 7 ? 'text-red-600 dark:text-red-400' :
            suggestion.dias_cobertura_atual < 14 ? 'text-yellow-600 dark:text-yellow-400' :
            'text-green-600 dark:text-green-400'
          }`}>
            {suggestion.dias_cobertura_atual.toFixed(1)} dias
          </p>
        </div>
      </div>

      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 mb-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-1">
              Quantidade Sugerida de Compra
            </p>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {suggestion.quantidade_sugerida} unidades
            </p>
            {suggestion.preco_custo && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Valor estimado: R$ {suggestion.valor_estimado_compra.toFixed(2)}
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 dark:text-gray-400 mb-3">
        <div>
          <span className="font-semibold">Total vendido (90 dias):</span> {suggestion.total_vendido_periodo.toFixed(2)}
        </div>
        <div>
          <span className="font-semibold">Número de vendas:</span> {suggestion.numero_vendas}
        </div>
        <div>
          <span className="font-semibold">Dias com vendas:</span> {suggestion.dias_com_vendas}
        </div>
        <div>
          <span className="font-semibold">Demanda máxima diária:</span> {suggestion.demanda_maxima_diaria.toFixed(2)}
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleCreateOrder}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          Criar Ordem de Compra
        </button>
        {onSelect && (
          <button
            onClick={() => onSelect(suggestion.produto_id)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              isSelected
                ? 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            {isSelected ? 'Selecionado' : 'Selecionar'}
          </button>
        )}
      </div>
    </div>
  );
}

