// /src/app/dashboard/orcamentos/novo/page.tsx
"use client";

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useProducts } from '@/hooks/useProducts';
import { Product, OrcamentoItem } from '@/types'; // Importe os tipos
import { apiService } from '@/services/apiService';
import { Header } from '@/components/dashboard/Header';
import ClientLayout from '@/components/ClientLayout';
import Button from '@/components/Button';
import Input from '@/components/Input';

function NovoOrcamentoPageContent() {
  const router = useRouter();
  const { products: allProducts } = useProducts(); 

  // Estado do formulário
  const [nomeCliente, setNomeCliente] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [itensOrcamento, setItensOrcamento] = useState<OrcamentoItem[]>([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Filtra os produtos com base na busca E que ainda não foram adicionados
  const produtosFiltrados = useMemo(() => {
    if (!searchTerm) return [];
    const idsItensAdicionados = new Set(itensOrcamento.map(item => item.produto_id));
    return allProducts.filter(p =>
        !idsItensAdicionados.has(p.id) &&
        p.nome.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [searchTerm, allProducts, itensOrcamento]);

  // Função para adicionar um produto ao orçamento
  const handleAddItem = (product: Product) => {
    const novoItem: OrcamentoItem = {
      produto_id: product.id,
      nome: product.nome,
      estoque_disponivel: product.quantidade_em_estoque,
      quantidade: 1, // Começa com quantidade 1
      preco_unitario: product.preco_venda,
    };
    setItensOrcamento(prevItens => [...prevItens, novoItem]);
    setSearchTerm(''); // Limpa a busca
  };

  // Função para atualizar a quantidade de um item
  const handleQuantidadeChange = (produto_id: number, novaQuantidade: number) => {
    setItensOrcamento(prevItens =>
      prevItens.map(item => {
        if (item.produto_id === produto_id) {
          // Validação para não exceder o estoque
          if (novaQuantidade > item.estoque_disponivel) {
            alert(`Estoque insuficiente! Disponível: ${item.estoque_disponivel}`);
            return { ...item, quantidade: item.estoque_disponivel };
          }
          return { ...item, quantidade: Math.max(1, novaQuantidade) }; // Garante no mínimo 1
        }
        return item;
      })
    );
  };
  
  // Função para remover um item do orçamento
  const handleRemoveItem = (produto_id: number) => {
    setItensOrcamento(prevItens => prevItens.filter(item => item.produto_id !== produto_id));
  }

  // Função para submeter o orçamento
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nomeCliente.trim()) {
        setError("Por favor, informe o nome do cliente.");
        return;
    }
    if (itensOrcamento.length === 0) {
        setError("Adicione pelo menos um produto ao orçamento.");
        return;
    }

    setIsLoading(true);
    setError('');

    const payload = {
        nome_cliente: nomeCliente,
        itens: itensOrcamento.map(({ produto_id, quantidade }) => ({ produto_id, quantidade })),
    };
    
    try {
        await apiService.post('/orcamentos/', payload);
        alert("Orçamento criado com sucesso!");
        router.push('/dashboard/orcamentos');
    } catch(err) {
        setError(err instanceof Error ? err.message : 'Falha ao criar orçamento.');
    } finally {
        setIsLoading(false);
    }
  };


  return (
    <>
      <Header>
        <h1 className="text-xl font-bold">Novo Orçamento</h1>
      </Header>
      <main className="flex-1 p-6 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Seção Cliente */}
            <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
                <h2 className="text-lg font-semibold mb-4">Dados do Cliente</h2>
                <Input
                    label="Nome do Cliente"
                    id="nomeCliente"
                    value={nomeCliente}
                    onChange={(e) => setNomeCliente(e.target.value)}
                    required
                />
            </div>

            {/* Seção Itens do Orçamento */}
            <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
                <h2 className="text-lg font-semibold mb-4">Itens do Orçamento</h2>
                
                {/* Tabela de itens adicionados */}
                <div className="mb-6 space-y-3">
                  {itensOrcamento.length === 0 ? (
                    <p className="text-center text-gray-500 py-4">Nenhum item adicionado.</p>
                  ) : (
                    itensOrcamento.map(item => (
                      <div key={item.produto_id} className="flex items-center gap-4 p-2 border-b dark:border-gray-700">
                          <span className="flex-1 font-medium">{item.nome}</span>
                          <Input label="" id={`qtd-${item.produto_id}`} type="number" value={item.quantidade} onChange={(e) => handleQuantidadeChange(item.produto_id, parseInt(e.target.value))} className="w-20 text-center" />
                          <button type="button" onClick={() => handleRemoveItem(item.produto_id)} className="text-red-500 hover:text-red-700">Remover</button>
                      </div>
                    ))
                  )}
                </div>

                {/* Busca de Produtos */}
                <div className="relative">
                  <Input 
                      label="Adicionar Produto" 
                      id="search-product" 
                      placeholder="Digite para buscar..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                  />
                  {searchTerm && produtosFiltrados.length > 0 && (
                      <ul className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-700 border dark:border-gray-600 rounded-md shadow-lg max-h-60 overflow-auto">
                          {produtosFiltrados.map(product => (
                              <li 
                                  key={product.id}
                                  onClick={() => handleAddItem(product)}
                                  className="px-4 py-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                              >
                                  {product.nome} (Estoque: {product.quantidade_em_estoque})
                              </li>
                          ))}
                      </ul>
                  )}
                </div>
            </div>

            {error && <p className="text-red-500 text-center font-semibold">{error}</p>}
            
            <div className="flex justify-end">
                <Button type="submit" disabled={isLoading}>
                    {isLoading ? "Salvando..." : "Salvar Orçamento"}
                </Button>
            </div>
          </form>
        </div>
      </main>
    </>
  );
}

// Wrapper que protege a rota, como fizemos na outra página
export default function NovoOrcamentoPageWrapper() {
  return (
    <ClientLayout>
      <NovoOrcamentoPageContent />
    </ClientLayout>
  );
}