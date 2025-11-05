// /src/app/vendedor-app/page.tsx
// Página principal do app de vendedor

'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { PlusCircle, FileText, LogOut, User } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useVendedorOrcamentos } from '@/hooks/useVendedorOrcamentos';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function VendedorAppPage() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const { orcamentos, loading, listarOrcamentos } = useVendedorOrcamentos();

  useEffect(() => {
    listarOrcamentos();
  }, [listarOrcamentos]);

  const handleLogout = () => {
    if (confirm("Tem certeza que deseja sair?")) {
      logout();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header simples */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
                {user?.nome.charAt(0).toUpperCase()}
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">App de Vendedor</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">{user?.nome}</p>
              </div>
            </div>
            <Button variant="ghost" onClick={handleLogout} className="gap-2">
              <LogOut size={16} />
              Sair
            </Button>
          </div>
        </div>
      </header>

      {/* Conteúdo principal */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Card: Novo Orçamento */}
          <Link href="/vendedor-app/novo-orcamento">
            <Card className="h-full cursor-pointer hover:shadow-lg transition-shadow bg-gradient-to-br from-blue-500 to-indigo-600 text-white border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-2xl">
                  <PlusCircle size={28} />
                  Novo Orçamento
                </CardTitle>
                <CardDescription className="text-blue-100">
                  Crie um novo orçamento para seu cliente
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-blue-50 text-sm">
                  Selecione produtos, defina preços e gere o PDF profissional automaticamente.
                </p>
              </CardContent>
            </Card>
          </Link>

          {/* Card: Histórico */}
          <Link href="/vendedor-app/historico">
            <Card className="h-full cursor-pointer hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-2xl">
                  <FileText size={28} />
                  Histórico de Orçamentos
                </CardTitle>
                <CardDescription>
                  Visualize e gerencie seus orçamentos
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <span className="text-3xl font-bold text-blue-600">
                    {loading ? '...' : orcamentos.length}
                  </span>
                  <span className="text-gray-500">orçamentos criados</span>
                </div>
              </CardContent>
            </Card>
          </Link>
        </div>

        {/* Estatísticas rápidas */}
        {!loading && orcamentos.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Últimos Orçamentos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {orcamentos.slice(0, 5).map((orcamento) => (
                  <div
                    key={orcamento.id}
                    className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div>
                      <p className="font-semibold">#{orcamento.id}</p>
                      <p className="text-sm text-gray-500">
                        {orcamento.cliente?.razao_social || 'Cliente sem nome'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">
                        {new Date(orcamento.data_criacao).toLocaleDateString('pt-BR')}
                      </p>
                      <p className="font-semibold text-blue-600">
                        {orcamento.itens?.reduce((acc, item) => 
                          acc + (item.quantidade * item.preco_unitario_congelado), 0
                        ).toFixed(2) || '0.00'} R$
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}

