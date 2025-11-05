// /src/app/vendedor-app/historico/page.tsx
// Histórico de orçamentos do vendedor

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Download, FileText, Calendar, User, Filter } from 'lucide-react';
import { useVendedorOrcamentos } from '@/hooks/useVendedorOrcamentos';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Orcamento } from '@/types/orcamentos';
import toast from 'react-hot-toast';

const statusColors: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  ENVIADO: 'secondary',
  APROVADO: 'default',
  REJEITADO: 'destructive',
  RASCUNHO: 'outline',
  FINALIZADO: 'default',
};

export default function HistoricoPage() {
  const router = useRouter();
  const { orcamentos, loading, listarOrcamentos, downloadPDF } = useVendedorOrcamentos();
  const [statusFilter, setStatusFilter] = useState<string>('TODOS');
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  useEffect(() => {
    listarOrcamentos();
  }, [listarOrcamentos]);

  const calcularTotal = (orcamento: Orcamento) => {
    if (!orcamento.itens) return 0;
    return orcamento.itens.reduce(
      (acc, item) => acc + item.quantidade * item.preco_unitario_congelado,
      0
    );
  };

  const handleDownloadPDF = async (orcamentoId: number) => {
    setDownloadingId(orcamentoId);
    toast.loading(`Gerando PDF #${orcamentoId}...`);

    try {
      await downloadPDF(orcamentoId);
    } catch (error) {
      console.error('Erro ao baixar PDF:', error);
      toast.error('Falha ao gerar o PDF');
    } finally {
      setDownloadingId(null);
    }
  };

  const filteredOrcamentos =
    statusFilter === 'TODOS'
      ? orcamentos
      : orcamentos.filter((orc) => orc.status === statusFilter);

  const sortedOrcamentos = [...filteredOrcamentos].sort(
    (a, b) => new Date(b.data_criacao).getTime() - new Date(a.data_criacao).getTime()
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => router.push('/vendedor-app')}
              >
                <ArrowLeft size={20} />
              </Button>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Histórico de Orçamentos
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Conteúdo principal */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Filtros */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <Filter size={18} className="text-gray-500" />
              <div className="flex-1">
                <label className="text-sm font-medium mb-2 block">Filtrar por Status</label>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-full md:w-[200px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="TODOS">Todos</SelectItem>
                    <SelectItem value="RASCUNHO">Rascunho</SelectItem>
                    <SelectItem value="ENVIADO">Enviado</SelectItem>
                    <SelectItem value="APROVADO">Aprovado</SelectItem>
                    <SelectItem value="REJEITADO">Rejeitado</SelectItem>
                    <SelectItem value="FINALIZADO">Finalizado</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="text-sm text-gray-500">
                {sortedOrcamentos.length} de {orcamentos.length} orçamentos
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Lista de orçamentos */}
        {loading ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p>Carregando histórico...</p>
            </CardContent>
          </Card>
        ) : sortedOrcamentos.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <FileText size={48} className="mx-auto mb-4 text-gray-400" />
              <h3 className="font-semibold text-lg mb-2">Nenhum orçamento encontrado</h3>
              <p className="text-gray-500 mb-4">
                {statusFilter === 'TODOS'
                  ? 'Comece criando seu primeiro orçamento.'
                  : 'Nenhum orçamento com este status.'}
              </p>
              <Button onClick={() => router.push('/vendedor-app/novo-orcamento')}>
                Criar Novo Orçamento
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Meus Orçamentos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
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
                    {sortedOrcamentos.map((orcamento) => (
                      <TableRow key={orcamento.id}>
                        <TableCell className="font-mono">#{orcamento.id}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <User size={14} className="text-gray-400" />
                            <span className="font-medium">
                              {orcamento.cliente?.razao_social || 'Cliente sem nome'}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Calendar size={14} className="text-gray-400" />
                            <span>
                              {new Date(orcamento.data_criacao).toLocaleDateString('pt-BR', {
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric',
                              })}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={statusColors[orcamento.status] || 'outline'}>
                            {orcamento.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right font-semibold text-blue-600">
                          R$ {calcularTotal(orcamento).toFixed(2)}
                        </TableCell>
                        <TableCell className="text-center">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDownloadPDF(orcamento.id)}
                            disabled={downloadingId === orcamento.id}
                            className="gap-2"
                          >
                            {downloadingId === orcamento.id ? (
                              'Gerando...'
                            ) : (
                              <>
                                <Download size={14} />
                                PDF
                              </>
                            )}
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}

