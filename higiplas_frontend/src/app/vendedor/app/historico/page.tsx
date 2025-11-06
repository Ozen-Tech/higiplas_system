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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/vendedor/app')}
          >
            <ArrowLeft size={16} className="mr-2" /> Voltar
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Histórico de Orçamentos
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Todos os seus orçamentos gerados
            </p>
          </div>
        </div>
        <Button onClick={() => router.push('/vendedor/app')}>
          Novo Orçamento
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <Input
                placeholder="Buscar por cliente ou ID..."
                value={termoBusca}
                onChange={(e) => setTermoBusca(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {orcamentosLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : orcamentosFiltrados.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText size={48} className="mx-auto mb-4 opacity-50" />
              <h3 className="font-semibold text-lg mb-2">Nenhum orçamento encontrado</h3>
              <p className="mb-4">Comece criando seu primeiro orçamento.</p>
              <Button onClick={() => router.push('/vendedor/app')}>
                Criar Primeiro Orçamento
              </Button>
            </div>
          ) : (
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
          )}
        </CardContent>
      </Card>
    </div>
  );
}

