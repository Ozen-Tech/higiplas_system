'use client';

import { useState, useEffect } from 'react';
import { Header } from '@/components/dashboard/Header';
import { useOrcamentos } from '@/hooks/useOrcamentos';
import { Orcamento } from '@/types/orcamentos';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Edit, CheckCircle, XCircle, Eye, Download, Search, Filter, Trash2 } from 'lucide-react';
import { OrcamentoEditModal } from '@/components/orcamentos/OrcamentoEditModal';
import { OrcamentoConfirmModal } from '@/components/orcamentos/OrcamentoConfirmModal';
import { OrcamentoViewModal } from '@/components/orcamentos/OrcamentoViewModal';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';
import { useAuth } from '@/contexts/AuthContext';

const statusColors: { [key: string]: 'default' | 'secondary' | 'destructive' | 'outline' } = {
  ENVIADO: 'secondary',
  APROVADO: 'default',
  REJEITADO: 'destructive',
  RASCUNHO: 'outline',
  FINALIZADO: 'default',
};

export default function OrcamentosAdminPage() {
  const { user } = useAuth();
  const { orcamentos, loading, listarTodosOrcamentos, atualizarStatus, confirmarOrcamento, excluirOrcamento } = useOrcamentos();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('TODOS');
  const [selectedOrcamento, setSelectedOrcamento] = useState<Orcamento | null>(null);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [confirmModalOpen, setConfirmModalOpen] = useState(false);
  const [viewModalOpen, setViewModalOpen] = useState(false);
  const [downloadingId, setDownloadingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const isAdmin = user?.email?.toLowerCase() === 'enzo.alverde@gmail.com';

  useEffect(() => {
    if (isAdmin) {
      listarTodosOrcamentos();
    }
  }, [isAdmin, listarTodosOrcamentos]);

  if (!isAdmin) {
    return (
      <>
        <Header>
          <h1 className="text-xl font-bold">Acesso Negado</h1>
        </Header>
        <main className="flex-1 p-6">
          <Card>
            <CardContent className="p-6 text-center">
              <p className="text-red-600">Apenas administradores podem acessar esta página.</p>
            </CardContent>
          </Card>
        </main>
      </>
    );
  }

  const calcularTotal = (orcamento: Orcamento) => {
    if (!orcamento.itens) return 0;
    return orcamento.itens.reduce((acc, item) => acc + (item.quantidade * item.preco_unitario_congelado), 0);
  };

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

  const handleAprovar = async (orcamento: Orcamento) => {
    const resultado = await atualizarStatus(orcamento.id, 'APROVADO');
    if (resultado) {
      listarTodosOrcamentos();
    }
  };

  const handleRejeitar = async (orcamento: Orcamento) => {
    const resultado = await atualizarStatus(orcamento.id, 'REJEITADO');
    if (resultado) {
      listarTodosOrcamentos();
    }
  };

  const handleConfirmar = async (orcamento: Orcamento) => {
    const resultado = await confirmarOrcamento(orcamento.id);
    if (resultado) {
      setConfirmModalOpen(false);
      listarTodosOrcamentos();
    }
  };

  const handleExcluir = async (orcamento: Orcamento) => {
    if (!confirm(`Tem certeza que deseja excluir o orçamento #${orcamento.id}? Esta ação não pode ser desfeita.`)) {
      return;
    }
    
    if (orcamento.status === 'FINALIZADO') {
      toast.error('Não é possível excluir orçamentos finalizados.');
      return;
    }

    setDeletingId(orcamento.id);
    const sucesso = await excluirOrcamento(orcamento.id);
    setDeletingId(null);
    
    if (sucesso) {
      listarTodosOrcamentos();
    }
  };

  const orcamentosFiltrados = orcamentos.filter(orc => {
    const matchSearch = 
      orc.cliente.razao_social.toLowerCase().includes(searchTerm.toLowerCase()) ||
      orc.id.toString().includes(searchTerm) ||
      orc.usuario.nome.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchStatus = statusFilter === 'TODOS' || orc.status === statusFilter;
    
    return matchSearch && matchStatus;
  });

  return (
    <>
      <Header>
        <h1 className="text-xl font-bold">Gerenciar Orçamentos</h1>
      </Header>
      <main className="flex-1 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Filtros */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter size={20} /> Filtros
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                  <Input
                    placeholder="Buscar por cliente, ID ou vendedor..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filtrar por status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="TODOS">Todos os status</SelectItem>
                    <SelectItem value="RASCUNHO">Rascunho</SelectItem>
                    <SelectItem value="ENVIADO">Enviado</SelectItem>
                    <SelectItem value="APROVADO">Aprovado</SelectItem>
                    <SelectItem value="REJEITADO">Rejeitado</SelectItem>
                    <SelectItem value="FINALIZADO">Finalizado</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Lista de Orçamentos */}
          <Card>
            <CardHeader>
              <CardTitle>Orçamentos ({orcamentosFiltrados.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-12">
                  <p className="text-gray-500">Carregando orçamentos...</p>
                </div>
              ) : orcamentosFiltrados.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p>Nenhum orçamento encontrado.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>#ID</TableHead>
                        <TableHead>Cliente</TableHead>
                        <TableHead>Vendedor</TableHead>
                        <TableHead>Data</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Valor Total</TableHead>
                        <TableHead className="text-center">Ações</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {orcamentosFiltrados.map((orc) => {
                        const total = calcularTotal(orc);
                        return (
                          <TableRow key={orc.id}>
                            <TableCell className="font-mono">#{orc.id}</TableCell>
                            <TableCell className="font-medium">{orc.cliente.razao_social}</TableCell>
                            <TableCell>{orc.usuario.nome}</TableCell>
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
                            <TableCell>
                              <div className="flex items-center justify-center gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedOrcamento(orc);
                                    setViewModalOpen(true);
                                  }}
                                  title="Visualizar"
                                >
                                  <Eye size={16} />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleDownloadPDF(orc.id)}
                                  disabled={downloadingId === orc.id}
                                  title="Baixar PDF"
                                >
                                  {downloadingId === orc.id ? '...' : <Download size={16} />}
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedOrcamento(orc);
                                    setEditModalOpen(true);
                                  }}
                                  title="Editar"
                                >
                                  <Edit size={16} />
                                </Button>
                                {orc.status === 'ENVIADO' && (
                                  <>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => handleAprovar(orc)}
                                      className="text-green-600 hover:text-green-700"
                                      title="Aprovar"
                                    >
                                      <CheckCircle size={16} />
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => handleRejeitar(orc)}
                                      className="text-red-600 hover:text-red-700"
                                      title="Rejeitar"
                                    >
                                      <XCircle size={16} />
                                    </Button>
                                  </>
                                )}
                                {(orc.status === 'APROVADO' || orc.status === 'ENVIADO') && (
                                  <Button
                                    variant="default"
                                    size="sm"
                                    onClick={() => {
                                      setSelectedOrcamento(orc);
                                      setConfirmModalOpen(true);
                                    }}
                                    title="Confirmar e dar baixa"
                                  >
                                    Confirmar
                                  </Button>
                                )}
                                {orc.status !== 'FINALIZADO' && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleExcluir(orc)}
                                    disabled={deletingId === orc.id}
                                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                    title="Excluir orçamento"
                                  >
                                    {deletingId === orc.id ? '...' : <Trash2 size={16} />}
                                  </Button>
                                )}
                              </div>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Modais */}
      {selectedOrcamento && (
        <>
          <OrcamentoViewModal
            orcamento={selectedOrcamento}
            open={viewModalOpen}
            onClose={() => {
              setViewModalOpen(false);
              setSelectedOrcamento(null);
            }}
            onDownloadPDF={() => handleDownloadPDF(selectedOrcamento.id)}
          />
          <OrcamentoEditModal
            orcamento={selectedOrcamento}
            open={editModalOpen}
            onClose={() => {
              setEditModalOpen(false);
              setSelectedOrcamento(null);
            }}
            onSuccess={() => {
              setEditModalOpen(false);
              setSelectedOrcamento(null);
              listarTodosOrcamentos();
            }}
          />
          <OrcamentoConfirmModal
            orcamento={selectedOrcamento}
            open={confirmModalOpen}
            onClose={() => {
              setConfirmModalOpen(false);
              setSelectedOrcamento(null);
            }}
            onConfirm={() => handleConfirmar(selectedOrcamento)}
          />
        </>
      )}
    </>
  );
}

