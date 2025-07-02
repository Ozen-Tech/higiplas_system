"use client";

import { useEffect, useState } from 'react';
import StockMovementModal from '@/components/StockMovementModal';


// Vamos definir um tipo para nossos produtos, aproveitando o TypeScript!
interface Product {
  id: number;
  nome: string;
  descricao: string;
  preco: number;
  estoque_atual: number;
  empresa_id: number;
}

export default function DashboardPage() {
  // Estado para guardar a lista de produtos que virá da API
  const [products, setProducts] = useState<Product[]>([]);
  // Estado para controlar a mensagem de carregamento ou erro
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Estado para controlar a abertura do modal e o produto selecionado
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  // FUNÇÕES PARA ABRIR E FECHAR O MODAL
  const handleOpenModal = (product: Product) => {
    setSelectedProduct(product);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setSelectedProduct(null);
    setIsModalOpen(false);
  };

  // FUNÇÃO QUE SERÁ CHAMADA QUANDO O MODAL FOR ENVIADO
  const handleMovementSubmit = async (tipo: 'entrada' | 'saida', quantidade: number) => {
    if (!selectedProduct) return;

    const token = localStorage.getItem('authToken');
    if (!token) {
      setError("Sessão expirada. Faça login novamente.");
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/movimentacoes/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          produto_id: selectedProduct.id,
          tipo: tipo,
          quantidade: quantidade,
        }),
      });


    if (!response.ok) {
        // Vamos capturar o corpo do erro e LOGAR NO CONSOLE antes de qualquer outra coisa.
        const errorData = await response.json();
        console.error("DETALHES DO ERRO DA API:", errorData); // <-- ESTA É A LINHA MAIS IMPORTANTE
        
        // Agora, tentamos extrair a mensagem de erro para o usuário
        // A mensagem pode estar em um array 'detail'
        const errorMessage = errorData.detail?.[0]?.msg || errorData.detail || 'Falha ao registrar movimentação.';
        throw new Error(errorMessage);
      }
  
      const updatedProduct = await response.json();
      
      setProducts(currentProducts => 
        currentProducts.map(p => 
          p.id === updatedProduct.id ? updatedProduct : p
        )
      );
  
      alert('Movimentação registrada com sucesso!');
      handleCloseModal();
  
    } catch (err: any) {
      // O catch agora vai receber a mensagem de erro mais detalhada
      alert(`Erro: ${err.message}`);
    }
  };

  useEffect(() => {
    // Função assíncrona para buscar os dados
    const fetchProducts = async () => {
      // 1. Pega o token do armazenamento local
      const token = localStorage.getItem('authToken');

      if (!token) {
        setError("Token não encontrado. Por favor, faça login novamente.");
        setLoading(false);
        // Opcional: redirecionar para a página de login
        // window.location.href = '/'; 
        return;
      }

      try {
        // 2. Faz a requisição para a API de produtos
        const response = await fetch('http://localhost:8000/produtos', {
          method: 'GET',
          headers: {
            // 3. A MÁGICA ACONTECE AQUI!
            // Enviamos o token no cabeçalho de autorização.
            // O formato "Bearer <token>" é um padrão universal.
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          // Se a resposta for 401 (Não Autorizado), o token pode ter expirado
          if (response.status === 401) {
            throw new Error('Sua sessão expirou. Por favor, faça login novamente.');
          }
          throw new Error('Falha ao buscar os produtos.');
        }

        const data: Product[] = await response.json();
        setProducts(data); // 4. Guarda os produtos no nosso estado

      } catch (err: any) {
        setError(err.message);
      } finally {
        // Independente de sucesso ou erro, paramos o carregamento
        setLoading(false);
      }
    };

    fetchProducts();
  }, []); // O array vazio [] garante que isso rode apenas uma vez

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Dashboard de Produtos</h1>

        {loading && <p className="text-center text-gray-500">Carregando produtos...</p>}
        
        {error && <p className="text-center text-red-500 bg-red-100 p-3 rounded-md">{error}</p>}

        {!loading && !error && (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
                <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrição</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estoque Atual</th>
                {/* 1. NOVO CABEÇALHO */}
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
                {products.map((product) => (
                <tr key={product.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{product.nome}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.descricao}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.estoque_atual}</td>
                    {/* 2. NOVA CÉLULA COM O BOTÃO */}
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                        onClick={() => handleOpenModal(product)} 
                        className="text-indigo-600 hover:text-indigo-900"
                    >
                        Movimentar
                    </button>
                    </td>
                </tr>
                ))}
            </tbody>
            </table>
          </div>
        )}
      </div>
      {selectedProduct && (
    <StockMovementModal
      isOpen={isModalOpen}
      onClose={handleCloseModal}
      onSubmit={handleMovementSubmit}
      productName={selectedProduct.nome}
    />
  )}
    </main>
  );
}