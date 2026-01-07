// /src/app/dashboard/vendedor/novo/page.tsx - CORREÇÃO DE DOWNLOAD

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useVendas } from '@/hooks/useVendas';
import { useOrcamentos } from '@/hooks/useOrcamentos';
import { Cliente, Produto } from '@/types/vendas';
import { ClienteV2 } from '@/types';
import toast from 'react-hot-toast'; 
import { apiService } from '@/services/apiService'; // Importa o apiService

import { ItemCarrinhoOrcamento, OrcamentoCreatePayload } from '@/types/orcamentos';
import { Header } from '@/components/dashboard/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { SugestoesCliente } from '@/components/orcamentos/SugestoesCliente';
import { useSugestoesOrcamento, SugestaoProduto } from '@/hooks/useSugestoesOrcamento';
import { 
  Users, Package, ShoppingCart, PlusCircle, Trash2, ArrowLeft, Send, Share2, UserPlus, History
} from 'lucide-react';

export default function NovoOrcamentoPage() {
  const router = useRouter();
  const {
    clientes,
    produtos,
    buscarClientes,
    buscarProdutos,
    criarClienteCompleto,
    loading: vendasLoading
  } = useVendas();
  const { criarOrcamento, loading: orcamentoLoading } = useOrcamentos();
  const { obterSugestoesCliente } = useSugestoesOrcamento();

  // Estados
  const [clienteSelecionado, setClienteSelecionado] = useState<Cliente | null>(null);
  const [carrinho, setCarrinho] = useState<ItemCarrinhoOrcamento[]>([]);
  const [condicaoPagamento, setCondicaoPagamento] = useState<string>('À vista');
  const [isClientModalOpen, setIsClientModalOpen] = useState(false);
  const [novoClienteNome, setNovoClienteNome] = useState('');
  const [novoClienteTelefone, setNovoClienteTelefone] = useState('');
  const [novoClienteCnpj, setNovoClienteCnpj] = useState('');
  const [novoClienteEmail, setNovoClienteEmail] = useState('');
  const [novoClienteBairro, setNovoClienteBairro] = useState('');
  const [novoClienteCidade, setNovoClienteCidade] = useState('');
  const [termoBuscaCliente, setTermoBuscaCliente] = useState('');
  const [termoBuscaProduto, setTermoBuscaProduto] = useState('');
  const [orcamentoFinalizado, setOrcamentoFinalizado] = useState<number | null>(null);
  const [isPersonalizadoModalOpen, setIsPersonalizadoModalOpen] = useState(false);
  const [novoItemNome, setNovoItemNome] = useState('');
  const [novoItemQuantidade, setNovoItemQuantidade] = useState(1);
  const [novoItemValor, setNovoItemValor] = useState(0);
  
  // Estado para sugestões de preços do cliente
  const [sugestoesCliente, setSugestoesCliente] = useState<Map<number, SugestaoProduto>>(new Map());

  useEffect(() => {
    buscarClientes();
    buscarProdutos();
  }, [buscarClientes, buscarProdutos]);
  
  // Recarregar produtos quando cliente é selecionado (para buscar range de preços)
  useEffect(() => {
    if (clienteSelecionado) {
      buscarProdutos(termoBuscaProduto, undefined, clienteSelecionado.id);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clienteSelecionado?.id]); // Recarrega apenas quando o ID do cliente muda
  
  // Carregar sugestões quando cliente é selecionado
  useEffect(() => {
    if (clienteSelecionado) {
      obterSugestoesCliente(clienteSelecionado.id).then(response => {
        if (response?.sugestoes) {
          const sugestoesMap = new Map<number, SugestaoProduto>();
          response.sugestoes.forEach(s => {
            sugestoesMap.set(s.produto_id, s);
          });
          setSugestoesCliente(sugestoesMap);
        }
      });
    } else {
      setSugestoesCliente(new Map());
    }
  }, [clienteSelecionado, obterSugestoesCliente]);
  
  const adicionarAoCarrinho = (produto: Produto, preco?: number, quantidade?: number) => {
    const itemExistente = carrinho.find(item => item.produto_id === produto.id);
    if (itemExistente) {
      // Atualizar item existente se preço ou quantidade foram fornecidos
      if (preco !== undefined || quantidade !== undefined) {
        setCarrinho(carrinho.map(item => {
          if (item.produto_id === produto.id) {
            return {
              ...item,
              preco_unitario_editavel: preco !== undefined ? preco : item.preco_unitario_editavel,
              quantidade: quantidade !== undefined ? quantidade : item.quantidade
            };
          }
          return item;
        }));
      }
      return;
    }
    
    // Verificar se há sugestão de preço para este cliente
    const sugestao = sugestoesCliente.get(produto.id);
    
    // Prioridade de preço: 1) parâmetro passado, 2) último preço do cliente, 3) preço do sistema
    let precoInicial = produto.preco;
    if (preco !== undefined) {
      precoInicial = preco;
    } else if (sugestao?.preco_cliente?.ultimo) {
      precoInicial = sugestao.preco_cliente.ultimo;
    }
    
    const novoItem: ItemCarrinhoOrcamento = {
        produto_id: produto.id,
        nome: produto.nome,
        estoque_disponivel: produto.estoque_disponivel,
        preco_original: produto.preco, // Preço do sistema
        preco_unitario_editavel: precoInicial,
        quantidade: quantidade !== undefined ? quantidade : 1,
        isPersonalizado: false,
        // Guardar dados de sugestão para exibir no carrinho
        preco_cliente: sugestao?.preco_cliente || null,
    };
    setCarrinho([...carrinho, novoItem]);
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

  const handleAplicarSugestao = (produtoId: number, preco: number, quantidade: number) => {
    const produto = produtos.find(p => p.id === produtoId);
    if (produto) {
      adicionarAoCarrinho(produto, preco, quantidade);
      toast.success('Sugestão aplicada!');
    }
  };
  
  const atualizarItemCarrinho = (itemKey: string | number, campo: 'quantidade' | 'preco', valor: number) => {
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
  
  const removerDoCarrinho = (itemKey: string | number) => {
    setCarrinho(carrinho.filter(item => {
      // Para itens normais, usar produto_id; para personalizados, usar nome como chave
      return item.produto_id ? item.produto_id !== itemKey : item.nome !== itemKey;
    }));
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
        setOrcamentoFinalizado(novoOrcamento.id);
        toast.success("Orçamento salvo! Gerando PDF...");

        try {
            // 1. Faz a requisição autenticada usando a nova função getBlob
            const response = await apiService.getBlob(`/orcamentos/${novoOrcamento.id}/pdf/`);
            const blob = await response.blob();
            
            // 2. Extrai o nome do arquivo do cabeçalho
            const contentDisposition = response.headers.get('content-disposition');
            let filename = `orcamento_${novoOrcamento.id}.pdf`;
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
                if (filenameMatch && filenameMatch.length > 1) {
                    filename = filenameMatch[1];
                }
            }

            // 3. Cria uma URL temporária para o arquivo
            const url = window.URL.createObjectURL(blob);
            
            // 4. Cria um link invisível e simula o clique para baixar
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();

            // 5. Limpa a URL e o link
            link.remove();
            window.URL.revokeObjectURL(url);

            toast.success("PDF gerado! Compartilhe com o cliente.");

        } catch (downloadError) {
            console.error("Erro ao baixar o PDF:", downloadError);
            toast.error("Orçamento salvo, mas falha ao gerar o PDF. Baixe-o na tela de Histórico.");
        }
    }
  };

  const handleShareWhatsApp = async () => {
      if(!clienteSelecionado) {
        toast.error('Selecione um cliente');
        return;
      }

      if (!clienteSelecionado.telefone) {
        toast.error('Cliente não possui telefone cadastrado');
        return;
      }

      if (!orcamentoFinalizado) {
        toast.error('Finalize o orçamento antes de compartilhar');
        return;
      }

      try {
        // Buscar o orçamento para obter o token de compartilhamento
        const response = await apiService.get(`/orcamentos/${orcamentoFinalizado}`);
        const orcamento = response?.data || response;
        
        if (!orcamento?.token_compartilhamento) {
          toast.error('Token de compartilhamento não disponível');
          return;
        }

        // Construir URL do PDF público
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;
        const pdfUrl = `${API_BASE_URL}/orcamentos/${orcamentoFinalizado}/pdf/public/${orcamento.token_compartilhamento}`;

        // Mensagem com link do PDF
        const mensagem = `Olá, ${clienteSelecionado.nome}! Segue o orçamento solicitado.\n\n📄 Acesse o PDF aqui: ${pdfUrl}\n\nEstou à disposição para qualquer dúvida.`;
        const fone = clienteSelecionado.telefone.replace(/\D/g, '');
        const whatsappUrl = `https://wa.me/55${fone}?text=${encodeURIComponent(mensagem)}`;
        window.open(whatsappUrl, '_blank');
      } catch (error) {
        console.error('Erro ao compartilhar:', error);
        toast.error('Erro ao compartilhar orçamento');
      }
  };

  const handleCriarNovoCliente = async () => {
    if (!novoClienteNome || !novoClienteTelefone) {
        toast.error("Nome/Razão Social e Telefone são obrigatórios.");
        return;
    }

    // Usar a nova função para criar cliente completo
    const novoCliente: ClienteV2 | null = await criarClienteCompleto(
      novoClienteNome,
      novoClienteTelefone,
      novoClienteCnpj,
      novoClienteEmail,
      novoClienteBairro,
      novoClienteCidade
    );

    if (novoCliente) {
        const clienteFormatado: Cliente = {
            id: novoCliente.id,
            nome: novoCliente.nome,
            telefone: novoCliente.telefone,
            bairro: novoCliente.bairro || null,
            cidade: novoCliente.cidade || null,
            ultima_compra: null
        };
        setClienteSelecionado(clienteFormatado);
        setIsClientModalOpen(false);
        // Limpar todos os campos
        setNovoClienteNome('');
        setNovoClienteTelefone('');
        setNovoClienteCnpj('');
        setNovoClienteEmail('');
        setNovoClienteBairro('');
        setNovoClienteCidade('');
        buscarClientes();
    }
  };

  if (orcamentoFinalizado) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6">
        <Card className="max-w-md text-center">
          <CardHeader>
            <CardTitle className="text-2xl text-green-600">Orçamento #{orcamentoFinalizado} Gerado com Sucesso!</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-6">O PDF do orçamento foi baixado. Você agora pode compartilhá-lo com o cliente.</p>
            <Button onClick={handleShareWhatsApp} className="w-full gap-2 mb-4" size="lg" style={{backgroundColor: '#25D366', color: 'white'}}><Share2/> Compartilhar no WhatsApp</Button>
            <Button onClick={() => router.push('/dashboard/vendedor')} className="w-full gap-2" variant="outline"><ArrowLeft/> Voltar para o Histórico</Button>
          </CardContent>
        </Card>
      </div>
    );
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
          <div className="lg:col-span-2 space-y-6">
              <Card>
                  <CardHeader><CardTitle className="flex items-center gap-2"><Users/> Selecionar Cliente</CardTitle></CardHeader>
                  <CardContent>
                    {clienteSelecionado ? (
                        <div className="p-4 bg-blue-100 rounded-lg flex justify-between items-center">
                            <p>Cliente: <span className="font-bold">{clienteSelecionado.nome}</span></p>
                            <Button variant="link" size="sm" onClick={() => setClienteSelecionado(null)}>Trocar cliente</Button>
                        </div>
                    ) : (
                        <>
                            <div className="flex gap-2">
                                <Input placeholder="Buscar cliente por nome..." value={termoBuscaCliente} onChange={(e) => setTermoBuscaCliente(e.target.value)} />
                                <Button onClick={() => setIsClientModalOpen(true)} className="gap-2 flex-shrink-0">
                                    <UserPlus size={16} /> Novo Cliente
                                </Button>
                            </div>
                            <div className="max-h-48 overflow-y-auto mt-2">
                                {clientes.filter(c => c.nome.toLowerCase().includes(termoBuscaCliente.toLowerCase())).map(c => (
                                    <div key={c.id} onClick={() => setClienteSelecionado(c)} className="p-2 hover:bg-gray-100 cursor-pointer rounded">{c.nome}</div>
                                ))}
                            </div>
                        </>
                    )}
                  </CardContent>
              </Card>
              {clienteSelecionado && (
                <SugestoesCliente
                  clienteId={clienteSelecionado.id}
                  onAplicarSugestao={handleAplicarSugestao}
                />
              )}
              <Card>
                  <CardHeader><CardTitle className="flex items-center gap-2"><Package/> Adicionar Produtos</CardTitle></CardHeader>
                  <CardContent>
                    <div className="flex gap-2 mb-2">
                      <Input placeholder="Buscar produto por nome ou código..." value={termoBuscaProduto} onChange={(e) => setTermoBuscaProduto(e.target.value)} className="flex-1" />
                      <Button onClick={() => setIsPersonalizadoModalOpen(true)} className="gap-2 flex-shrink-0" variant="default">
                        <PlusCircle size={16} /> Novo Produto
                      </Button>
                    </div>
                    <p className="text-xs text-gray-500 mb-2">Não encontrou o produto? Clique em &quot;Novo Produto&quot; para adicionar um item personalizado.</p>
                    <div className="max-h-60 overflow-y-auto mt-2">
                        {produtos.filter(p => p.nome.toLowerCase().includes(termoBuscaProduto.toLowerCase())).map(p => {
                            const sugestao = sugestoesCliente.get(p.id);
                            const temHistorico = (p.preco_cliente && p.preco_cliente.total_vendas > 0) || sugestao?.historico_disponivel;
                            const temRangePreco = p.preco_cliente && 
                                                  p.preco_cliente.minimo !== null && 
                                                  p.preco_cliente.maximo !== null &&
                                                  p.preco_cliente.minimo !== undefined &&
                                                  p.preco_cliente.maximo !== undefined;
                            
                            return (
                              <div key={p.id} className="flex justify-between items-center p-2 hover:bg-gray-100 rounded">
                                  <div className="flex-1">
                                      <div className="flex items-center gap-2">
                                        <p className="font-medium">{p.nome}</p>
                                        {temHistorico && (
                                          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full flex items-center gap-1">
                                            <History size={10} /> Já vendido
                                          </span>
                                        )}
                                      </div>
                                      <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500 mt-1">
                                        <span>Estoque: {p.estoque_disponivel}</span>
                                        <span>Sistema: R$ {p.preco.toFixed(2)}</span>
                                        {temRangePreco && (
                                          <span className="text-blue-600 font-semibold bg-blue-50 px-2 py-0.5 rounded">
                                            Cliente: R$ {p.preco_cliente!.minimo!.toFixed(2)} - R$ {p.preco_cliente!.maximo!.toFixed(2)}
                                          </span>
                                        )}
                                      </div>
                                  </div>
                                  <Button size="sm" onClick={() => adicionarAoCarrinho(p)}><PlusCircle size={14}/></Button>
                              </div>
                            );
                        })}
                    </div>
                  </CardContent>
              </Card>
          </div>
          
          <div className="lg:col-span-1 space-y-6">
              <Card>
                  <CardHeader><CardTitle className="flex items-center gap-2"><ShoppingCart/> Itens do Pedido</CardTitle></CardHeader>
                  <CardContent className="space-y-4 max-h-[50vh] overflow-y-auto">
                    {carrinho.length === 0 ? <p className="text-gray-500 text-center">Nenhum item.</p> : null}
                    {carrinho.map((item, index) => {
                      const itemKey = item.produto_id || item.nome || index;
                      return (
                        <div key={itemKey} className="p-3 border rounded-lg">
                            <div className="flex justify-between items-center">
                                <div className="flex items-center gap-2">
                                  <p className="font-semibold">{item.nome}</p>
                                  {item.isPersonalizado && (
                                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Novo Produto</span>
                                  )}
                                </div>
                                <Button variant="ghost" size="icon" onClick={() => removerDoCarrinho(itemKey)}>
                                    <Trash2 size={16} className="text-red-500"/>
                                </Button>
                            </div>
                            <div className="grid grid-cols-2 gap-2 mt-2">
                                <div>
                                    <label className="text-xs">Quantidade</label>
                                    <Input type="number" value={item.quantidade} onChange={(e) => atualizarItemCarrinho(itemKey, 'quantidade', parseInt(e.target.value) || 0)}/>
                                    {!item.isPersonalizado && item.estoque_disponivel !== undefined && item.quantidade > item.estoque_disponivel && (
                                      <p className="text-xs text-orange-500 mt-1">Estoque insuficiente!</p>
                                    )}
                                    {item.isPersonalizado && (
                                      <p className="text-xs text-blue-500 mt-1">Será criado no sistema</p>
                                    )}
                                </div>
                                <div>
                                    <label className="text-xs">Preço Unit. (R$)</label>
                                    <Input type="number" step="0.01" value={item.preco_unitario_editavel} onChange={(e) => atualizarItemCarrinho(itemKey, 'preco', parseFloat(e.target.value) || 0)}/>
                                    {/* Mostrar preço do sistema e range do cliente */}
                                    <p className="text-xs text-gray-400 mt-1">
                                      Sistema: R$ {item.preco_original.toFixed(2)}
                                    </p>
                                    {item.preco_cliente && (
                                      <p className="text-xs text-blue-500 mt-0.5">
                                        Cliente: R$ {item.preco_cliente.minimo?.toFixed(2)} - R$ {item.preco_cliente.maximo?.toFixed(2)}
                                      </p>
                                    )}
                                </div>
                            </div>
                        </div>
                      );
                    })}
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
                                  <SelectItem value="7 dias">7 dias</SelectItem>
                                  <SelectItem value="14 dias">14 dias</SelectItem>
                                  <SelectItem value="21 dias">21 dias</SelectItem>
                                  <SelectItem value="30 dias">30 dias</SelectItem>
                                  <SelectItem value="45 dias">45 dias</SelectItem>
                                  <SelectItem value="60 dias">60 dias</SelectItem>
                                  <SelectItem value="90 dias">90 dias</SelectItem>
                                  <SelectItem value="30/60 dias">30/60 dias</SelectItem>
                                  <SelectItem value="30/60/90 dias">30/60/90 dias</SelectItem>
                                  <SelectItem value="Entrada + 30 dias">Entrada + 30 dias</SelectItem>
                                  <SelectItem value="Entrada + 60 dias">Entrada + 60 dias</SelectItem>
                                  <SelectItem value="Boleto 30 dias">Boleto 30 dias</SelectItem>
                                  <SelectItem value="Boleto 60 dias">Boleto 60 dias</SelectItem>
                                  <SelectItem value="Cheque 30 dias">Cheque 30 dias</SelectItem>
                                  <SelectItem value="Cheque 60 dias">Cheque 60 dias</SelectItem>
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
      {isClientModalOpen && (
          <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
              <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                  <CardHeader>
                      <CardTitle className="flex items-center gap-2"><UserPlus /> Cadastrar Novo Cliente</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                              <label className="text-sm font-medium">Nome/Razão Social *</label>
                              <Input
                                  placeholder="Nome completo ou razão social"
                                  value={novoClienteNome}
                                  onChange={(e) => setNovoClienteNome(e.target.value)}
                              />
                          </div>
                          <div>
                              <label className="text-sm font-medium">Telefone (WhatsApp) *</label>
                              <Input
                                  placeholder="Ex: 98912345678"
                                  value={novoClienteTelefone}
                                  onChange={(e) => setNovoClienteTelefone(e.target.value)}
                              />
                          </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                              <label className="text-sm font-medium">CNPJ/CPF</label>
                              <Input
                                  placeholder="CNPJ ou CPF"
                                  value={novoClienteCnpj}
                                  onChange={(e) => setNovoClienteCnpj(e.target.value)}
                              />
                          </div>
                          <div>
                              <label className="text-sm font-medium">Email</label>
                              <Input
                                  placeholder="cliente@exemplo.com"
                                  value={novoClienteEmail}
                                  onChange={(e) => setNovoClienteEmail(e.target.value)}
                              />
                          </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                              <label className="text-sm font-medium">Bairro</label>
                              <Input
                                  placeholder="Bairro"
                                  value={novoClienteBairro}
                                  onChange={(e) => setNovoClienteBairro(e.target.value)}
                              />
                          </div>
                          <div>
                              <label className="text-sm font-medium">Cidade</label>
                              <Input
                                  placeholder="Cidade"
                                  value={novoClienteCidade}
                                  onChange={(e) => setNovoClienteCidade(e.target.value)}
                              />
                          </div>
                      </div>
                  </CardContent>
                  <div className="flex justify-end gap-4 p-6 pt-0">
                      <Button variant="ghost" onClick={() => setIsClientModalOpen(false)}>Cancelar</Button>
                      <Button onClick={handleCriarNovoCliente} disabled={vendasLoading}>
                          {vendasLoading ? 'Salvando...' : 'Salvar Cliente'}
                      </Button>
                  </div>
              </Card>
          </div>
        )}
      {isPersonalizadoModalOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PlusCircle /> Adicionar Item Personalizado
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600">
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
    </>
  );
}