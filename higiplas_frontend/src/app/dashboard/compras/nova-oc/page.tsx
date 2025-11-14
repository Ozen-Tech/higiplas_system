"use client";

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { apiService } from '@/services/apiService';
import { Product } from '@/types';
import { Header } from '@/components/dashboard/Header';
import Button from '@/components/Button';
import Input from '@/components/Input';
import toast from 'react-hot-toast';

interface Fornecedor { id: number; nome: string; }
interface OrderItem extends Product {
    quantidade_solicitada: number;
    custo_unitario_registrado: number;
}

export default function NovaOrdemDeCompraPage() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const [items, setItems] = useState<OrderItem[]>([]);
    const [fornecedores, setFornecedores] = useState<Fornecedor[]>([]);
    const [selectedFornecedorId, setSelectedFornecedorId] = useState<string>('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const productIds = searchParams.get('productIds')?.split(',') || [];
        if (productIds.length === 0) {
            router.replace('/dashboard/compras');
            return;
        }

        const fetchInitialData = async () => {
            try {
                const [productsData, fornecedoresData] = await Promise.all([
                    Promise.all(productIds.map(id => apiService.get(`/produtos/${id}`))),
                    apiService.get('/fornecedores/').catch(() => ({ data: [] })) // Não falhar se não houver fornecedores
                ]);

                const initialItems: OrderItem[] = productsData.map(response => ({
                    ...response?.data,
                    quantidade_solicitada: response?.data?.estoque_minimo || 10, // Sugestão inicial
                    custo_unitario_registrado: response?.data?.preco_custo || 0,
                }));

                setItems(initialItems);
                const fornecedores = fornecedoresData?.data || [];
                setFornecedores(fornecedores);
                // Não selecionar fornecedor por padrão - deixar opcional
            } catch (error) {
                console.error("Erro ao carregar dados da OC", error);
                toast.error("Falha ao carregar dados. Tente novamente.");
            } finally {
                setLoading(false);
            }
        };

        fetchInitialData();
    }, [searchParams, router]);

    const handleItemChange = (id: number, field: keyof OrderItem, value: string | number) => {
        setItems(currentItems =>
            currentItems.map(item =>
                item.id === id ? { ...item, [field]: value } : item
            )
        );
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
        
        const promise = apiService.post('/ordens-compra/', payload);

        toast.promise(promise, {
            loading: 'Salvando Ordem de Compra...',
            success: () => {
                router.push('/dashboard/compras');
                return 'Ordem de Compra criada com sucesso!';
            },
            error: (err) => `Erro ao criar OC: ${err.message}`,
        });
    };

    if (loading) return <div>Carregando...</div>;

    return (
        <>
            <Header><h1 className="text-xl font-bold">Nova Ordem de Compra</h1></Header>
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

                    <div className="space-y-4">
                        {items.map(item => (
                            <div key={item.id} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center border-b pb-4 dark:border-gray-700">
                                <span className="font-medium col-span-1 md:col-span-2">{item.nome}</span>
                                <Input label="Quantidade" type="number" value={item.quantidade_solicitada} onChange={e => handleItemChange(item.id, 'quantidade_solicitada', e.target.value)} />
                                <Input label="Custo Unitário (R$)" type="number" step="0.01" value={item.custo_unitario_registrado} onChange={e => handleItemChange(item.id, 'custo_unitario_registrado', e.target.value)} />
                            </div>
                        ))}
                    </div>

                    <div className="mt-8 flex justify-end gap-4">
                        <Button type="button" variant="secondary" onClick={() => router.back()}>Cancelar</Button>
                        <Button type="submit">Salvar Ordem de Compra</Button>
                    </div>
                </form>
            </main>
        </>
    );
}