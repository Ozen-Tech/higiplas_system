// /src/app/dashboard/vendedor/novo/page.tsx - CORRIGIDO

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useVendas } from '@/hooks/useVendas';
import { useOrcamentos } from '@/hooks/useOrcamentos';
import { Cliente, Produto } from '@/types/vendas';
import { ItemCarrinhoOrcamento, OrcamentoCreatePayload } from '@/types/orcamentos';
import toast from 'react-hot-toast';

import { Header } from '@/components/dashboard/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  Users, Package, ShoppingCart, PlusCircle, Trash2, ArrowLeft, Send, Share2 
  // CORREÇÃO: Ícones 'Search' e 'Save' removidos da importação
} from 'lucide-react';

export default function NovoOrcamentoPage() {
  const router = useRouter();
  const { clientes, produtos, buscarClientes, buscarProdutos } = useVendas();
  const { criarOrcamento, loading: orcamentoLoading } = useOrcamentos();

  // Estados do formulário
  const [clienteSelecionado, setClienteSelecionado] = useState<Cliente | null>(null);
  const [carrinho, setCarrinho] = useState<ItemCarrinhoOrcamento[]>([]);
  const [condicaoPagamento, setCondicaoPagamento] = useState<string>('À vista');
  
  // Estados da UI
  const [termoBuscaCliente, setTermoBuscaCliente] = useState('');
  const [termoBuscaProduto, setTermoBuscaProduto] = useState('');
  const [orcamentoFinalizado, setOrcamentoFinalizado] = useState<number | null>(null);

  useEffect(() => {
    // Busca inicial
    buscarClientes();
    buscarProdutos();
  }, [buscarClientes, buscarProdutos]);
  
  const adicionarAoCarrinho = (produto: Produto) => {
    if (carrinho.find(item => item.produto_id === produto.id)) return;
    const novoItem: ItemCarrinhoOrcamento = {
        produto_id: produto.id,
        nome: produto.nome,
        estoque_disponivel: produto.estoque_disponivel,
        preco_original: produto.preco,
        preco_unitario_editavel: produto.preco,
        quantidade: 1,
    };
    setCarrinho([...carrinho, novoItem]);
  };
  
  const atualizarItemCarrinho = (produtoId: number, campo: 'quantidade' | 'preco', valor: number) => {
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
  
  const removerDoCarrinho = (produtoId: number) => {
    setCarrinho(carrinho.filter(item => item.produto_id !== produtoId));
  };

  const totalCarrinho = carrinho.reduce((acc, item) => acc + (item.preco_unitario_editavel * item.quantidade), 0);

  const handleFinalizar = async () => {
    if (!clienteSelecionado || carrinho.length === 0) {
        toast.error('Selecione um cliente e adicione produtos ao carrinho.');
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
        setOrcamentoFinalizado(novoOrcamento.id);
        const pdfUrl = `${process.env.NEXT_PUBLIC_API_URL}/orcamentos/${novoOrcamento.id}/pdf/`;
        window.open(pdfUrl, '_blank');
        toast.success("PDF gerado! Compartilhe com o cliente.");
    }
  };

  const handleShareWhatsApp = () => {
      if(!clienteSelecionado) return;
      const mensagem = `Olá, ${clienteSelecionado.nome}! Segue o orçamento solicitado. Estou à disposição para qualquer dúvida.`;
      const fone = clienteSelecionado.telefone.replace(/\D/g, ''); // Remove não-números
      const whatsappUrl = `https://wa.me/55${fone}?text=${encodeURIComponent(mensagem)}`;
      window.open(whatsappUrl, '_blank');
  };

  if(orcamentoFinalizado) {
      return (
          <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6">
              <Card className="max-w-md text-center">
                  <CardHeader>
                      <CardTitle className="text-2xl text-green-600">Orçamento #{orcamentoFinalizado} Gerado com Sucesso!</CardTitle>
                  </CardHeader>
                  <CardContent>
                      <p className="mb-6">O PDF do orçamento foi baixado. Você agora pode compartilhá-lo com o cliente.</p>
                      <Button onClick={handleShareWhatsApp} className="w-full gap-2 mb-4" size="lg" style={{backgroundColor: '#25D366', color: 'white'}}>
                          <Share2/> Compartilhar no WhatsApp
                      </Button>
                      <Button onClick={() => router.push('/dashboard/vendedor')} className="w-full gap-2" variant="outline">
                          <ArrowLeft/> Voltar para o Histórico
                      </Button>
                  </CardContent>
              </Card>
          </div>
      )
  }

  return (
    <>
      <Header>
          <Button variant="ghost" onClick={() => router.back()} className="gap-2">
            <ArrowLeft size={16}/> Voltar
          </Button>
          <h1 className="text-xl font-bold">Novo Orçamento</h1>
      </Header>
      <main className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Coluna Esquerda: Clientes e Produtos */}
          <div className="lg:col-span-2 space-y-6">
              <Card>
                  <CardHeader><CardTitle className="flex items-center gap-2"><Users/> Selecionar Cliente</CardTitle></CardHeader>
                  <CardContent>
                    {clienteSelecionado ? (
                        <div className="p-4 bg-blue-100 rounded-lg">
                            <p>Cliente: <span className="font-bold">{clienteSelecionado.nome}</span></p>
                            <Button variant="link" size="sm" onClick={() => setClienteSelecionado(null)}>Trocar cliente</Button>
                        </div>
                    ) : (
                        <>
                            <Input placeholder="Buscar cliente por nome..." value={termoBuscaCliente} onChange={(e) => setTermoBuscaCliente(e.target.value)} />
                            <div className="max-h-48 overflow-y-auto mt-2">
                                {clientes.filter(c => c.nome.toLowerCase().includes(termoBuscaCliente.toLowerCase())).map(c => (
                                    <div key={c.id} onClick={() => setClienteSelecionado(c)} className="p-2 hover:bg-gray-100 cursor-pointer rounded">{c.nome}</div>
                                ))}
                            </div>
                        </>
                    )}
                  </CardContent>
              </Card>

              <Card>
                  <CardHeader><CardTitle className="flex items-center gap-2"><Package/> Adicionar Produtos</CardTitle></CardHeader>
                  <CardContent>
                    <Input placeholder="Buscar produto por nome ou código..." value={termoBuscaProduto} onChange={(e) => setTermoBuscaProduto(e.target.value)} />
                    <div className="max-h-60 overflow-y-auto mt-2">
                        {produtos.filter(p => p.nome.toLowerCase().includes(termoBuscaProduto.toLowerCase())).map(p => (
                            <div key={p.id} className="flex justify-between items-center p-2 hover:bg-gray-100 rounded">
                                <div>
                                    <p>{p.nome}</p>
                                    <p className="text-xs text-gray-500">Estoque: {p.estoque_disponivel}</p>
                                </div>
                                <Button size="sm" onClick={() => adicionarAoCarrinho(p)}><PlusCircle size={14}/></Button>
                            </div>
                        ))}
                    </div>
                  </CardContent>
              </Card>
          </div>
          
          {/* Coluna Direita: Resumo do Orçamento */}
          <div className="lg:col-span-1 space-y-6">
              <Card>
                  <CardHeader><CardTitle className="flex items-center gap-2"><ShoppingCart/> Itens do Pedido</CardTitle></CardHeader>
                  <CardContent className="space-y-4 max-h-[50vh] overflow-y-auto">
                    {carrinho.length === 0 ? <p className="text-gray-500 text-center">Nenhum item.</p> : null}
                    {carrinho.map(item => (
                        <div key={item.produto_id} className="p-3 border rounded-lg">
                            <div className="flex justify-between items-center">
                                <p className="font-semibold">{item.nome}</p>
                                <Button variant="ghost" size="icon" onClick={() => removerDoCarrinho(item.produto_id)}>
                                    <Trash2 size={16} className="text-red-500"/>
                                </Button>
                            </div>
                            <div className="grid grid-cols-2 gap-2 mt-2">
                                <div>
                                    <label className="text-xs">Quantidade</label>
                                    <Input type="number" value={item.quantidade} onChange={(e) => atualizarItemCarrinho(item.produto_id, 'quantidade', parseInt(e.target.value))}/>
                                    {item.quantidade > item.estoque_disponivel && <p className="text-xs text-orange-500 mt-1">Estoque insuficiente!</p>}
                                </div>
                                <div>
                                    <label className="text-xs">Preço Unit. (R$)</label>
                                    <Input type="number" value={item.preco_unitario_editavel} onChange={(e) => atualizarItemCarrinho(item.produto_id, 'preco', parseFloat(e.target.value))}/>
                                </div>
                            </div>
                        </div>
                    ))}
                  </CardContent>
              </Card>
              <Card>
                  <CardHeader><CardTitle>Finalização</CardTitle></CardHeader>
                  <CardContent className="space-y-4">
                      <div>
                          <label>Condição de Pagamento</label>
                          <Select value={condicaoPagamento} onValueChange={setCondicaoPagamento}>
                              <SelectTrigger><SelectValue placeholder="Selecione..." /></SelectTrigger>
                              <SelectContent>
                                  <SelectItem value="À vista">À vista</SelectItem>
                                  <SelectItem value="30 dias">30 dias</SelectItem>
                                  <SelectItem value="30/60 dias">30/60 dias</SelectItem>
                              </SelectContent>
                          </Select>
                      </div>
                      <div className="text-2xl font-bold text-right">
                          Total: R$ {totalCarrinho.toFixed(2)}
                      </div>
                      <Button onClick={handleFinalizar} disabled={orcamentoLoading} className="w-full gap-2" size="lg">
                          {orcamentoLoading ? 'Salvando...' : <><Send size={16}/> Finalizar e Gerar PDF</>}
                      </Button>
                  </CardContent>
              </Card>
          </div>
      </main>
    </>
  );
}