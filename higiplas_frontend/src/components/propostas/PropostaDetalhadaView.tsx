// src/components/propostas/PropostaDetalhadaView.tsx

'use client';

import { PropostaDetalhada } from '@/services/propostaService';
import { FichaTecnicaCard } from './FichaTecnicaCard';
import { ComparacaoConcorrentes } from './ComparacaoConcorrentes';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calculator, TrendingUp, DollarSign, Share2, Copy, Download, Columns4 } from 'lucide-react';
import toast from 'react-hot-toast';
import { apiService } from '@/services/apiService';

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

  const handleDownloadPDF = async () => {
    toast.loading('Gerando PDF...');
    try {
      const response = await apiService.getBlob(`/propostas-detalhadas/${proposta.id}/pdf/`);
      const blob = await response.blob();

      const contentDisposition = response.headers.get('content-disposition');
      let filename = `proposta_detalhada_${proposta.id}.pdf`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch && filenameMatch.length > 1) {
          filename = filenameMatch[1];
        }
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();

      toast.dismiss();
      toast.success('PDF baixado com sucesso!');

      setTimeout(() => {
        window.URL.revokeObjectURL(url);
        link.remove();
      }, 100);
    } catch (error) {
      toast.dismiss();
      toast.error('Erro ao gerar PDF');
      console.error('Erro no download:', error);
    }
  };

  const totalRendimento = proposta.itens.reduce(
    (acc, item) => acc + (item.rendimento_total_litros || 0),
    0
  );
  const custoMedio =
    proposta.itens.filter((item) => item.custo_por_litro_final).length > 0
      ? proposta.itens
          .filter((item) => item.custo_por_litro_final)
          .reduce((acc, item) => acc + (item.custo_por_litro_final || 0), 0) /
        proposta.itens.filter((item) => item.custo_por_litro_final).length
      : null;

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
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleDownloadPDF} size="sm">
                <Download className="mr-2 h-4 w-4" />
                Baixar PDF
              </Button>
              {proposta.compartilhavel && proposta.token_compartilhamento && (
                <Button variant="outline" onClick={copiarLink} size="sm">
                  <Copy className="mr-2 h-4 w-4" />
                  Copiar Link
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Cliente</p>
              <p className="font-semibold">{proposta.cliente_nome || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Produtos Higiplas</p>
              <p className="font-semibold">{proposta.itens.length} selecionado(s)</p>
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
              Resumo de Rendimentos
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Rendimento total</p>
              <div className="flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-green-600" />
                <p className="text-3xl font-bold text-green-600">
                  {totalRendimento.toFixed(2)} L
                </p>
              </div>
            </div>
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Custo médio final</p>
              <div className="flex items-center gap-2">
                <DollarSign className="h-6 w-6 text-blue-600" />
                <p className="text-3xl font-bold text-blue-600">
                  {custoMedio ? `R$ ${custoMedio.toFixed(2)}` : 'N/A'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <FichaTecnicaCard ficha={proposta.ficha_tecnica || null} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Columns4 className="h-5 w-5" />
            Tabela comparativa (Higiplas x Cliente)
          </CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="bg-gray-100 dark:bg-gray-800 text-left">
                <th className="px-3 py-2">Produto Higiplas</th>
                <th className="px-3 py-2">Rendimento (L)</th>
                <th className="px-3 py-2">Custo/L (R$)</th>
                <th className="px-3 py-2">Concorrente citado</th>
                <th className="px-3 py-2">Rendimento concorrente</th>
                <th className="px-3 py-2">Custo concorrente (R$)</th>
              </tr>
            </thead>
            <tbody>
              {proposta.itens.map((item) => (
                <tr key={item.id} className="border-b dark:border-gray-800">
                  <td className="px-3 py-3">
                    <p className="font-medium">{item.produto_nome || proposta.produto_nome || 'Produto Higiplas'}</p>
                    {item.dilucao_aplicada && (
                      <p className="text-xs text-gray-500">Diluição {item.dilucao_aplicada}</p>
                    )}
                  </td>
                  <td className="px-3 py-3">{item.rendimento_total_litros ? `${item.rendimento_total_litros.toFixed(2)} L` : 'N/A'}</td>
                  <td className="px-3 py-3">{item.custo_por_litro_final ? `R$ ${item.custo_por_litro_final.toFixed(2)}` : 'N/A'}</td>
                  <td className="px-3 py-3">{item.concorrente_nome_manual || 'Não informado'}</td>
                  <td className="px-3 py-3">
                    {item.concorrente_rendimento_manual ? `${item.concorrente_rendimento_manual.toFixed(2)} L` : 'N/A'}
                  </td>
                  <td className="px-3 py-3">
                    {item.concorrente_custo_por_litro_manual ? `R$ ${item.concorrente_custo_por_litro_manual.toFixed(2)}` : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

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

      {proposta.comparacoes_personalizadas && proposta.comparacoes_personalizadas.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Produtos concorrentes cadastrados</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {proposta.comparacoes_personalizadas.map((comp) => (
              <div key={comp.id} className="border rounded-lg p-3">
                <p className="font-semibold">{comp.nome}</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm text-gray-600 dark:text-gray-400 mt-2">
                  <span>Rendimento: {comp.rendimento_litro ? `${comp.rendimento_litro.toFixed(2)} L` : 'N/A'}</span>
                  <span>Custo/L: {comp.custo_por_litro ? `R$ ${comp.custo_por_litro.toFixed(2)}` : 'N/A'}</span>
                  {comp.observacoes && <span>Notas: {comp.observacoes}</span>}
                </div>
              </div>
            ))}
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

