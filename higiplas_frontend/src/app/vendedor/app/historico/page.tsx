'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useVendedor } from '@/hooks/useVendedor';
import { useOrcamentos } from '@/hooks/useOrcamentos';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { apiService } from '@/services/apiService';
import { Download, ArrowLeft, Search, FileText } from 'lucide-react';
import toast from 'react-hot-toast';
import { Loader2 } from 'lucide-react';

const statusColors: { [key: string]: 'default' | 'secondary' | 'destructive' | 'outline' } = {
  ENVIADO: 'secondary',
  APROVADO: 'default',
  REJEITADO: 'destructive',
  RASCUNHO: 'outline',
};

export default function HistoricoPage() {
  const router = useRouter();
  const { loading: userLoading, isVendedor } = useVendedor();
  const { orcamentos, loading: orcamentosLoading, listarOrcamentosVendedor } = useOrcamentos();
  const [termoBusca, setTermoBusca] = useState('');
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  useEffect(() => {
    if (isVendedor) {
      listarOrcamentosVendedor();
    }
  }, [isVendedor, listarOrcamentosVendedor]);

  const handleDownloadPDF = async (orcamentoId: number) => {
    setDownloadingId(orcamentoId);
    toast.loading(`Gerando PDF #${orcamentoId}...`);

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
      toast.success(`PDF #${orcamentoId} baixado!`);

      setTimeout(() => {
        window.URL.revokeObjectURL(url);
        link.remove();
      }, 100);
    } catch (downloadError) {
      toast.dismiss();
      toast.error('Falha ao gerar o PDF. Verifique o console.');
      console.error('Erro no download:', downloadError);
    } finally {
      setDownloadingId(null);
    }
  };

  const orcamentosFiltrados = orcamentos.filter(orc => 
    orc.cliente.razao_social.toLowerCase().includes(termoBusca.toLowerCase()) ||
    orc.id.toString().includes(termoBusca)
  );

  if (userLoading || !isVendedor) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4">
        <div className="flex items-center gap-2 sm:gap-4 min-w-0 flex-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/vendedor/app')}
            className="min-h-[44px] sm:min-h-0"
          >
            <ArrowLeft size={18} className="mr-2" /> 
            <span className="hidden sm:inline">Voltar</span>
          </Button>
          <div className="min-w-0 flex-1">
            <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">
              Histórico de Orçamentos
            </h1>
            <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1">
              Todos os seus orçamentos gerados
            </p>
          </div>
        </div>
        <Button 
          onClick={() => router.push('/vendedor/app')}
          className="w-full sm:w-auto min-h-[44px] sm:min-h-0"
        >
          Novo Orçamento
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <Input
              placeholder="Buscar por cliente ou ID..."
              value={termoBusca}
              onChange={(e) => setTermoBusca(e.target.value)}
              className="pl-10 h-11 sm:h-10 text-base sm:text-sm"
            />
          </div>
        </CardHeader>
        <CardContent>
          {orcamentosLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : orcamentosFiltrados.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              <FileText size={48} className="mx-auto mb-4 opacity-50" />
              <h3 className="font-semibold text-base sm:text-lg mb-2">Nenhum orçamento encontrado</h3>
              <p className="mb-4 text-sm sm:text-base">Comece criando seu primeiro orçamento.</p>
              <Button 
                onClick={() => router.push('/vendedor/app')}
                className="min-h-[44px] sm:min-h-0"
              >
                Criar Primeiro Orçamento
              </Button>
            </div>
          ) : (
            <>
              {/* Mobile: Cards */}
              <div className="block sm:hidden space-y-3">
                {orcamentosFiltrados.map((orc) => {
                  const total = orc.itens.reduce((acc, item) => 
                    acc + (item.quantidade * item.preco_unitario_congelado), 0
                  );
                  return (
                    <div key={orc.id} className="p-4 border rounded-lg space-y-3 bg-white dark:bg-gray-800">
                      <div className="flex justify-between items-start">
                        <div className="flex-1 min-w-0">
                          <p className="font-mono text-sm text-gray-500 dark:text-gray-400">#{orc.id}</p>
                          <p className="font-semibold text-base mt-1">{orc.cliente.razao_social}</p>
                        </div>
                        <Badge variant={statusColors[orc.status] || 'outline'} className="ml-2">
                          {orc.status}
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-600 dark:text-gray-400">
                          {new Date(orc.data_criacao).toLocaleDateString('pt-BR')}
                        </span>
                        <span className="font-bold text-green-600 dark:text-green-400 text-base">
                          R$ {total.toFixed(2)}
                        </span>
                      </div>
                      <Button
                        variant="outline"
                        onClick={() => handleDownloadPDF(orc.id)}
                        disabled={downloadingId === orc.id}
                        className="w-full min-h-[44px] gap-2"
                      >
                        {downloadingId === orc.id ? (
                          <>
                            <Loader2 size={18} className="animate-spin" />
                            Gerando PDF...
                          </>
                        ) : (
                          <>
                            <Download size={18} />
                            Baixar PDF
                          </>
                        )}
                      </Button>
                    </div>
                  );
                })}
              </div>

              {/* Desktop: Table */}
              <div className="hidden sm:block overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>#ID</TableHead>
                      <TableHead>Cliente</TableHead>
                      <TableHead>Data</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Valor Total</TableHead>
                      <TableHead className="text-center">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {orcamentosFiltrados.map((orc) => {
                      const total = orc.itens.reduce((acc, item) => 
                        acc + (item.quantidade * item.preco_unitario_congelado), 0
                      );
                      return (
                        <TableRow key={orc.id}>
                          <TableCell className="font-mono">#{orc.id}</TableCell>
                          <TableCell className="font-medium">{orc.cliente.razao_social}</TableCell>
                          <TableCell>
                            {new Date(orc.data_criacao).toLocaleDateString('pt-BR')}
                          </TableCell>
                          <TableCell>
                            <Badge variant={statusColors[orc.status] || 'outline'}>
                              {orc.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right font-semibold">
                            R$ {total.toFixed(2)}
                          </TableCell>
                          <TableCell className="text-center">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDownloadPDF(orc.id)}
                              disabled={downloadingId === orc.id}
                              className="gap-2"
                            >
                              {downloadingId === orc.id ? (
                                <>
                                  <Loader2 size={14} className="animate-spin" />
                                  Gerando...
                                </>
                              ) : (
                                <>
                                  <Download size={14} />
                                  Baixar PDF
                                </>
                              )}
                            </Button>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

