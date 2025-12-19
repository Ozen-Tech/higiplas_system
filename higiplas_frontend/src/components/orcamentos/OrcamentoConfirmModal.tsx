'use client';

import { useState } from 'react';
import { Orcamento } from '@/types/orcamentos';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert } from '@/components/ui/alert';
import { X, AlertTriangle, CheckCircle, Info } from 'lucide-react';

interface OrcamentoConfirmModalProps {
  orcamento: Orcamento;
  open: boolean;
  onClose: () => void;
  onConfirm: (baixarEstoque: boolean) => void;
  userPerfil?: string; // Perfil do usuário (ADMIN, GESTOR, VENDEDOR)
}

export function OrcamentoConfirmModal({
  orcamento,
  open,
  onClose,
  onConfirm,
  userPerfil = 'VENDEDOR',
}: OrcamentoConfirmModalProps) {
  const [confirmando, setConfirmando] = useState(false);
  const [naoBaixarEstoque, setNaoBaixarEstoque] = useState(false);
  
  // Apenas Admin/Gestor podem usar a opção de não baixar estoque
  const podeNaoBaixarEstoque = ['ADMIN', 'GESTOR'].includes(userPerfil.toUpperCase());

  if (!open) return null;

  const calcularTotal = () => {
    if (!orcamento.itens) return 0;
    return orcamento.itens.reduce((acc, item) => acc + (item.quantidade * item.preco_unitario_congelado), 0);
  };

  const handleConfirm = async () => {
    setConfirmando(true);
    try {
      // Passa true para baixar estoque (comportamento padrão), false se checkbox marcado
      await onConfirm(!naoBaixarEstoque);
    } finally {
      setConfirmando(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <Card className="w-full max-w-3xl max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-800" onClick={(e) => e.stopPropagation()}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl flex items-center gap-2">
            <CheckCircle size={24} className="text-green-600" />
            Confirmar Orçamento e Dar Baixa no Estoque
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose} disabled={confirmando}>
            <X size={20} />
          </Button>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Alerta */}
          <Alert className={`${naoBaixarEstoque ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800' : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'}`}>
            {naoBaixarEstoque ? (
              <Info className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
            )}
            <div className="ml-2">
              {naoBaixarEstoque ? (
                <>
                  <p className="font-semibold text-blue-800 dark:text-blue-200">
                    Confirmação sem baixa de estoque
                  </p>
                  <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                    O estoque NÃO será alterado. Use esta opção apenas quando a NF já foi lançada pela aba de movimentações.
                    O histórico de preços do cliente será registrado normalmente.
                  </p>
                </>
              ) : (
                <>
                  <p className="font-semibold text-yellow-800 dark:text-yellow-200">
                    Atenção: Esta ação não pode ser desfeita!
                  </p>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                    Ao confirmar, o estoque será reduzido automaticamente para todos os produtos deste orçamento.
                  </p>
                </>
              )}
            </div>
          </Alert>
          
          {/* Opção de não baixar estoque (apenas Admin/Gestor) */}
          {podeNaoBaixarEstoque && (
            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border">
              <input
                type="checkbox"
                id="naoBaixarEstoque"
                checked={naoBaixarEstoque}
                onChange={(e) => setNaoBaixarEstoque(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <label htmlFor="naoBaixarEstoque" className="text-sm cursor-pointer">
                <span className="font-medium">Não baixar estoque</span>
                <span className="text-gray-500 dark:text-gray-400 ml-1">
                  (usar quando a NF já foi lançada nas movimentações)
                </span>
              </label>
            </div>
          )}

          {/* Resumo do Orçamento */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Resumo do Orçamento #{orcamento.id}</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Cliente:</span>
                <span className="font-medium">{orcamento.cliente.razao_social}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Vendedor:</span>
                <span className="font-medium">{orcamento.usuario.nome}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Valor Total:</span>
                <span className="text-xl font-bold text-green-600 dark:text-green-400">
                  R$ {calcularTotal().toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Itens que serão dados baixa */}
          <div>
            <h3 className="text-lg font-semibold mb-4">
              {naoBaixarEstoque 
                ? 'Itens do orçamento (estoque NÃO será alterado):' 
                : 'Itens que serão dados baixa no estoque:'
              }
            </h3>
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-100 dark:bg-gray-700">
                  <tr>
                    <th className="px-4 py-2 text-left text-sm font-medium">Produto</th>
                    <th className="px-4 py-2 text-center text-sm font-medium">Quantidade</th>
                    <th className="px-4 py-2 text-right text-sm font-medium">Preço Unit.</th>
                    <th className="px-4 py-2 text-right text-sm font-medium">Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {orcamento.itens.map((item, index) => {
                    const subtotal = item.quantidade * item.preco_unitario_congelado;
                    return (
                      <tr key={item.id || index} className="border-t dark:border-gray-700">
                        <td className="px-4 py-2">
                          <div>
                            <p className="font-medium">{item.produto.nome}</p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              Código: {item.produto.codigo}
                            </p>
                          </div>
                        </td>
                        <td className="px-4 py-2 text-center">
                          <span className={`font-semibold ${naoBaixarEstoque ? 'text-gray-600 dark:text-gray-400' : 'text-red-600 dark:text-red-400'}`}>
                            {naoBaixarEstoque ? item.quantidade : `-${item.quantidade}`}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-right">
                          R$ {item.preco_unitario_congelado.toFixed(2)}
                        </td>
                        <td className="px-4 py-2 text-right font-semibold">
                          R$ {subtotal.toFixed(2)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Ações */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="outline" onClick={onClose} disabled={confirmando}>
              Cancelar
            </Button>
            <Button 
              onClick={handleConfirm} 
              disabled={confirmando}
              className={naoBaixarEstoque ? "bg-blue-600 hover:bg-blue-700" : "bg-green-600 hover:bg-green-700"}
            >
              {confirmando 
                ? 'Confirmando...' 
                : naoBaixarEstoque 
                  ? 'Confirmar (Sem Baixa de Estoque)' 
                  : 'Confirmar e Dar Baixa no Estoque'
              }
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

