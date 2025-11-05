// /src/app/vendedor-app/novo-orcamento/page.tsx
// Página de criação de orçamento otimizada para vendedores

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Send, Users, Package, ShoppingCart, Share2 } from 'lucide-react';
import { useVendedorOrcamentos } from '@/hooks/useVendedorOrcamentos';
import { ProductSearch } from '@/components/vendedor/ProductSearch';
import { ClientQuickSearch } from '@/components/vendedor/ClientQuickSearch';
import { OrcamentoCart, ItemCarrinho } from '@/components/vendedor/OrcamentoCart';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ClienteV2 } from '@/types';
import { Product } from '@/types';
import { OrcamentoCreatePayload } from '@/types/orcamentos';
import toast from 'react-hot-toast';

export default function NovoOrcamentoPage() {
  const router = useRouter();
  const {
    produtos,
    clientes,
    loading,
    buscarProdutos,
    buscarClientes,
    criarClienteRapido,
    criarOrcamento,
    downloadPDF,
  } = useVendedorOrcamentos();

  const [clienteSelecionado, setClienteSelecionado] = useState<ClienteV2 | { id: number; nome: string; telefone?: string } | null>(null);
  const [carrinho, setCarrinho] = useState<ItemCarrinho[]>([]);
  const [condicaoPagamento, setCondicaoPagamento] = useState<string>('À vista');
  const [orcamentoFinalizado, setOrcamentoFinalizado] = useState<number | null>(null);

  useEffect(() => {
    buscarProdutos();
    buscarClientes();
  }, [buscarProdutos, buscarClientes]);

  const handleSelectProduct = (product: Product) => {
    // Verifica se o produto já está no carrinho
    if (carrinho.find((item) => item.produto_id === product.id)) {
      toast.error('Produto já adicionado ao carrinho');
      return;
    }

    const novoItem: ItemCarrinho = {
      produto_id: product.id,
      nome: product.nome,
      preco_original: product.preco_venda,
      preco_unitario_editavel: product.preco_venda,
      quantidade: 1,
      estoque_disponivel: product.quantidade_em_estoque,
    };

    setCarrinho([...carrinho, novoItem]);
    toast.success(`${product.nome} adicionado ao carrinho`);
  };

  const handleUpdateItem = (produtoId: number, campo: 'quantidade' | 'preco', valor: number) => {
    setCarrinho(
      carrinho.map((item) => {
        if (item.produto_id === produtoId) {
          return {
            ...item,
            [campo === 'quantidade' ? 'quantidade' : 'preco_unitario_editavel']: Math.max(
              campo === 'quantidade' ? 1 : 0,
              valor
            ),
          };
        }
        return item;
      })
    );
  };

  const handleRemoveItem = (produtoId: number) => {
    setCarrinho(carrinho.filter((item) => item.produto_id !== produtoId));
    toast.success('Item removido do carrinho');
  };

  const handleSelectClient = (client: ClienteV2 | { id: number; nome: string; telefone?: string }) => {
    setClienteSelecionado(client);
    toast.success(`Cliente selecionado: ${client.nome}`);
  };

  const handleFinalizar = async () => {
    if (!clienteSelecionado) {
      toast.error('Selecione um cliente antes de finalizar');
      return;
    }

    if (carrinho.length === 0) {
      toast.error('Adicione pelo menos um produto ao carrinho');
      return;
    }

    const payload: OrcamentoCreatePayload = {
      cliente_id: clienteSelecionado.id,
      condicao_pagamento: condicaoPagamento,
      status: 'ENVIADO',
      itens: carrinho.map((item) => ({
        produto_id: item.produto_id,
        quantidade: item.quantidade,
        preco_unitario: item.preco_unitario_editavel,
      })),
    };

    const novoOrcamento = await criarOrcamento(payload);

    if (novoOrcamento) {
      setOrcamentoFinalizado(novoOrcamento.id);
      toast.success('Orçamento criado com sucesso! Gerando PDF...');

      try {
        await downloadPDF(novoOrcamento.id);
        toast.success('PDF gerado e baixado automaticamente!');
      } catch (error) {
        console.error('Erro ao gerar PDF:', error);
        toast.error('Orçamento criado, mas houve erro ao gerar o PDF. Você pode baixá-lo no histórico.');
      }
    }
  };

  const handleShareWhatsApp = () => {
    if (!clienteSelecionado || !orcamentoFinalizado) return;
    const mensagem = `Olá, ${clienteSelecionado.nome}! Segue o orçamento #${orcamentoFinalizado} solicitado. Estou à disposição para qualquer dúvida.`;
    const fone = clienteSelecionado.telefone.replace(/\D/g, '');
    const whatsappUrl = `https://wa.me/55${fone}?text=${encodeURIComponent(mensagem)}`;
    window.open(whatsappUrl, '_blank');
  };

  // Tela de sucesso após criação
  if (orcamentoFinalizado) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-6">
        <Card className="max-w-md w-full text-center">
          <CardHeader>
            <CardTitle className="text-2xl text-green-600">
              Orçamento #{orcamentoFinalizado} Criado com Sucesso!
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600 dark:text-gray-400">
              O PDF do orçamento foi gerado e baixado. Você pode compartilhá-lo com o cliente.
            </p>
            {clienteSelecionado && (
              <Button
                onClick={handleShareWhatsApp}
                className="w-full gap-2"
                style={{ backgroundColor: '#25D366', color: 'white' }}
              >
                <Share2 size={18} />
                Compartilhar no WhatsApp
              </Button>
            )}
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => router.push('/vendedor-app')}
                className="flex-1 gap-2"
              >
                <ArrowLeft size={18} />
                Voltar ao Início
              </Button>
              <Button
                onClick={() => {
                  setOrcamentoFinalizado(null);
                  setClienteSelecionado(null);
                  setCarrinho([]);
                }}
                className="flex-1 gap-2"
              >
                Criar Novo Orçamento
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

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
                Novo Orçamento
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Conteúdo principal */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Coluna esquerda - Cliente e Produtos */}
          <div className="lg:col-span-2 space-y-6">
            {/* Seleção de Cliente */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users size={20} />
                  Cliente
                </CardTitle>
              </CardHeader>
              <CardContent>
                {clienteSelecionado ? (
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex items-center justify-between">
                    <div>
                      <p className="font-semibold">{clienteSelecionado.nome}</p>
                      {clienteSelecionado.telefone && (
                        <p className="text-sm text-gray-500">{clienteSelecionado.telefone}</p>
                      )}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setClienteSelecionado(null)}
                    >
                      Trocar
                    </Button>
                  </div>
                ) : (
                  <ClientQuickSearch
                    clientes={clientes}
                    onSelectClient={handleSelectClient}
                    onCreateClient={criarClienteRapido}
                    loading={loading}
                  />
                )}
              </CardContent>
            </Card>

            {/* Busca de Produtos */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Package size={20} />
                  Produtos
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ProductSearch
                  produtos={produtos}
                  onSelectProduct={handleSelectProduct}
                  loading={loading}
                />
                <p className="text-xs text-gray-500 mt-2">
                  {produtos.length} produtos disponíveis (incluindo estoque zero)
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Coluna direita - Carrinho e Finalização */}
          <div className="lg:col-span-1 space-y-6">
            <OrcamentoCart
              items={carrinho}
              onUpdateItem={handleUpdateItem}
              onRemoveItem={handleRemoveItem}
            />

            {/* Finalização */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShoppingCart size={20} />
                  Finalização
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Condição de Pagamento
                  </label>
                  <Select value={condicaoPagamento} onValueChange={setCondicaoPagamento}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="À vista">À vista</SelectItem>
                      <SelectItem value="30 dias">30 dias</SelectItem>
                      <SelectItem value="60 dias">60 dias</SelectItem>
                      <SelectItem value="30/60 dias">30/60 dias</SelectItem>
                      <SelectItem value="90 dias">90 dias</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="pt-4 border-t">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-lg font-semibold">Total:</span>
                    <span className="text-2xl font-bold text-blue-600">
                      R${' '}
                      {carrinho
                        .reduce(
                          (acc, item) => acc + item.preco_unitario_editavel * item.quantidade,
                          0
                        )
                        .toFixed(2)}
                    </span>
                  </div>

                  <Button
                    onClick={handleFinalizar}
                    disabled={loading || !clienteSelecionado || carrinho.length === 0}
                    className="w-full gap-2"
                    size="lg"
                  >
                    {loading ? (
                      'Criando...'
                    ) : (
                      <>
                        <Send size={18} />
                        Finalizar e Gerar PDF
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

