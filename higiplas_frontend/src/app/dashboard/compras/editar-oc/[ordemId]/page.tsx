"use client";

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { apiService } from '@/services/apiService';
import { Product } from '@/types';
import { Header } from '@/components/dashboard/Header';
import Button from '@/components/Button';
import Input from '@/components/Input';
import toast from 'react-hot-toast';
import { Loader2 } from 'lucide-react';

interface Fornecedor { id: number; nome: string; }
interface OrderItem extends Product {
    quantidade_solicitada: number;
    custo_unitario_registrado: number;
}

export default function EditarOrdemDeCompraPage() {
    const params = useParams();
    const router = useRouter();
    const ordemId = parseInt(params.ordemId as string, 10);
    
    const [items, setItems] = useState<OrderItem[]>([]);
    const [fornecedores, setFornecedores] = useState<Fornecedor[]>([]);
    const [selectedFornecedorId, setSelectedFornecedorId] = useState<string>('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [ordemData, fornecedoresData] = await Promise.all([
                    apiService.get(`/ordens-compra/${ordemId}`),
                    apiService.get('/fornecedores/').catch(() => ({ data: [] }))
                ]);

                const ordem = ordemData?.data;
                
                if (!ordem) {
                    toast.error('Ordem de compra não encontrada');
                    router.push('/dashboard/compras');
                    return;
                }

                // Verificar se pode editar
                if (ordem.status === 'RECEBIDA') {
                    toast.error('Não é possível editar uma ordem de compra já recebida');
                    router.push('/dashboard/compras');
                    return;
                }

                // Carregar itens da ordem
                const ordemItems: OrderItem[] = ordem.itens?.map((item: any) => ({
                    ...item.produto,
                    quantidade_solicitada: item.quantidade_solicitada,
                    custo_unitario_registrado: item.custo_unitario_registrado,
                })) || [];

                setItems(ordemItems);
                setSelectedFornecedorId(ordem.fornecedor_id?.toString() || '');
                setFornecedores(fornecedoresData?.data || []);
            } catch (error) {
                console.error("Erro ao carregar dados da OC", error);
                toast.error("Falha ao carregar dados. Tente novamente.");
                router.push('/dashboard/compras');
            } finally {
                setLoading(false);
            }
        };

        if (ordemId) {
            fetchData();
        }
    }, [ordemId, router]);

    const handleItemChange = (id: number, field: keyof OrderItem, value: string | number) => {
        setItems(currentItems =>
            currentItems.map(item =>
                item.id === id ? { ...item, [field]: value } : item
            )
        );
    };

    const handleRemoveItem = (id: number) => {
        setItems(currentItems => currentItems.filter(item => item.id !== id));
    };

    const handleAddProduct = async () => {
        // Buscar produtos para adicionar
        try {
            const produtosData = await apiService.get('/produtos/');
            const produtos = produtosData?.data || [];
            
            // Mostrar um prompt simples ou criar um modal mais elaborado
            const produtoId = prompt('Digite o ID do produto para adicionar:');
            if (!produtoId) return;

            const produto = produtos.find((p: Product) => p.id === parseInt(produtoId, 10));
            if (!produto) {
                toast.error('Produto não encontrado');
                return;
            }

            // Verificar se já existe
            if (items.find(item => item.id === produto.id)) {
                toast.error('Produto já está na lista');
                return;
            }

            setItems([...items, {
                ...produto,
                quantidade_solicitada: produto.estoque_minimo || 10,
                custo_unitario_registrado: produto.preco_custo || 0,
            }]);
        } catch (error) {
            toast.error('Erro ao buscar produtos');
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (items.length === 0) {
            toast.error("Adicione pelo menos um item à ordem de compra.");
            return;
        }

        const payload = {
            fornecedor_id: selectedFornecedorId ? parseInt(selectedFornecedorId, 10) : null,
            itens: items.map(item => ({
                produto_id: item.id,
                quantidade_solicitada: Number(item.quantidade_solicitada),
                custo_unitario_registrado: Number(item.custo_unitario_registrado)
            }))
        };
        
        const promise = apiService.put(`/ordens-compra/${ordemId}`, payload);

        toast.promise(promise, {
            loading: 'Atualizando Ordem de Compra...',
            success: () => {
                router.push('/dashboard/compras');
                return 'Ordem de Compra atualizada com sucesso!';
            },
            error: (err) => `Erro ao atualizar OC: ${err.message}`,
        });
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
        );
    }

    return (
        <>
            <Header><h1 className="text-xl font-bold">Editar Ordem de Compra #{ordemId}</h1></Header>
            <main className="flex-1 p-6">
                <form onSubmit={handleSubmit} className="max-w-4xl mx-auto bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
                    <div className="mb-6">
                        <label htmlFor="fornecedor" className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                            Fornecedor <span className="text-gray-500 text-xs">(Opcional)</span>
                        </label>
                        <select
                            id="fornecedor"
                            value={selectedFornecedorId}
                            onChange={e => setSelectedFornecedorId(e.target.value)}
                            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                        >
                            <option value="">Nenhum fornecedor</option>
                            {fornecedores.map(f => <option key={f.id} value={f.id}>{f.nome}</option>)}
                        </select>
                    </div>

                    <div className="mb-4">
                        <Button type="button" variant="secondary" onClick={handleAddProduct}>
                            + Adicionar Produto
                        </Button>
                    </div>

                    <div className="space-y-4">
                        {items.map(item => (
                            <div key={item.id} className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center border-b pb-4 dark:border-gray-700">
                                <span className="font-medium col-span-1 md:col-span-2">{item.nome}</span>
                                <Input 
                                    label="Quantidade" 
                                    type="number" 
                                    value={item.quantidade_solicitada} 
                                    onChange={e => handleItemChange(item.id, 'quantidade_solicitada', parseInt(e.target.value) || 0)} 
                                />
                                <Input 
                                    label="Custo Unitário (R$)" 
                                    type="number" 
                                    step="0.01" 
                                    value={item.custo_unitario_registrado} 
                                    onChange={e => handleItemChange(item.id, 'custo_unitario_registrado', parseFloat(e.target.value) || 0)} 
                                />
                                <button
                                    type="button"
                                    onClick={() => handleRemoveItem(item.id)}
                                    className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 p-2"
                                    title="Remover item"
                                >
                                    ✕
                                </button>
                            </div>
                        ))}
                    </div>

                    {items.length === 0 && (
                        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                            <p>Nenhum item adicionado. Clique em "Adicionar Produto" para começar.</p>
                        </div>
                    )}

                    <div className="mt-8 flex justify-end gap-4">
                        <Button type="button" variant="secondary" onClick={() => router.back()}>Cancelar</Button>
                        <Button type="submit">Salvar Alterações</Button>
                    </div>
                </form>
            </main>
        </>
    );
}

