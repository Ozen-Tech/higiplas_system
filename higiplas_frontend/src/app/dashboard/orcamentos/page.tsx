// /src/app/dashboard/orcamentos/page.tsx
"use client";
import Link from 'next/link';
// ...
export default function OrcamentosPage() {
    return (
        <div>
            <h1>Meus Orçamentos</h1>
            <Link href="/dashboard/orcamentos/novo">Criar Novo Orçamento</Link>
            {/* Aqui virá a tabela com os orçamentos */}
        </div>
    );
}