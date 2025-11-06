'use client';

import { useState, useEffect } from 'react';
import { Cliente, Produto } from '@/types/vendas';
import { ItemCarrinhoOrcamento, OrcamentoCreatePayload } from '@/types/orcamentos';
import { useVendas } from '@/hooks/useVendas';
import { useOrcamentos } from '@/hooks/useOrcamentos';
import { ClienteSelector } from './ClienteSelector';
import { ProdutoSelector } from './ProdutoSelector';
import { OrcamentoReview } from './OrcamentoReview';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ShoppingCart, Trash2, ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';
import { apiService } from '@/services/apiService';

type Etapa = 'cliente' | 'produtos' | 'revisao';

export function OrcamentoBuilder() {
  const { clientes, produtos, buscarClientes, buscarProdutos, criarClienteCompleto, loading: vendasLoading } = useVendas();
  const { criarOrcamento, loading: orcamentoLoading } = useOrcamentos();

  const [etapa, setEtapa] = useState<Etapa>('cliente');
  const [clienteSelecionado, setClienteSelecionado] = useState<Cliente | null>(null);
  const [carrinho, setCarrinho] = useState<ItemCarrinhoOrcamento[]>([]);
  const [condicaoPagamento, setCondicaoPagamento] = useState<string>('À vista');
  const [orcamentoId, setOrcamentoId] = useState<number | null>(null);

  useEffect(() => {
    buscarClientes();
    buscarProdutos();
  }, [buscarClientes, buscarProdutos]);

  const adicionarProduto = (produto: Produto) => {
    if (carrinho.find(item => item.produto_id === produto.id)) {
      toast.error('Produto já está no carrinho');
      return;
    }

    const novoItem: ItemCarrinhoOrcamento = {
      produto_id: produto.id,
      nome: produto.nome,
      estoque_disponivel: produto.estoque_disponivel,
      preco_original: produto.preco,
      preco_unitario_editavel: produto.preco,
      quantidade: 1,
    };
    setCarrinho([...carrinho, novoItem]);
    toast.success(`${produto.nome} adicionado ao carrinho`);
  };

  const atualizarItem = (produtoId: number, campo: 'quantidade' | 'preco', valor: number) => {
    setCarrinho(carrinho.map(item => {
      if (item.produto_id === produtoId) {
        return {
          ...item,
          [campo === 'quantidade' ? 'quantidade' : 'preco_unitario_editavel']: Math.max(0, valor)
        };
      }
      return item;
    }));
  };

  const removerItem = (produtoId: number) => {
    setCarrinho(carrinho.filter(item => item.produto_id !== produtoId));
    toast.success('Item removido do carrinho');
  };

  const total = carrinho.reduce((acc, item) => acc + (item.preco_unitario_editavel * item.quantidade), 0);

  const handleFinalizar = async () => {
    if (!clienteSelecionado || carrinho.length === 0) {
      toast.error('Selecione um cliente e adicione produtos ao carrinho');
      return;
    }

    const payload: OrcamentoCreatePayload = {
      cliente_id: clienteSelecionado.id,
      condicao_pagamento: condicaoPagamento,
      status: 'ENVIADO',
      itens: carrinho.map(item => ({
        produto_id: item.produto_id,
        quantidade: item.quantidade,
        preco_unitario: item.preco_unitario_editavel
      }))
    };

    const novoOrcamento = await criarOrcamento(payload);

    if (novoOrcamento) {
      setOrcamentoId(novoOrcamento.id);
      toast.success('Orçamento salvo! Gerando PDF...');

      try {
        const response = await apiService.getBlob(`/orcamentos/${novoOrcamento.id}/pdf/`);
        const blob = await response.blob();

        const contentDisposition = response.headers.get('content-disposition');
        let filename = `orcamento_${novoOrcamento.id}.pdf`;
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
        toast.success('PDF gerado! Compartilhe com o cliente.');

        setTimeout(() => {
          window.URL.revokeObjectURL(url);
          link.remove();
        }, 100);
      } catch (error) {
        console.error('Erro ao baixar PDF:', error);
        toast.error('Orçamento salvo, mas falha ao gerar PDF. Baixe-o na tela de histórico.');
      }
    }
  };

  const handleVoltarEtapa = () => {
    if (etapa === 'revisao') {
      setEtapa('produtos');
    } else if (etapa === 'produtos') {
      setEtapa('cliente');
    }
  };

  const handleAvancarEtapa = () => {
    if (etapa === 'cliente') {
      if (!clienteSelecionado) {
        toast.error('Selecione um cliente primeiro');
        return;
      }
      setEtapa('produtos');
    } else if (etapa === 'produtos') {
      if (carrinho.length === 0) {
        toast.error('Adicione pelo menos um produto ao carrinho');
        return;
      }
      setEtapa('revisao');
    }
  };

  return (
    <div className="space-y-6">
      {/* Indicador de Etapas */}
      <div className="flex items-center justify-center gap-2 mb-6">
        <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${etapa === 'cliente' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' : 'bg-gray-100 dark:bg-gray-800'}`}>
          <span className="font-semibold">1. Cliente</span>
        </div>
        <div className="w-8 h-0.5 bg-gray-300"></div>
        <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${etapa === 'produtos' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' : 'bg-gray-100 dark:bg-gray-800'}`}>
          <span className="font-semibold">2. Produtos</span>
        </div>
        <div className="w-8 h-0.5 bg-gray-300"></div>
        <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${etapa === 'revisao' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' : 'bg-gray-100 dark:bg-gray-800'}`}>
          <span className="font-semibold">3. Revisão</span>
        </div>
      </div>

      {/* Etapa: Cliente */}
      {etapa === 'cliente' && (
        <ClienteSelector
          clientes={clientes}
          clienteSelecionado={clienteSelecionado}
          onSelectCliente={setClienteSelecionado}
          onCriarCliente={criarClienteCompleto}
          loading={vendasLoading}
        />
      )}

      {/* Etapa: Produtos */}
      {etapa === 'produtos' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ProdutoSelector
              produtos={produtos}
              carrinho={carrinho}
              onAdicionarProduto={adicionarProduto}
              loading={vendasLoading}
            />
          </div>
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShoppingCart size={20} /> Carrinho
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 max-h-[60vh] overflow-y-auto">
                {carrinho.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">Carrinho vazio</p>
                ) : (
                  carrinho.map((item) => (
                    <div key={item.produto_id} className="p-3 border rounded-lg space-y-2">
                      <div className="flex justify-between items-start">
                        <p className="font-medium text-sm">{item.nome}</p>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => removerItem(item.produto_id)}
                          className="h-6 w-6"
                        >
                          <Trash2 size={14} className="text-red-500" />
                        </Button>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <label className="text-xs text-gray-600 dark:text-gray-400">Qtd</label>
                          <Input
                            type="number"
                            value={item.quantidade}
                            onChange={(e) => atualizarItem(item.produto_id, 'quantidade', parseInt(e.target.value) || 0)}
                            className="h-8 text-sm"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-600 dark:text-gray-400">Preço</label>
                          <Input
                            type="number"
                            step="0.01"
                            value={item.preco_unitario_editavel}
                            onChange={(e) => atualizarItem(item.produto_id, 'preco', parseFloat(e.target.value) || 0)}
                            className="h-8 text-sm"
                          />
                        </div>
                      </div>
                      {item.quantidade > item.estoque_disponivel && (
                        <p className="text-xs text-orange-500">Estoque insuficiente!</p>
                      )}
                      <p className="text-sm font-semibold text-right">
                        R$ {(item.quantidade * item.preco_unitario_editavel).toFixed(2)}
                      </p>
                    </div>
                  ))
                )}
              </CardContent>
              {carrinho.length > 0 && (
                <div className="p-4 border-t">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold">Total:</span>
                    <span className="text-xl font-bold text-green-600 dark:text-green-400">
                      R$ {total.toFixed(2)}
                    </span>
                  </div>
                </div>
              )}
            </Card>
            <Card className="mt-4">
              <CardHeader>
                <CardTitle>Condição de Pagamento</CardTitle>
              </CardHeader>
              <CardContent>
                <Select value={condicaoPagamento} onValueChange={setCondicaoPagamento}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="À vista">À vista</SelectItem>
                    <SelectItem value="30 dias">30 dias</SelectItem>
                    <SelectItem value="30/60 dias">30/60 dias</SelectItem>
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Etapa: Revisão */}
      {etapa === 'revisao' && clienteSelecionado && (
        <OrcamentoReview
          cliente={clienteSelecionado}
          carrinho={carrinho}
          condicaoPagamento={condicaoPagamento}
          total={total}
          onVoltar={handleVoltarEtapa}
          onFinalizar={handleFinalizar}
          orcamentoId={orcamentoId || undefined}
          loading={orcamentoLoading}
        />
      )}

      {/* Navegação */}
      <div className="flex justify-between items-center pt-4 border-t">
        <Button
          variant="outline"
          onClick={handleVoltarEtapa}
          disabled={etapa === 'cliente'}
        >
          <ArrowLeft size={16} className="mr-2" /> Voltar
        </Button>
        {etapa !== 'revisao' && (
          <Button
            onClick={handleAvancarEtapa}
            disabled={(etapa === 'cliente' && !clienteSelecionado) || (etapa === 'produtos' && carrinho.length === 0)}
          >
            Avançar
          </Button>
        )}
      </div>
    </div>
  );
}

