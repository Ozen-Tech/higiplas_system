// /src/app/components/dashboard/CreateProductModal.tsx

import { useState, FormEvent, ChangeEvent } from "react";
import { ProdutoCreateData } from "@/types";
import Input from "@/components/Input";
import Button from "@/components/Button";

interface CreateProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  // Alteração na tipagem para corresponder ao que vamos enviar
  onCreate: (data: Omit<ProdutoCreateData, 'data_validade'> & { data_validade: string | null }) => Promise<void>;
}

export default function CreateProductModal({ isOpen, onClose, onCreate }: CreateProductModalProps) {
  // --- CORREÇÃO 1: Definir data_validade como string vazia no estado inicial ---
  const initialState = {
    nome: "", 
    codigo: "", 
    categoria: "", 
    descricao: "", 
    preco_custo: undefined, // Usar undefined para números opcionais
    preco_venda: undefined, // Usar undefined para números opcionais
    unidade_medida: "", 
    estoque_minimo: undefined, // Usar undefined para números opcionais
    data_validade: "", // O input de data funciona melhor com string vazia
  };

  const [newProductData, setNewProductData] = useState(initialState);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setNewProductData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // --- CORREÇÃO 2: Preparar os dados para envio ---
    // Cria um novo objeto para não modificar o estado diretamente
    const dataToSend = {
      ...newProductData,
      // Converte campos numéricos de string para number
      preco_custo: newProductData.preco_custo ? parseFloat(String(newProductData.preco_custo)) : null,
      preco_venda: newProductData.preco_venda ? parseFloat(String(newProductData.preco_venda)) : 0, // Preço de venda é obrigatório
      estoque_minimo: newProductData.estoque_minimo ? parseInt(String(newProductData.estoque_minimo), 10) : 0,
      
      // A MÁGICA: Se data_validade for uma string vazia, envia null.
      // Senão, envia a própria string da data.
      data_validade: newProductData.data_validade || null,
      creationDate: new Date().toISOString(),
    };
    
    // Validação extra para garantir que campos obrigatórios não estão vazios
    if (!dataToSend.nome || !dataToSend.codigo || !dataToSend.categoria || !dataToSend.unidade_medida || !dataToSend.preco_venda) {
        alert("Por favor, preencha todos os campos obrigatórios.");
        return;
    }

    await onCreate(dataToSend);
    setNewProductData(initialState); // Reseta o formulário
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-100">Adicionar Novo Produto</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input label="Nome do Produto" name="nome" required value={newProductData.nome} onChange={handleInputChange} />
            <Input label="Código Único" name="codigo" required value={newProductData.codigo} onChange={handleInputChange} />
            <Input label="Categoria" name="categoria" required value={newProductData.categoria} onChange={handleInputChange} />
            <Input label="Unidade de Medida" name="unidade_medida" required value={newProductData.unidade_medida} onChange={handleInputChange} placeholder="Ex: CX, UN, LT, KG"/>
            <Input label="Preço de Custo" name="preco_custo" type="number" step="0.01" value={newProductData.preco_custo || ''} onChange={handleInputChange} />
            <Input label="Preço de Venda" name="preco_venda" type="number" step="0.01" required value={newProductData.preco_venda || ''} onChange={handleInputChange} />
            <Input label="Estoque Mínimo" name="estoque_minimo" type="number" value={newProductData.estoque_minimo || ''} onChange={handleInputChange} />
            <Input label="Data de Validade" name="data_validade" type="date" value={newProductData.data_validade || ''} onChange={handleInputChange} />
          </div>
          <div className="col-span-2">
             <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Descrição</label>
             <textarea 
               name="descricao" 
               value={newProductData.descricao ?? ''} 
               onChange={handleInputChange} 
               className="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md p-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-higiplas-blue focus:border-higiplas-blue" 
               rows={3} 
             />
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