'use client';

import { Cliente } from '@/types/vendas';
import { ItemCarrinhoOrcamento } from '@/types/orcamentos';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Share2, Download, CheckCircle } from 'lucide-react';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';

interface OrcamentoReviewProps {
  cliente: Cliente;
  carrinho: ItemCarrinhoOrcamento[];
  condicaoPagamento: string;
  total: number;
  onVoltar: () => void;
  onFinalizar: () => void;
  orcamentoId?: number;
  loading?: boolean;
}

export function OrcamentoReview({
  cliente,
  carrinho,
  condicaoPagamento,
  total,
  onVoltar,
  onFinalizar,
  orcamentoId,
  loading = false,
}: OrcamentoReviewProps) {
  const handleDownloadPDF = async () => {
    if (!orcamentoId) return;

    toast.loading('Gerando PDF...');
    try {
      const response = await apiService.getBlob(`/orcamentos/${orcamentoId}/pdf/`);
      const blob = await response.blob();

      const contentDisposition = response.headers.get('content-disposition');
      let filename = `orcamento_${orcamentoId}.pdf`;
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

  const handleShareWhatsApp = () => {
    if (!cliente.telefone) {
      toast.error('Cliente não possui telefone cadastrado');
      return;
    }

    const mensagem = `Olá, ${cliente.nome}! Segue o orçamento solicitado. Estou à disposição para qualquer dúvida.`;
    const fone = cliente.telefone.replace(/\D/g, '');
    const whatsappUrl = `https://wa.me/55${fone}?text=${encodeURIComponent(mensagem)}`;
    window.open(whatsappUrl, '_blank');
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle size={20} className="text-green-600" /> Revisão do Orçamento
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Cliente */}
          <div>
            <h3 className="font-semibold mb-2">Cliente</h3>
            <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <p className="font-medium">{cliente.nome}</p>
              {cliente.telefone && (
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {cliente.telefone}
                </p>
              )}
            </div>
          </div>

          {/* Itens */}
          <div>
            <h3 className="font-semibold mb-2">Itens do Orçamento</h3>
            <div className="space-y-2">
              {carrinho.map((item) => (
                <div
                  key={item.produto_id}
                  className="p-3 border rounded-lg flex justify-between items-center"
                >
                  <div className="flex-1">
                    <p className="font-medium">{item.nome}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {item.quantidade} x R$ {item.preco_unitario_editavel.toFixed(2)}
                    </p>
                  </div>
                  <p className="font-semibold">
                    R$ {(item.quantidade * item.preco_unitario_editavel).toFixed(2)}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Condições */}
          <div>
            <h3 className="font-semibold mb-2">Condições</h3>
            <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <p>Pagamento: {condicaoPagamento}</p>
            </div>
          </div>

          {/* Total */}
          <div className="border-t pt-4">
            <div className="flex justify-between items-center">
              <span className="text-xl font-semibold">Total:</span>
              <span className="text-2xl font-bold text-green-600 dark:text-green-400">
                R$ {total.toFixed(2)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Ações */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Button
          variant="outline"
          onClick={onVoltar}
          className="flex-1"
        >
          Voltar e Editar
        </Button>
        {orcamentoId && (
          <>
            <Button
              variant="outline"
              onClick={handleDownloadPDF}
              className="flex-1 gap-2"
            >
              <Download size={16} /> Baixar PDF
            </Button>
            <Button
              onClick={handleShareWhatsApp}
              className="flex-1 gap-2"
              style={{ backgroundColor: '#25D366', color: 'white' }}
            >
              <Share2 size={16} /> WhatsApp
            </Button>
          </>
        )}
        {!orcamentoId && (
          <Button
            onClick={onFinalizar}
            disabled={loading}
            className="flex-1 gap-2"
          >
            {loading ? 'Salvando...' : 'Finalizar Orçamento'}
          </Button>
        )}
      </div>
    </div>
  );
}

