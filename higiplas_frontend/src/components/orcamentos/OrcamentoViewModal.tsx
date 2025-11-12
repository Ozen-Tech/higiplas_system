'use client';

import { Orcamento } from '@/types/orcamentos';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { X, Download } from 'lucide-react';

interface OrcamentoViewModalProps {
  orcamento: Orcamento;
  open: boolean;
  onClose: () => void;
  onDownloadPDF: () => void;
}

const statusColors: { [key: string]: 'default' | 'secondary' | 'destructive' | 'outline' } = {
  ENVIADO: 'secondary',
  APROVADO: 'default',
  REJEITADO: 'destructive',
  RASCUNHO: 'outline',
  FINALIZADO: 'default',
};

export function OrcamentoViewModal({
  orcamento,
  open,
  onClose,
  onDownloadPDF,
}: OrcamentoViewModalProps) {
  if (!open) return null;

  const calcularTotal = () => {
    if (!orcamento.itens) return 0;
    return orcamento.itens.reduce((acc, item) => acc + (item.quantidade * item.preco_unitario_congelado), 0);
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-800" onClick={(e) => e.stopPropagation()}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl">Detalhes do Orçamento #{orcamento.id}</CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X size={20} />
          </Button>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Informações Gerais */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Cliente</label>
              <p className="text-lg font-semibold">{orcamento.cliente.razao_social}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Vendedor</label>
              <p className="text-lg">{orcamento.usuario.nome}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Data de Criação</label>
              <p className="text-lg">{new Date(orcamento.data_criacao).toLocaleDateString('pt-BR')}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Status</label>
              <div className="mt-1">
                <Badge variant={statusColors[orcamento.status] || 'outline'}>
                  {orcamento.status}
                </Badge>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Condição de Pagamento</label>
              <p className="text-lg">{orcamento.condicao_pagamento}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Valor Total</label>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                R$ {calcularTotal().toFixed(2)}
              </p>
            </div>
          </div>

          {/* Itens do Orçamento */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Itens do Orçamento</h3>
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
                        <td className="px-4 py-2 text-center">{item.quantidade}</td>
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
            <Button variant="outline" onClick={onDownloadPDF}>
              <Download size={16} className="mr-2" />
              Baixar PDF
            </Button>
            <Button onClick={onClose}>Fechar</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

