// /src/components/dashboard/ProductTable.tsx

import { Product, ProdutoUpdateData } from "@/types";
import { useState } from "react";
import Link from 'next/link';
import { CustomTable } from './CustomTable'; // Importa nosso novo componente responsivo

// Um novo micro-componente para as ações, para evitar repetição
const ProductActions = ({ product, onMoveStock, onRemove, onEdit }: {
  product: Product;
  onMoveStock: (p: Product) => void;
  onRemove: (id: number) => void;
  onEdit: (p: Product) => void; // A lógica de edição será gerenciada aqui
}) => (
    <div className="flex justify-end items-center gap-2 md:gap-4 text-sm font-semibold">
        <Link href={`/dashboard/history/${product.id}`} className="text-gray-500 hover:text-gray-400">
          Histórico
        </Link>
        <button onClick={() => onEdit(product)} className="text-indigo-600 hover:text-indigo-500">
            Editar
        </button>
        <button onClick={() => onMoveStock(product)} className="text-blue-600 hover:text-blue-500">
            Movimentar
        </button>
        <button onClick={() => onRemove(product.id)} className="text-red-600 hover:text-red-500">
            Remover
        </button>
    </div>
);


// Interface das Props, igual à de antes
interface ProductTableProps {
  products: Product[];
  onSave: (id: number, data: ProdutoUpdateData) => Promise<void>;
  onRemove: (id: number) => Promise<void>;
  onMoveStock: (product: Product) => void;
}

export function ProductTable({ products, onSave, onRemove, onMoveStock }: ProductTableProps) {
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  // Lógica de edição que será usada pelos componentes filhos
  // Esta parte poderia ser extraída para o `ProductTableRow` se preferir
  const handleEdit = (product: Product) => {
    setEditingProduct(product);
  };
  
  const handleSaveEdit = (id: number, data: ProdutoUpdateData) => {
    onSave(id, data).then(() => setEditingProduct(null));
  }

  // Define as colunas para a tabela de desktop
  const columns = [
    { header: 'Nome', accessor: 'nome', render: (p: Product) => (
        <div>
          <span className="font-medium text-gray-900 dark:text-gray-100">{p.nome}</span>
          <div className="text-xs text-gray-500">{p.codigo}</div>
        </div>
    )},
    { header: 'Estoque Mín.', accessor: 'estoque_minimo', render: (p: Product) => <div className="text-center">{p.estoque_minimo ?? 0}</div> },
    { header: 'Qtde Estoque', accessor: 'quantidade_em_estoque', render: (p: Product) => <div className="text-center font-bold">{p.quantidade_em_estoque}</div>},
    { header: 'Validade', accessor: 'data_validade', render: (p: Product) => p.data_validade ? new Date(p.data_validade + 'T00:00:00').toLocaleDateString("pt-BR") : "-"},
    { header: 'Ações', accessor: 'actions', render: (p: Product) => (
      <ProductActions product={p} onMoveStock={onMoveStock} onRemove={onRemove} onEdit={handleEdit} />
    )},
  ];

  // Define como cada produto será renderizado no formato de card em telas pequenas
  const renderMobileCard = (product: Product) => (
    <div className="space-y-3">
        <div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">{product.nome}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">Código: {product.codigo}</p>
        </div>
        <div className="flex justify-between border-t dark:border-gray-700 pt-2 text-sm">
            <span className="text-gray-500">Estoque Mínimo:</span>
            <span className="font-medium">{product.estoque_minimo ?? 0}</span>
        </div>
        <div className="flex justify-between text-sm">
            <span className="text-gray-500">Estoque Atual:</span>
            <span className={`font-bold text-lg ${product.quantidade_em_estoque <= (product.estoque_minimo ?? 0) ? 'text-yellow-500' : 'text-gray-800 dark:text-gray-200'}`}>{product.quantidade_em_estoque}</span>
        </div>
        <div className="flex justify-between text-sm">
            <span className="text-gray-500">Validade:</span>
            <span className="font-medium">{product.data_validade ? new Date(product.data_validade + 'T00:00:00').toLocaleDateString("pt-BR") : "-"}</span>
        </div>
        {/* Renderiza o componente de ações também para mobile */}
        <div className="pt-3 border-t dark:border-gray-700">
           <ProductActions product={product} onMoveStock={onMoveStock} onRemove={onRemove} onEdit={handleEdit} />
        </div>
    </div>
  );

  return <CustomTable columns={columns} data={products} renderMobileCard={renderMobileCard} />;
}