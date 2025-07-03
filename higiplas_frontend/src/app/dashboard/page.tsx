"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import StockMovementModal from "@/components/StockMovementModal";

interface Product {
  id: number;
  nome: string;
  codigo: string;
  categoria: string;
  descricao?: string;
  preco_custo?: number;
  preco_venda: number;
  unidade_medida: string;
  estoque_minimo?: number;
  empresa_id: number;
  quantidade_em_estoque: number;
  data_validade?: string; // ISO string
}

export default function DashboardPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState("");

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  // Abre modal para movimentar estoque
  const handleOpenModal = (product: Product) => {
    setSelectedProduct(product);
    setIsModalOpen(true);
  };

  // Fecha modal
  const handleCloseModal = () => {
    setSelectedProduct(null);
    setIsModalOpen(false);
  };

  // Função para movimentar estoque, compatível com o modal (tipo: 'entrada' | 'saida')
  const handleMovementSubmit = async (
    tipo: "entrada" | "saida",
    quantidade: number
  ) => {
    if (!selectedProduct) return;

    const token = localStorage.getItem("authToken");
    if (!token) {
      setError("Sessão expirada. Faça login novamente.");
      return;
    }

    const tipoMaiusculo = tipo.toUpperCase() as "ENTRADA" | "SAIDA";

    try {
      const response = await fetch("http://localhost:8000/movimentacoes/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          produto_id: selectedProduct.id,
          tipo_movimentacao: tipoMaiusculo,
          quantidade,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage =
          errorData.detail?.[0]?.msg || errorData.detail || "Erro ao registrar movimentação.";
        throw new Error(errorMessage);
      }

      const updatedProduct = await response.json();

      setProducts((currentProducts) =>
        currentProducts.map((p) => (p.id === updatedProduct.id ? updatedProduct : p))
      );

      alert("Movimentação registrada com sucesso!");
      handleCloseModal();
    } catch (err: any) {
      alert(`Erro: ${err.message}`);
    }
  };

  // Busca produtos no backend
  useEffect(() => {
    const fetchProducts = async () => {
      const token = localStorage.getItem("authToken");
      if (!token) {
        setError("Token não encontrado. Por favor, faça login novamente.");
        setLoading(false);
        return;
      }

      try {
        const response = await fetch("http://localhost:8000/produtos", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          if (response.status === 401) {
            throw new Error("Sua sessão expirou. Por favor, faça login novamente.");
          }
          throw new Error("Falha ao buscar os produtos.");
        }

        const data: Product[] = await response.json();
        setProducts(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  // Filtra produtos pelo termo de busca (nome ou código)
  const filteredProducts = products.filter((product) =>
    product.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.codigo.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <main className="min-h-screen bg-neutral-gray-50 p-8">
      <div className="max-w-6xl mx-auto bg-white rounded-3xl shadow-lg p-8">
        {/* Logo e título */}
        <div className="flex items-center justify-between mb-8">
          <Image
            src="/HIGIPLAS-LOGO-2048x761.png"
            alt="Logo Higiplas"
            width={180}
            height={60}
            priority
            className="drop-shadow-lg"
          />
          <h1 className="text-4xl font-extrabold text-higiplas-blue text-center flex-grow ml-8">
            Dashboard de Produtos
          </h1>
        </div>

        {/* Input de busca */}
        <input
          type="text"
          placeholder="Buscar por nome ou código"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="mb-6 w-full max-w-sm px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-higiplas-blue"
        />

        {loading && (
          <p className="text-center text-neutral-gray-600 text-lg font-medium">
            Carregando produtos...
          </p>
        )}

        {error && (
          <p className="text-center text-red-600 bg-red-100 p-4 rounded-md font-semibold mb-6">
            {error}
          </p>
        )}

        {!loading && !error && (
          <div className="overflow-x-auto rounded-lg border border-neutral-gray-200 shadow-sm">
            <table className="min-w-full divide-y divide-neutral-gray-200">
              <thead className="bg-neutral-gray-100">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-gray-600 uppercase tracking-wide">
                    Nome
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-gray-600 uppercase tracking-wide">
                    Código
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-gray-600 uppercase tracking-wide">
                    Categoria
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-gray-600 uppercase tracking-wide">
                    Descrição
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-gray-600 uppercase tracking-wide">
                    Preço Venda
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-gray-600 uppercase tracking-wide">
                    Unidade Medida
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-gray-600 uppercase tracking-wide">
                    Estoque Mínimo
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-gray-600 uppercase tracking-wide">
                    Quantidade em Estoque
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-gray-600 uppercase tracking-wide">
                    Data Validade
                  </th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-neutral-gray-600 uppercase tracking-wide">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-neutral-gray-200">
                {filteredProducts.map((product) => (
                  <tr key={product.id} className="hover:bg-neutral-gray-50 transition">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-neutral-gray-900">
                      {product.nome}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-gray-700">
                      {product.codigo}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-gray-700">
                      {product.categoria}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-gray-700">
                      {product.descricao || "-"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-gray-700">
                      {product.preco_venda.toLocaleString("pt-BR", {
                        style: "currency",
                        currency: "BRL",
                      })}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-gray-700">
                      {product.unidade_medida}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-gray-700">
                      {product.estoque_minimo ?? 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-gray-700">
                      {product.quantidade_em_estoque}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-gray-700">
                      {product.data_validade
                        ? new Date(product.data_validade).toLocaleDateString("pt-BR")
                        : "-"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleOpenModal(product)}
                        className="text-higiplas-blue hover:text-blue-800 font-semibold transition"
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