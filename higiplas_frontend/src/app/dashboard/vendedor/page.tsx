// /src/app/dashboard/vendedor/page.tsx - VERSÃO CORRIGIDA

'use client';

import { useEffect, useState } from 'react';
// CORRIGIDO: 'Dashboard' foi removido pois não era usado no componente.
import { Cliente, Produto, ItemCarrinho } from '@/types/vendas'; 
import { useVendas } from '@/hooks/useVendas';
import toast from 'react-hot-toast';

// Componentes da UI (simplificados para o exemplo)
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  DollarSign, ShoppingCart, Users, Target, Search, Package, PlusCircle, XCircle 
} from 'lucide-react';

// CORRIGIDO: Definida uma interface para as props do InfoCard para evitar o erro de `any`
interface InfoCardProps {
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  title: string;
  value: string | number;
  color: string;
}

export default function VendasMobilePage() {
  // 1. Usando o hook correto com toda a lógica pronta
  const { 
    dashboard, 
    clientes, 
    produtos, 
    loading, 
    error, // A variável 'error' agora será usada
    carregarDashboard, 
    buscarClientes, 
    buscarProdutos, 
    registrarVenda,
    // CORRIGIDO: 'criarClienteRapido' removido pois não estava sendo usado na interface.
  } = useVendas();

  // 2. Estados para controlar a interface
  const [carrinho, setCarrinho] = useState<ItemCarrinho[]>([]);
  const [clienteSelecionado, setClienteSelecionado] = useState<Cliente | null>(null);
  const [termoBuscaCliente, setTermoBuscaCliente] = useState('');
  const [termoBuscaProduto, setTermoBuscaProduto] = useState('');
  
  // Carrega os dados iniciais quando a página abre
  useEffect(() => {
    carregarDashboard();
    buscarProdutos();
    buscarClientes();
    // CORRIGIDO: Adicionadas as dependências que o React solicitou
  }, [carregarDashboard, buscarProdutos, buscarClientes]);

  // 3. Funções para interagir com o carrinho
  const adicionarAoCarrinho = (produto: Produto) => {
    if (carrinho.find(item => item.id === produto.id)) {
      toast.error(`${produto.nome} já está no carrinho.`);
      return;
    }
    setCarrinho([...carrinho, { ...produto, id: produto.id, preco: produto.preco, quantidade: 1 }]);
  };

  const atualizarQuantidadeCarrinho = (produtoId: number, quantidade: number) => {
    setCarrinho(carrinho.map(item => 
      item.id === produtoId ? { ...item, quantidade: Math.max(0, quantidade) } : item
    ));
  };

  const removerDoCarrinho = (produtoId: number) => {
    setCarrinho(carrinho.filter(item => item.id !== produtoId));
  };
  
  const totalCarrinho = carrinho.reduce((acc, item) => acc + (item.preco * item.quantidade), 0);

  // 4. Função para finalizar a venda
  const handleFinalizarVenda = async () => {
    if (!clienteSelecionado) {
      toast.error('Selecione um cliente antes de finalizar a venda.');
      return;
    }
    if (carrinho.length === 0 || carrinho.every(item => item.quantidade === 0)) {
        toast.error('Adicione pelo menos um produto ao carrinho.');
        return;
    }

    const vendaPayload = {
      cliente_id: clienteSelecionado.id,
      itens: carrinho
        .filter(item => item.quantidade > 0)
        .map(item => ({ produto_id: item.id, quantidade: item.quantidade })),
    };

    try {
      await registrarVenda(vendaPayload);
      // Limpa tudo após o sucesso
      setCarrinho([]);
      setClienteSelecionado(null);
      setTermoBuscaCliente('');
      // Recarrega os produtos para atualizar o estoque
      buscarProdutos();
    } catch (e) {
      // O hook `useVendas` já mostra o toast de erro.
      console.error("Falha ao registrar venda:", e);
    }
  };

  // Renderização da Página
  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Área do Vendedor</h1>

      {/* ADICIONADO: Exibe a mensagem de erro, se houver */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
            <strong className="font-bold">Ocorreu um erro: </strong>
            <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Dashboard Resumido */}
      {dashboard && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <InfoCard icon={DollarSign} title="Vendas Hoje" value={`R$ ${dashboard.total_vendido_hoje.toFixed(2)}`} color="green" />
          <InfoCard icon={ShoppingCart} title="Pedidos Hoje" value={dashboard.quantidade_pedidos_hoje} color="blue" />
          <InfoCard icon={Users} title="Clientes Atendidos" value={dashboard.clientes_visitados_hoje} color="purple" />
          <InfoCard icon={Target} title="Meta do Dia" value={`${dashboard.progresso_meta.toFixed(1)}%`} color="yellow" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Coluna da Esquerda: Clientes e Produtos */}
        <div className="lg:col-span-2 space-y-6">
          {/* Card de Clientes */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Users /> Clientes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 mb-4">
                <Input placeholder="Buscar cliente por nome ou telefone..." value={termoBuscaCliente} onChange={(e) => setTermoBuscaCliente(e.target.value)} />
                <Button onClick={() => buscarClientes(termoBuscaCliente)}><Search className="w-4 h-4" /></Button>
              </div>
              {clienteSelecionado && (
                  <div className="bg-blue-100 border border-blue-300 text-blue-800 p-3 rounded-lg mb-4">
                      <strong>Cliente Selecionado:</strong> {clienteSelecionado.nome}
                  </div>
              )}
              <div className="max-h-60 overflow-y-auto space-y-2">
                {clientes.map(cliente => (
                  <div key={cliente.id} onClick={() => setClienteSelecionado(cliente)} 
                       className={`p-3 rounded-lg cursor-pointer ${clienteSelecionado?.id === cliente.id ? 'bg-blue-200' : 'bg-gray-100 hover:bg-gray-200'}`}>
                    <p className="font-semibold">{cliente.nome}</p>
                    <p className="text-sm text-gray-600">{cliente.telefone}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Card de Produtos */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Package /> Produtos Disponíveis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 mb-4">
                  <Input placeholder="Buscar produto por nome ou código..." value={termoBuscaProduto} onChange={e => setTermoBuscaProduto(e.target.value)} />
                  <Button onClick={() => buscarProdutos(termoBuscaProduto)}><Search className="w-4 h-4" /></Button>
              </div>
              <div className="max-h-96 overflow-y-auto space-y-2">
                {produtos.filter(p => p.nome.toLowerCase().includes(termoBuscaProduto.toLowerCase()) || p.codigo.toLowerCase().includes(termoBuscaProduto.toLowerCase())).map(produto => (
                    <div key={produto.id} className="flex justify-between items-center p-3 bg-gray-100 rounded-lg">
                        <div>
                            <p className="font-semibold">{produto.nome}</p>
                            <p className="text-sm text-gray-600">Estoque: {produto.estoque_disponivel} | R$ {produto.preco.toFixed(2)}</p>
                        </div>
                        <Button size="sm" onClick={() => adicionarAoCarrinho(produto)}><PlusCircle className="w-4 h-4 mr-2" /> Adicionar</Button>
                    </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Coluna da Direita: Carrinho */}
        <div className="lg:col-span-1">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2"><ShoppingCart /> Carrinho de Compras</CardTitle>
                </CardHeader>
                <CardContent>
                    {carrinho.length === 0 ? (
                        <p className="text-center text-gray-500 py-8">O carrinho está vazio.</p>
                    ) : (
                        <div className="space-y-4">
                            {carrinho.map(item => (
                                <div key={item.id} className="flex items-center gap-4">
                                    <div className="flex-1">
                                        <p className="font-semibold">{item.nome}</p>
                                        <p className="text-sm">R$ {item.preco.toFixed(2)}</p>
                                    </div>
                                    <Input 
                                        type="number" 
                                        value={item.quantidade} 
                                        onChange={(e) => atualizarQuantidadeCarrinho(item.id, parseInt(e.target.value))}
                                        className="w-20 text-center"
                                        min="0"
                                        max={item.estoque_disponivel}
                                    />
                                    <Button size="icon" variant="ghost" onClick={() => removerDoCarrinho(item.id)}>
                                        <XCircle className="w-5 h-5 text-red-500" />
                                    </Button>
                                </div>
                            ))}
                            <div className="border-t pt-4 mt-4">
                                <p className="text-xl font-bold text-right">
                                    Total: R$ {totalCarrinho.toFixed(2)}
                                </p>
                            </div>
                        </div>
                    )}
                    <Button 
                      className="w-full mt-6" 
                      onClick={handleFinalizarVenda} 
                      disabled={loading || !clienteSelecionado || carrinho.length === 0}
                    >
                      {loading ? 'Finalizando...' : 'Finalizar Venda'}
                    </Button>
                </CardContent>
            </Card>
        </div>
      </div>
    </div>
  );
}

// Componente auxiliar para os cards do dashboard
// CORRIGIDO: Props agora usam a interface InfoCardProps
const InfoCard = ({ icon: Icon, title, value, color }: InfoCardProps) => {
    const colors: { [key: string]: string } = {
      green: 'text-green-600',
      blue: 'text-blue-600',
      purple: 'text-purple-600',
      yellow: 'text-yellow-600',
    };
  
    return (
      <Card>
        <CardContent className="p-4 flex items-center">
          <Icon className={`w-8 h-8 mr-4 ${colors[color]}`} />
          <div>
            <p className="text-sm text-gray-500">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
          </div>
        </CardContent>
      </Card>
    );
  };