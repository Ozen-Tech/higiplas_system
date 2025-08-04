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

  // --- CORREÇÃO AQUI ---
  // Defina todas as colunas que a tabela deve exibir.
  const columns = [
    { 
      header: 'Nome', 
      accessor: 'nome' as const,
      // Renderização especial para adicionar o estilo de fonte
      render: (p: Product) => <span className="font-medium text-gray-900 dark:text-gray-100">{p.nome}</span>
    },
    { 
      header: 'Código', 
      accessor: 'codigo' as const 
    },
    { 
      header: 'Estoque Mínimo', 
      accessor: 'estoque_minimo' as const,
      // Renderização para mostrar '0' caso o valor seja nulo
      render: (p: Product) => <span>{p.estoque_minimo ?? 0}</span>
    },
    { 
      header: 'Qtde em Estoque', 
      accessor: 'quantidade_em_estoque' as const,
      render: (p: Product) => <span className="font-bold">{p.quantidade_em_estoque}</span>
    },
    { 
      header: 'Data de Validade', 
      accessor: 'data_validade' as const,
      // Renderização para formatar a data para o padrão brasileiro
      render: (p: Product) => (
        <span>
          {p.data_validade ? new Date(p.data_validade + 'T00:00:00').toLocaleDateString("pt-BR") : "-"}
        </span>
      )
    },
    { 
      header: 'Ações', 
      accessor: 'actions' as const, 
      render: (p: Product) => (
        <ProductActions product={p} onMoveStock={onMoveStock} onRemove={onRemove} onEditClick={handleEditClick} />
      )
    },
  ];

  const renderMobileCard = (product: Product) => (
    <div className="space-y-3">
        <div className="flex justify-between items-center">
            <span className="font-bold text-lg dark:text-gray-100">{product.nome}</span>
            <span className="text-sm text-gray-500 dark:text-gray-400">{product.codigo}</span>
        </div>
        <div>
            <p>Estoque: <span className="font-semibold">{product.quantidade_em_estoque}</span> (Mín: {product.estoque_minimo ?? 0})</p>
            <p>Validade: {product.data_validade ? new Date(product.data_validade + 'T00:00:00').toLocaleDateString("pt-BR") : "-"}</p>
        </div>
        <div className="pt-3 border-t dark:border-gray-700">
           <ProductActions product={product} onMoveStock={onMoveStock} onRemove={onRemove} onEditClick={handleEditClick} />
        </div>
    </div>
  );

  return <CustomTable<Product> columns={columns} data={products} renderMobileCard={renderMobileCard} />;
}