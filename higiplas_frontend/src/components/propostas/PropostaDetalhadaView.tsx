// src/components/propostas/PropostaDetalhadaView.tsx

'use client';

import { PropostaDetalhada } from '@/services/propostaService';
import { FichaTecnicaCard } from './FichaTecnicaCard';
import { ComparacaoConcorrentes } from './ComparacaoConcorrentes';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calculator, TrendingUp, DollarSign, Share2, Copy } from 'lucide-react';
import toast from 'react-hot-toast';

interface PropostaDetalhadaViewProps {
  proposta: PropostaDetalhada;
  onCompartilhar?: () => void;
}

export function PropostaDetalhadaView({ proposta, onCompartilhar }: PropostaDetalhadaViewProps) {
  const copiarLink = () => {
    if (proposta.token_compartilhamento) {
      const link = `${window.location.origin}/propostas/compartilhar/${proposta.token_compartilhamento}`;
      navigator.clipboard.writeText(link);
      toast.success('Link copiado para a área de transferência!');
    }
  };

  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Proposta Detalhada #{proposta.id}</CardTitle>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Criada em {new Date(proposta.data_criacao).toLocaleDateString('pt-BR')}
              </p>
            </div>
            {proposta.compartilhavel && proposta.token_compartilhamento && (
              <Button variant="outline" onClick={copiarLink} size="sm">
                <Copy className="mr-2 h-4 w-4" />
                Copiar Link
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Cliente</p>
              <p className="font-semibold">{proposta.cliente_nome || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Produto</p>
              <p className="font-semibold">{proposta.produto_nome || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Vendedor</p>
              <p className="font-semibold">{proposta.vendedor_nome || 'N/A'}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Informações Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              Cálculos de Rendimento
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Quantidade do Produto</p>
              <p className="text-2xl font-bold">{proposta.quantidade_produto} {proposta.dilucao_aplicada ? 'litro(s)' : 'unidade(s)'}</p>
            </div>

            {proposta.dilucao_aplicada && (
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Diluição Aplicada</p>
                <p className="text-xl font-semibold">{proposta.dilucao_aplicada}</p>
              </div>
            )}

            {proposta.rendimento_total_litros && (
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Rendimento Total</p>
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                  <p className="text-3xl font-bold text-green-600">
                    {proposta.rendimento_total_litros.toFixed(2)} litros
                  </p>
                </div>
              </div>
            )}

            {proposta.custo_por_litro_final && (
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Custo por Litro Final</p>
                <div className="flex items-center gap-2">
                  <DollarSign className="h-6 w-6 text-blue-600" />
                  <p className="text-3xl font-bold text-blue-600">
                    R$ {proposta.custo_por_litro_final.toFixed(2)}
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Ficha Técnica */}
        <FichaTecnicaCard ficha={proposta.ficha_tecnica || null} />
      </div>

      {/* Comparação com Concorrentes */}
      {proposta.comparacoes && proposta.comparacoes.length > 0 && (
        <ComparacaoConcorrentes
          comparacoes={proposta.comparacoes}
          produtoGirassol={{
            nome: proposta.produto_nome || 'Produto Girassol',
            preco: proposta.preco_produto,
            custoPorLitro: proposta.custo_por_litro_final || undefined,
          }}
        />
      )}

      {/* Economia */}
      {proposta.economia_percentual && (
        <Card className="bg-green-50 dark:bg-green-900/20">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 dark:bg-green-800 rounded-full">
                <TrendingUp className="h-8 w-8 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Economia vs Concorrente</p>
                <p className="text-3xl font-bold text-green-600">
                  {proposta.economia_percentual.toFixed(1)}%
                </p>
                {proposta.economia_valor && (
                  <p className="text-sm text-green-700 dark:text-green-400">
                    Economia de R$ {proposta.economia_valor.toFixed(2)} por litro
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Observações */}
      {proposta.observacoes && (
        <Card>
          <CardHeader>
            <CardTitle>Observações</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
              {proposta.observacoes}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Botão Compartilhar */}
      {!proposta.compartilhavel && onCompartilhar && (
        <div className="flex justify-end">
          <Button onClick={onCompartilhar} variant="outline">
            <Share2 className="mr-2 h-4 w-4" />
            Gerar Link Compartilhável
          </Button>
        </div>
      )}
    </div>
  );
}

