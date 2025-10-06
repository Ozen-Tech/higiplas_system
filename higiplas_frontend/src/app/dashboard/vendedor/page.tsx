"use client";
import { useEffect, useState } from "react";
import ProdutoCard from "./ProdutoCard";

interface Produto {
  id: number;
  nome: string;
  estoque_atual: number;
  preco_venda: number;
}

export default function VendedorPage() {
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [quantidades, setQuantidades] = useState<{ [key: number]: number }>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("/api/vendas-simples") // Ajuste se sua rota for diferente
      .then(res => res.json())
      .then(data => setProdutos(data))
      .catch(err => console.error(err));
  }, []);

  const handleQuantidadeChange = (id: number, quantidade: number) => {
    setQuantidades(prev => ({ ...prev, [id]: quantidade }));
  };

  const handleSubmit = async () => {
    const itens = Object.entries(quantidades)
      .filter(([_, qtd]) => qtd > 0)
      .map(([produto_id, quantidade]) => ({ produto_id: Number(produto_id), quantidade }));

    if (itens.length === 0) {
      alert("Selecione pelo menos um produto para vender.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/api/vendas-simples", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ itens })
      });
      const data = await res.json();
      alert(data.mensagem);
      // Atualizar estoque local
      setProdutos(prev => prev.map(p => {
        const item = itens.find(i => i.produto_id === p.id);
        if (item) return { ...p, estoque_atual: p.estoque_atual - item.quantidade };
        return p;
      }));
      setQuantidades({});
    } catch (err) {
      console.error(err);
      alert("Erro ao registrar venda.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Vendas Simples</h1>
      {produtos.map(produto => (
        <ProdutoCard
          key={produto.id}
          {...produto}
          onQuantidadeChange={handleQuantidadeChange}
        />
      ))}
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="bg-blue-500 text-white px-4 py-2 rounded mt-4"
      >
        {loading ? "Registrando..." : "Finalizar Venda"}
      </button>
    </div>
  );
}
