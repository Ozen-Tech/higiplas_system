"use client";
import { useState } from "react";

interface ProdutoCardProps {
  id: number;
  nome: string;
  estoque_atual: number;
  preco_venda: number;
  onQuantidadeChange: (id: number, quantidade: number) => void;
}

export default function ProdutoCard({ id, nome, estoque_atual, preco_venda, onQuantidadeChange }: ProdutoCardProps) {
  const [quantidade, setQuantidade] = useState(0);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value) || 0;
    if (value > estoque_atual) return;
    setQuantidade(value);
    onQuantidadeChange(id, value);
  };

  return (
    <div className="border p-4 rounded-md shadow mb-3">
      <h3 className="font-bold">{nome}</h3>
      <p>Estoque: {estoque_atual}</p>
      <p>Preço: R$ {preco_venda.toFixed(2)}</p>
      <input
        type="number"
        min={0}
        max={estoque_atual}
        value={quantidade}
        onChange={handleChange}
        className="border rounded p-1 mt-2 w-20"
      />
    </div>
  );
}
