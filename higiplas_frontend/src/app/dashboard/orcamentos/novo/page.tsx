// /src/app/dashboard/orcamentos/novo/page.tsx
"use client";
import { useState } from 'react';
import { useProducts } from '@/hooks/useProducts'; // Reutilizaremos o hook de produtos
import { Product } from '@/types';

// ...

export default function NovoOrcamentoPage() {
    const { products, loading } = useProducts(); // Pega a lista de todos os produtos
    const [cliente, setCliente] = useState('');
    const [itensOrcamento, setItensOrcamento] = useState<any[]>([]);
    // ... (lógica para pesquisar produtos da lista `products`)
    // ... (lógica para adicionar um produto aos `itensOrcamento` com validação de estoque)
    // ... (lógica para `handleSubmit` que envia para a API)

    return (
        <div>
            <h1>Criar Novo Orçamento</h1>
            <form>
                <label>Nome do Cliente</label>
                <input value={cliente} onChange={e => setCliente(e.target.value)} />
                
                <hr />

                <h2>Adicionar Produtos</h2>
                {/* Aqui viria o campo de busca de produtos e a lista de itens adicionados */}
                {/* Para cada item adicionado, permitir definir a quantidade */}

                <button type="submit">Salvar Orçamento</button>
            </form>
        </div>
    )
}