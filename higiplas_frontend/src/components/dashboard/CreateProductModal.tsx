// /src/app/components/dashboard/CreateProductModal.tsx

import { useState, FormEvent, ChangeEvent } from "react";
import { ProdutoCreateData } from "@/types";
import Input from "@/components/Input"; // Importando do local correto
import Button from "@/components/Button"; // Importando do local correto

interface CreateProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (data: ProdutoCreateData) => Promise<void>;
}

export default function CreateProductModal({ isOpen, onClose, onCreate }: CreateProductModalProps) {
  const initialState: ProdutoCreateData = {
    nome: "", codigo: "", categoria: "", descricao: "", preco_custo: 0,
    preco_venda: 0, unidade_medida: "", estoque_minimo: 0, data_validade: "",
  };
  const [newProductData, setNewProductData] = useState<ProdutoCreateData>(initialState);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const isNumber = type === 'number';
    // @ts-ignore
    setNewProductData(prev => ({ ...prev, [name]: isNumber ? parseFloat(value) || 0 : value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await onCreate(newProductData);
    setNewProductData(initialState); // Reseta o formulário
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Adicionar Novo Produto</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input label="Nome do Produto" name="nome" required value={newProductData.nome} onChange={handleInputChange} />
            <Input label="Código Único" name="codigo" required value={newProductData.codigo} onChange={handleInputChange} />
            <Input label="Categoria" name="categoria" required value={newProductData.categoria} onChange={handleInputChange} />
            <Input label="Unidade de Medida" name="unidade_medida" required value={newProductData.unidade_medida} onChange={handleInputChange} placeholder="Ex: CX, UN, LT, KG"/>
            <Input label="Preço de Custo" name="preco_custo" type="number" step="0.01" value={newProductData.preco_custo || ''} onChange={handleInputChange} />
            <Input label="Preço de Venda" name="preco_venda" type="number" step="0.01" required value={newProductData.preco_venda ?? ''} onChange={handleInputChange} />
            <Input label="Estoque Mínimo" name="estoque_minimo" type="number" value={newProductData.estoque_minimo ?? ''} onChange={handleInputChange} />
            <Input label="Data de Validade" name="data_validade" type="date" value={newProductData.data_validade || ''} onChange={handleInputChange} />
          </div>
          <div className="col-span-2">
             <label className="block text-sm font-medium text-neutral-gray-700">Descrição</label>
             <textarea name="descricao" value={newProductData.descricao?? ''} onChange={handleInputChange} className="mt-1 block w-full border border-neutral-gray-300 rounded-md p-2 text-gray-900" rows={3} />
          </div>
          <div className="mt-8 flex justify-end space-x-4">
            <Button type="button" variant="secondary" onClick={onClose}>Cancelar</Button>
            <Button type="submit" variant="primary">Criar Produto</Button>
          </div>
        </form>
      </div>
    </div>
  );
}