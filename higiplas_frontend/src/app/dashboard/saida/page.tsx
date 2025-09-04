'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Page() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/dashboard/movimentacoes?tipo=SAIDA');
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p>Redirecionando para Movimentações (Saída)...</p>
    </div>
  );
}