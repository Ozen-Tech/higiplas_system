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
import { ShoppingCart, Trash2, ArrowLeft, PlusCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { apiService } from '@/services/apiService';

type Etapa = 'cliente' | 'produtos' | 'revisao';

export function OrcamentoBuilder() {
  const { clientes, produtos, buscarClientes, buscarProdutos, criarClienteCompleto, loading: vendasLoading } = useVendas();
  const { criarOrcamento, loading: orcamentoLoading } = useOrcamentos();

  const [etapa, setEtapa] = useState<Etapa>('cliente');
  const [clienteSelecionado, setClienteSelecionado] = useState<Cliente | null>(null);
  const [carrinho, setCarrinho] = useState<ItemCarrinhoOrcamento[]>([]);
  const [condicaoPagamento, setCondicaoPagamento] = useState<string>('5 dias');
  const [condicaoPersonalizada, setCondicaoPersonalizada] = useState<string>('');
  const [orcamentoId, setOrcamentoId] = useState<number | null>(null);
  const [isPersonalizadoModalOpen, setIsPersonalizadoModalOpen] = useState(false);
  const [novoItemNome, setNovoItemNome] = useState('');
  const [novoItemQuantidade, setNovoItemQuantidade] = useState(1);
  const [novoItemValor, setNovoItemValor] = useState(0);

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
      isPersonalizado: false,
    };
    setCarrinho([...carrinho, novoItem]);
    toast.success(`${produto.nome} adicionado ao carrinho`);
  };

  const adicionarItemPersonalizado = () => {
    if (!novoItemNome || novoItemQuantidade <= 0 || novoItemValor <= 0) {
      toast.error('Preencha todos os campos corretamente.');
      return;
    }

    const novoItem: ItemCarrinhoOrcamento = {
      nome_produto_personalizado: novoItemNome,
      nome: novoItemNome,
      quantidade: novoItemQuantidade,
      preco_original: novoItemValor,
      preco_unitario_editavel: novoItemValor,
      isPersonalizado: true,
    };
    
    setCarrinho([...carrinho, novoItem]);
    setNovoItemNome('');
    setNovoItemQuantidade(1);
    setNovoItemValor(0);
    setIsPersonalizadoModalOpen(false);
    toast.success('Item personalizado adicionado!');
  };

  const atualizarItem = (itemKey: number | string | undefined, campo: 'quantidade' | 'preco', valor: number) => {
    setCarrinho(carrinho.map(item => {
      // Para itens normais, usar produto_id; para personalizados, usar nome como chave
      const itemKeyMatch = item.produto_id ? item.produto_id === itemKey : item.nome === itemKey;
      if (itemKeyMatch) {
        return {
          ...item,
          [campo === 'quantidade' ? 'quantidade' : 'preco_unitario_editavel']: Math.max(0, valor)
        };
      }
      return item;
    }));
  };

  const removerItem = (itemKey: number | string | undefined) => {
    setCarrinho(carrinho.filter(item => {
      // Para itens normais, usar produto_id; para personalizados, usar nome como chave
      return item.produto_id ? item.produto_id !== itemKey : item.nome !== itemKey;
    }));
    toast.success('Item removido do carrinho');
  };

  const total = carrinho.reduce((acc, item) => acc + (item.preco_unitario_editavel * item.quantidade), 0);

  const handleFinalizar = async () => {
    if (!clienteSelecionado || carrinho.length === 0) {
      toast.error('Selecione um cliente e adicione produtos ao carrinho');
      return;
    }

    if (condicaoPagamento === 'personalizado' && !condicaoPersonalizada.trim()) {
      toast.error('Informe a condição de pagamento personalizada');
      return;
    }

    const condicaoFinal = condicaoPagamento === 'personalizado' 
      ? condicaoPersonalizada.trim() 
      : condicaoPagamento;

    const payload: OrcamentoCreatePayload = {
      cliente_id: clienteSelecionado.id,
      condicao_pagamento: condicaoFinal,
      status: 'ENVIADO',
      itens: carrinho.map(item => {
        if (item.isPersonalizado && item.nome_produto_personalizado) {
          // Item personalizado: enviar nome_produto_personalizado ao invés de produto_id
          return {
            nome_produto_personalizado: item.nome_produto_personalizado,
            quantidade: item.quantidade,
            preco_unitario: item.preco_unitario_editavel
          };
        } else {
          // Item normal: enviar produto_id
          return {
            produto_id: item.produto_id!,
            quantidade: item.quantidade,
            preco_unitario: item.preco_unitario_editavel
          };
        }
      })
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
    <div className="space-y-4 sm:space-y-6">
      {/* Indicador de Etapas - Otimizado para mobile */}
      <div className="flex items-center justify-between sm:justify-center gap-1 sm:gap-2 mb-4 sm:mb-6 px-2">
        <div className={`flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-4 py-2 sm:py-2.5 rounded-lg text-xs sm:text-sm flex-1 sm:flex-initial min-h-[44px] ${etapa === 'cliente' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 font-semibold' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'}`}>
          <span className="hidden sm:inline">1. </span>
          <span>Cliente</span>
        </div>
        <div className="w-2 sm:w-8 h-0.5 sm:h-1 bg-gray-300 dark:bg-gray-600 flex-shrink-0"></div>
        <div className={`flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-4 py-2 sm:py-2.5 rounded-lg text-xs sm:text-sm flex-1 sm:flex-initial min-h-[44px] ${etapa === 'produtos' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 font-semibold' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'}`}>
          <span className="hidden sm:inline">2. </span>
          <span>Produtos</span>
        </div>
        <div className="w-2 sm:w-8 h-0.5 sm:h-1 bg-gray-300 dark:bg-gray-600 flex-shrink-0"></div>
        <div className={`flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-4 py-2 sm:py-2.5 rounded-lg text-xs sm:text-sm flex-1 sm:flex-initial min-h-[44px] ${etapa === 'revisao' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 font-semibold' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'}`}>
          <span className="hidden sm:inline">3. </span>
          <span>Revisão</span>
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

      {/* Etapa: Produtos - Otimizado para mobile */}
      {etapa === 'produtos' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
          <div className="lg:col-span-2 order-2 lg:order-1 space-y-4">
            <ProdutoSelector
              produtos={produtos}
              carrinho={carrinho}
              onAdicionarProduto={adicionarProduto}
              loading={vendasLoading}
            />
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium mb-1">Não encontrou o produto?</p>
                    <p className="text-xs text-gray-500">Adicione um item personalizado que será criado automaticamente no sistema.</p>
                  </div>
                  <Button 
                    onClick={() => setIsPersonalizadoModalOpen(true)} 
                    className="gap-2 w-full sm:w-auto"
                    variant="default"
                  >
                    <PlusCircle size={16} /> Novo Produto
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
          <div className="lg:col-span-1 order-1 lg:order-2">
            <Card className="sticky top-20 lg:top-4">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                  <ShoppingCart size={18} className="sm:w-5 sm:h-5" /> 
                  <span>Carrinho ({carrinho.length})</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 sm:space-y-4 max-h-[50vh] sm:max-h-[60vh] overflow-y-auto">
                {carrinho.length === 0 ? (
                  <p className="text-center text-gray-500 dark:text-gray-400 py-8 text-sm">Carrinho vazio</p>
                ) : (
                  carrinho.map((item, index) => {
                    const itemKey = item.produto_id || item.nome || index;
                    return (
                      <div key={itemKey} className="p-3 sm:p-4 border rounded-lg space-y-2 sm:space-y-3 bg-white dark:bg-gray-800">
                        <div className="flex justify-between items-start gap-2">
                          <div className="flex items-center gap-2 flex-1">
                            <p className="font-medium text-sm sm:text-base flex-1 line-clamp-2">{item.nome}</p>
                            {item.isPersonalizado && (
                              <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">Novo</span>
                            )}
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removerItem(itemKey)}
                            className="h-8 w-8 sm:h-9 sm:w-9 flex-shrink-0"
                            title="Remover"
                          >
                            <Trash2 size={16} className="text-red-500" />
                          </Button>
                        </div>
                        <div className="grid grid-cols-2 gap-2 sm:gap-3">
                          <div>
                            <label className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-1 block">Qtd</label>
                            <Input
                              type="number"
                              inputMode="numeric"
                              value={item.quantidade}
                              onChange={(e) => atualizarItem(itemKey, 'quantidade', parseInt(e.target.value) || 0)}
                              className="h-10 sm:h-9 text-sm sm:text-base"
                              min="1"
                            />
                          </div>
                          <div>
                            <label className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-1 block">Preço</label>
                            <Input
                              type="number"
                              inputMode="decimal"
                              step="0.01"
                              value={item.preco_unitario_editavel}
                              onChange={(e) => atualizarItem(itemKey, 'preco', parseFloat(e.target.value) || 0)}
                              className="h-10 sm:h-9 text-sm sm:text-base"
                              min="0"
                            />
                          </div>
                        </div>
                        {!item.isPersonalizado && item.estoque_disponivel !== undefined && item.quantidade > item.estoque_disponivel && (
                          <p className="text-xs sm:text-sm text-orange-500 dark:text-orange-400 font-medium">
                            ⚠️ Estoque insuficiente! (Disponível: {item.estoque_disponivel})
                          </p>
                        )}
                        {item.isPersonalizado && (
                          <p className="text-xs sm:text-sm text-blue-500 dark:text-blue-400 font-medium">
                            ℹ️ Será criado no sistema
                          </p>
                        )}
                        <p className="text-sm sm:text-base font-semibold text-right text-green-600 dark:text-green-400">
                          R$ {(item.quantidade * item.preco_unitario_editavel).toFixed(2)}
                        </p>
                      </div>
                    );
                  })
                )}
              </CardContent>
              {carrinho.length > 0 && (
                <div className="p-3 sm:p-4 border-t bg-gray-50 dark:bg-gray-900">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-sm sm:text-base">Total:</span>
                    <span className="text-lg sm:text-xl font-bold text-green-600 dark:text-green-400">
                      R$ {total.toFixed(2)}
                    </span>
                  </div>
                </div>
              )}
            </Card>
            <Card className="mt-3 sm:mt-4">
              <CardHeader className="pb-3">
                <CardTitle className="text-base sm:text-lg">Condição de Pagamento</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Select value={condicaoPagamento} onValueChange={(value) => {
                  setCondicaoPagamento(value);
                  if (value !== 'personalizado') {
                    setCondicaoPersonalizada('');
                  }
                }}>
                  <SelectTrigger className="h-11 sm:h-10">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="5 dias">5 dias</SelectItem>
                    <SelectItem value="7 dias">7 dias</SelectItem>
                    <SelectItem value="personalizado">Personalizado</SelectItem>
                  </SelectContent>
                </Select>
                {condicaoPagamento === 'personalizado' && (
                  <Input
                    placeholder="Ex: 15 dias, 30 dias, À vista..."
                    value={condicaoPersonalizada}
                    onChange={(e) => setCondicaoPersonalizada(e.target.value)}
                    className="h-11 sm:h-10"
                  />
                )}
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

      {/* Navegação - Otimizada para mobile */}
      <div className="flex justify-between items-center gap-3 pt-4 border-t sticky bottom-0 bg-white dark:bg-gray-900 pb-2 sm:pb-0 sm:relative sm:bg-transparent">
        <Button
          variant="outline"
          onClick={handleVoltarEtapa}
          disabled={etapa === 'cliente'}
          className="min-h-[44px] flex-1 sm:flex-initial"
        >
          <ArrowLeft size={18} className="mr-2" /> 
          <span className="hidden sm:inline">Voltar</span>
          <span className="sm:hidden">Voltar</span>
        </Button>
        {etapa !== 'revisao' && (
          <Button
            onClick={handleAvancarEtapa}
            disabled={(etapa === 'cliente' && !clienteSelecionado) || (etapa === 'produtos' && carrinho.length === 0)}
            className="min-h-[44px] flex-1 sm:flex-initial"
          >
            Avançar →
          </Button>
        )}
      </div>

      {/* Modal de Item Personalizado */}
      {isPersonalizadoModalOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PlusCircle /> Adicionar Item Personalizado
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Este produto será criado automaticamente no sistema quando o orçamento for salvo.
              </p>
              <div>
                <label className="text-sm font-medium">Nome do Produto *</label>
                <Input
                  placeholder="Ex: Produto especial sob medida"
                  value={novoItemNome}
                  onChange={(e) => setNovoItemNome(e.target.value)}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Quantidade *</label>
                  <Input
                    type="number"
                    min="1"
                    value={novoItemQuantidade}
                    onChange={(e) => setNovoItemQuantidade(parseInt(e.target.value) || 1)}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Valor Unitário (R$) *</label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    value={novoItemValor}
                    onChange={(e) => setNovoItemValor(parseFloat(e.target.value) || 0)}
                  />
                </div>
              </div>
            </CardContent>
            <div className="flex justify-end gap-4 p-6 pt-0">
              <Button variant="ghost" onClick={() => {
                setIsPersonalizadoModalOpen(false);
                setNovoItemNome('');
                setNovoItemQuantidade(1);
                setNovoItemValor(0);
              }}>
                Cancelar
              </Button>
              <Button onClick={adicionarItemPersonalizado}>
                Adicionar
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

