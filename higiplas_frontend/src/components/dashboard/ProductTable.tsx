// /src/components/dashboard/ProductTable.tsx
import { Product, ProdutoUpdateData } from "@/types";
import { CustomTable } from './CustomTable';
import Link from 'next/link';

const ProductActions = ({ product, onMoveStock, onRemove, onEditClick }: {
  product: Product;
  onMoveStock: (p: Product) => void;
  onRemove: (id: number) => void;
  onEditClick: (p: Product) => void; // Apenas a função para "abrir" a edição
}) => (
    <div className="flex justify-end items-center gap-2 md:gap-4 text-sm font-semibold">
        <Link href={`/dashboard/history/${product.id}`} className="text-gray-500 hover:text-gray-400">
          Histórico
        </Link>
        <button onClick={() => onEditClick(product)} className="text-indigo-600 hover:text-indigo-500">
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

interface ProductTableProps {
  products: Product[];
  onSave: (id: number, data: ProdutoUpdateData) => Promise<void>;
  onRemove: (id: number) => Promise<void>;
  onMoveStock: (product: Product) => void;
}

export function ProductTable({ products, onRemove, onMoveStock }: ProductTableProps) {

  // A função para o botão "Editar" por enquanto pode só dar um alerta.
  // Futuramente, ela abriria um Modal de Edição.
  const handleEditClick = (product: Product) => {
    alert(`Funcionalidade de editar "${product.nome}" a ser implementada.`);
  };

  const columns = [
    // ... suas colunas ...
    { header: 'Ações', accessor: 'actions' as const, render: (p: Product) => (
      <ProductActions product={p} onMoveStock={onMoveStock} onRemove={onRemove} onEditClick={handleEditClick} />
    )},
  ];

  const renderMobileCard = (product: Product) => (
    <div className="space-y-3">
        {/* ... seu card mobile ... */}
        <div className="pt-3 border-t dark:border-gray-700">
           <ProductActions product={product} onMoveStock={onMoveStock} onRemove={onRemove} onEditClick={handleEditClick} />
        </div>
    </div>
  );

  return <CustomTable<Product> columns={columns} data={products} renderMobileCard={renderMobileCard} />;
}