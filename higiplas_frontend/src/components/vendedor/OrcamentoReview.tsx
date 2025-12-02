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

  const handleShareWhatsApp = async () => {
    if (!cliente.telefone) {
      toast.error('Cliente não possui telefone cadastrado');
      return;
    }

    if (!orcamentoId) {
      toast.error('Orçamento não encontrado');
      return;
    }

    try {
      // Buscar o orçamento para obter o token de compartilhamento
      const response = await apiService.get(`/orcamentos/${orcamentoId}`);
      const orcamento = response?.data || response;
      
      if (!orcamento?.token_compartilhamento) {
        toast.error('Token de compartilhamento não disponível');
        return;
      }

      // Construir URL do PDF público
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;
      const pdfUrl = `${API_BASE_URL}/orcamentos/${orcamentoId}/pdf/public/${orcamento.token_compartilhamento}`;

      // Mensagem com link do PDF
      const mensagem = `Olá, ${cliente.nome}! Segue o orçamento solicitado.\n\n📄 Acesse o PDF aqui: ${pdfUrl}\n\nEstou à disposição para qualquer dúvida.`;
      const fone = cliente.telefone.replace(/\D/g, '');
      const whatsappUrl = `https://wa.me/55${fone}?text=${encodeURIComponent(mensagem)}`;
      window.open(whatsappUrl, '_blank');
    } catch (error) {
      console.error('Erro ao compartilhar:', error);
      toast.error('Erro ao compartilhar orçamento');
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
            <CheckCircle size={20} className="text-green-600 dark:text-green-400" /> 
            Revisão do Orçamento
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 sm:space-y-6">
          {/* Cliente */}
          <div>
            <h3 className="font-semibold mb-2 text-sm sm:text-base">Cliente</h3>
            <div className="p-3 sm:p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <p className="font-medium text-sm sm:text-base">{cliente.nome}</p>
              {cliente.telefone && (
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1">
                  📞 {cliente.telefone}
                </p>
              )}
            </div>
          </div>

          {/* Itens */}
          <div>
            <h3 className="font-semibold mb-2 text-sm sm:text-base">Itens do Orçamento</h3>
            <div className="space-y-2">
              {carrinho.map((item, index) => {
                const itemKey = item.produto_id || item.nome || index;
                return (
                  <div
                    key={itemKey}
                    className="p-3 sm:p-4 border rounded-lg flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 sm:gap-4"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-sm sm:text-base">{item.nome}</p>
                        {item.isPersonalizado && (
                          <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-0.5 rounded">Novo</span>
                        )}
                      </div>
                      <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {item.quantidade} x R$ {item.preco_unitario_editavel.toFixed(2)}
                      </p>
                    </div>
                    <p className="font-semibold text-base sm:text-lg text-green-600 dark:text-green-400 text-right sm:text-left">
                      R$ {(item.quantidade * item.preco_unitario_editavel).toFixed(2)}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Condições */}
          <div>
            <h3 className="font-semibold mb-2 text-sm sm:text-base">Condições</h3>
            <div className="p-3 sm:p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <p className="text-sm sm:text-base">
                <span className="font-medium">Pagamento:</span> {condicaoPagamento}
              </p>
            </div>
          </div>

          {/* Total */}
          <div className="border-t pt-4">
            <div className="flex justify-between items-center">
              <span className="text-lg sm:text-xl font-semibold">Total:</span>
              <span className="text-xl sm:text-2xl font-bold text-green-600 dark:text-green-400">
                R$ {total.toFixed(2)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Ações - Otimizadas para mobile */}
      <div className="flex flex-col gap-3 sticky bottom-0 bg-white dark:bg-gray-900 pb-2 sm:pb-0 sm:relative sm:bg-transparent">
        <Button
          variant="outline"
          onClick={onVoltar}
          className="w-full min-h-[44px] sm:min-h-0"
        >
          ← Voltar e Editar
        </Button>
        {orcamentoId && (
          <>
            <Button
              variant="outline"
              onClick={handleDownloadPDF}
              className="w-full min-h-[44px] sm:min-h-0 gap-2"
            >
              <Download size={18} className="sm:w-4 sm:h-4" /> 
              Baixar PDF
            </Button>
            <Button
              onClick={handleShareWhatsApp}
              className="w-full min-h-[44px] sm:min-h-0 gap-2"
              style={{ backgroundColor: '#25D366', color: 'white' }}
            >
              <Share2 size={18} className="sm:w-4 sm:h-4" /> 
              Compartilhar no WhatsApp
            </Button>
          </>
        )}
        {!orcamentoId && (
          <Button
            onClick={onFinalizar}
            disabled={loading}
            className="w-full min-h-[44px] sm:min-h-0 gap-2 bg-green-600 hover:bg-green-700"
          >
            {loading ? (
              <>⏳ Salvando...</>
            ) : (
              <>
                <CheckCircle size={18} className="sm:w-4 sm:h-4" /> 
                Finalizar Orçamento
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}

