// /src/app/dashboard/vendedor/page.tsx - CORRIGIDO

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
// CORREÇÃO: Trocamos 'ListBulletIcon' pelo ícone correto 'List'
import { PlusCircle, List } from 'lucide-react';

import { Header } from '@/components/dashboard/Header';
import { useOrcamentos } from '@/hooks/useOrcamentos';
import { Orcamento } from '@/types/orcamentos';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

// Mapeamento de status para cores do Badge
const statusColors: { [key: string]: 'default' | 'secondary' | 'destructive' | 'outline' } = {
  ENVIADO: 'secondary', // Amarelo/Pendente
  APROVADO: 'default',   // Verde/Sucesso
  REJEITADO: 'destructive',
  RASCUNHO: 'outline',
};

export default function VendedorHubPage() {
  const { orcamentos, loading, error, listarOrcamentosVendedor } = useOrcamentos();
  const [activeTab, setActiveTab] = useState('historico');

  useEffect(() => {
    // Busca os orçamentos quando o componente é montado
    listarOrcamentosVendedor();
  }, [listarOrcamentosVendedor]);

  // Função para calcular o total de um orçamento
  const calcularTotal = (orcamento: Orcamento) => {
    return orcamento.itens.reduce((acc, item) => acc + (item.quantidade * item.preco_unitario_congelado), 0);
  };
  
  // Função para baixar o PDF
  const handleDownloadPDF = (orcamentoId: number) => {
      const pdfUrl = `${process.env.NEXT_PUBLIC_API_URL}/orcamentos/${orcamentoId}/pdf/`;
      window.open(pdfUrl, '_blank');
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
              {/* CORREÇÃO: Ícone substituído */}
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
                {loading && <p>Carregando histórico...</p>}
                {error && <p className="text-red-500">{error}</p>}
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
                            <Button variant="outline" size="sm" onClick={() => handleDownloadPDF(orc.id)}>
                              Baixar PDF
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
                {orcamentos.length === 0 && !loading && (
                    <p className="text-center py-8 text-gray-500">Nenhum orçamento encontrado.</p>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </>
  );
}