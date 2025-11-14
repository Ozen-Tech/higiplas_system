// src/components/propostas/ComparacaoConcorrentes.tsx

'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ComparacaoConcorrente } from '@/services/propostaService';
import { TrendingDown, DollarSign } from 'lucide-react';

interface ComparacaoConcorrentesProps {
  comparacoes: ComparacaoConcorrente[];
  produtoGirassol: {
    nome: string;
    preco?: number;
    custoPorLitro?: number;
  };
}

export function ComparacaoConcorrentes({ comparacoes, produtoGirassol }: ComparacaoConcorrentesProps) {
  if (!comparacoes || comparacoes.length === 0) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-gray-500 dark:text-gray-400 text-center">
            Nenhuma comparação disponível com concorrentes
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Comparação com Concorrentes</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">Produto</th>
                <th className="text-right p-2">Preço</th>
                <th className="text-right p-2">Custo/Litro</th>
                <th className="text-right p-2">Economia</th>
              </tr>
            </thead>
            <tbody>
              {/* Produto Girassol */}
              <tr className="bg-blue-50 dark:bg-blue-900/20 border-b">
                <td className="p-2 font-semibold">{produtoGirassol.nome}</td>
                <td className="text-right p-2">
                  {produtoGirassol.preco ? `R$ ${produtoGirassol.preco.toFixed(2)}` : '-'}
                </td>
                <td className="text-right p-2">
                  {produtoGirassol.custoPorLitro ? `R$ ${produtoGirassol.custoPorLitro.toFixed(2)}` : '-'}
                </td>
                <td className="text-right p-2">
                  <span className="text-green-600 dark:text-green-400 font-semibold">Referência</span>
                </td>
              </tr>

              {/* Concorrentes */}
              {comparacoes.map((comp) => (
                <tr key={comp.concorrente_id} className="border-b hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td className="p-2">
                    <div>
                      <p className="font-medium">{comp.concorrente_nome}</p>
                      {comp.concorrente_marca && (
                        <p className="text-xs text-gray-500 dark:text-gray-400">{comp.concorrente_marca}</p>
                      )}
                    </div>
                  </td>
                  <td className="text-right p-2">
                    {comp.preco_concorrente ? `R$ ${comp.preco_concorrente.toFixed(2)}` : '-'}
                  </td>
                  <td className="text-right p-2">
                    {comp.custo_por_litro_concorrente ? `R$ ${comp.custo_por_litro_concorrente.toFixed(2)}` : '-'}
                  </td>
                  <td className="text-right p-2">
                    {comp.economia_percentual !== null && comp.economia_percentual !== undefined ? (
                      <div className="flex items-center justify-end gap-1">
                        <TrendingDown className="h-4 w-4 text-green-600" />
                        <span className="font-semibold text-green-600 dark:text-green-400">
                          {comp.economia_percentual.toFixed(1)}%
                        </span>
                        {comp.economia_valor && (
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            (R$ {comp.economia_valor.toFixed(2)})
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Resumo */}
        {comparacoes.length > 0 && comparacoes[0].economia_percentual && (
          <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-green-600" />
              <div>
                <p className="font-semibold text-green-800 dark:text-green-300">
                  Economia média de {comparacoes[0].economia_percentual.toFixed(1)}%
                </p>
                {comparacoes[0].economia_valor && (
                  <p className="text-sm text-green-700 dark:text-green-400">
                    Economia de R$ {comparacoes[0].economia_valor.toFixed(2)} por litro
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

