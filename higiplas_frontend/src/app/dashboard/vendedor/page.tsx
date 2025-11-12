// /src/app/dashboard/vendedor/page.tsx - CORREÇÃO FINAL DE ASPAS

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { PlusCircle, List, Download } from 'lucide-react';

import { Header } from '@/components/dashboard/Header';
import { useOrcamentos } from '@/hooks/useOrcamentos';
import { Orcamento } from '@/types/orcamentos';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';
import { useAuth } from '@/contexts/AuthContext';

// Mapeamento de status para cores do Badge
const statusColors: { [key: string]: 'default' | 'secondary' | 'destructive' | 'outline' } = {
  ENVIADO: 'secondary',
  APROVADO: 'default',
  REJEITADO: 'destructive',
  RASCUNHO: 'outline',
};

export default function VendedorHubPage() {
  const { user } = useAuth();
  const { orcamentos, loading, error, listarOrcamentosVendedor } = useOrcamentos();
  const [activeTab, setActiveTab] = useState<'historico' | 'novo'>('historico');
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  // Verificar se o usuário é vendedor ou admin/gestor
  const perfilUpper = user?.perfil?.toUpperCase() || '';
  const isVendedor = perfilUpper.includes('VENDEDOR');
  const isAdminOrGestor = perfilUpper === 'ADMIN' || perfilUpper === 'GESTOR';
  const podeAcessar = isVendedor || isAdminOrGestor;

  useEffect(() => {
    if (podeAcessar) {
      listarOrcamentosVendedor();
    }
  }, [podeAcessar, listarOrcamentosVendedor]);

  if (!podeAcessar) {
    return (
      <>
        <Header>
          <h1 className="text-xl font-bold">Acesso Negado</h1>
        </Header>
        <main className="flex-1 p-6">
          <Card>
            <CardContent className="p-6 text-center">
              <p className="text-red-600">Apenas vendedores, administradores ou gestores podem acessar esta página.</p>
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
        
        toast.dismiss(); // Remove o "loading..."
        toast.success(`PDF #${orcamentoId} baixado!`);
        
        // Limpeza
        setTimeout(() => {
            window.URL.revokeObjectURL(url);
            link.remove();
        }, 100);

    } catch (downloadError) {
        toast.dismiss();
        toast.error("Falha ao gerar o PDF. Verifique o console.");
        console.error("Erro no download:", downloadError);
    } finally {
        setDownloadingId(null);
    }
  };

  return (
    <>
      <Header>
        <h1 className="text-xl font-bold">Portal do Vendedor</h1>
      </Header>
      <main className="flex-1 p-6">
        <div className="max-w-7xl mx-auto">
          {/* Abas de Navegação */}
          <div className="mb-6 flex border-b">
            <button 
              onClick={() => setActiveTab('novo')}
              className={`flex items-center gap-2 px-4 py-3 font-semibold ${activeTab === 'novo' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'}`}
            >
              <PlusCircle size={18} /> Novo Pedido
            </button>
            <button 
              onClick={() => setActiveTab('historico')}
              className={`flex items-center gap-2 px-4 py-3 font-semibold ${activeTab === 'historico' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'}`}
            >
              <List size={18} /> Histórico de Pedidos
            </button>
          </div>

          {/* Conteúdo das Abas */}
          {activeTab === 'novo' && (
            <Card>
              <CardHeader>
                <CardTitle>Iniciar um Novo Pedido</CardTitle>
              </CardHeader>
              <CardContent className="text-center py-12">
                <p className="text-gray-600 mb-4">Clique no botão abaixo para criar um novo orçamento para um cliente.</p>
                <Link href="/dashboard/vendedor/novo">
                  <Button size="lg" className="gap-2">
                    <PlusCircle /> Criar Novo Orçamento
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}

          {activeTab === 'historico' && (
            <Card>
              <CardHeader>
                <CardTitle>Seus Orçamentos</CardTitle>
              </CardHeader>
              <CardContent>
                {loading && <p className="text-center py-8">Carregando histórico...</p>}
                {error && <p className="text-red-500 text-center py-8">{error}</p>}
                {!loading && !error && (
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
                      {orcamentos.map(orc => (
                        <TableRow key={orc.id}>
                          <TableCell className="font-mono">#{orc.id}</TableCell>
                          <TableCell className="font-medium">{orc.cliente.razao_social}</TableCell>
                          <TableCell>{new Date(orc.data_criacao).toLocaleDateString('pt-BR')}</TableCell>
                          <TableCell>
                            <Badge variant={statusColors[orc.status] || 'outline'}>{orc.status}</Badge>
                          </TableCell>
                          <TableCell className="text-right font-semibold">
                            R$ {calcularTotal(orc).toFixed(2)}
                          </TableCell>
                          <TableCell className="text-center">
                            <Button 
                              variant="outline" 
                              size="sm" 
                              onClick={() => handleDownloadPDF(orc.id)}
                              disabled={downloadingId === orc.id}
                              className="gap-2"
                            >
                              {downloadingId === orc.id ? 'Gerando...' : <Download size={14} />}
                              {downloadingId !== orc.id && 'Baixar PDF'}
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
                {orcamentos.length === 0 && !loading && (
                    <div className="text-center py-12 text-gray-500">
                        <List size={48} className="mx-auto mb-4" />
                        <h3 className="font-semibold text-lg">Nenhum orçamento encontrado.</h3>
                        
                        <p>Comece a vender utilizando a aba Novo Pedido.</p>
                    </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </>
  );
}