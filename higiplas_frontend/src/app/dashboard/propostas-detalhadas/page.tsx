// src/app/dashboard/propostas-detalhadas/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { usePropostaDetalhada } from '@/hooks/usePropostaDetalhada';
import { PropostaDetalhadaView } from '@/components/propostas/PropostaDetalhadaView';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { PropostaDetalhada } from '@/services/propostaService';
import { Eye, Trash2, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAdmin } from '@/hooks/useAdmin';

export default function PropostasDetalhadasPage() {
  const { isAdmin } = useAdmin();
  const { propostas, loading, getPropostas, getPropostaById, deleteProposta } = usePropostaDetalhada();
  const [propostaSelecionada, setPropostaSelecionada] = useState<PropostaDetalhada | null>(null);
  const [filtro, setFiltro] = useState<string>('');

  useEffect(() => {
    getPropostas(0, 100);
  }, [getPropostas]);

  const propostasFiltradas = propostas.filter((p) => {
    if (!filtro) return true;
    const filtroLower = filtro.toLowerCase();
    return (
      p.produto_nome?.toLowerCase().includes(filtroLower) ||
      p.cliente_nome?.toLowerCase().includes(filtroLower) ||
      p.vendedor_nome?.toLowerCase().includes(filtroLower)
    );
  });

  const handleVisualizar = async (propostaId: number) => {
    try {
      const proposta = await getPropostaById(propostaId);
      if (proposta) {
        setPropostaSelecionada(proposta);
      }
    } catch {
      toast.error('Erro ao carregar proposta');
    }
  };

  const handleDeletar = async (propostaId: number) => {
    if (!confirm('Tem certeza que deseja deletar esta proposta?')) {
      return;
    }

    try {
      await deleteProposta(propostaId);
      toast.success('Proposta deletada com sucesso');
    } catch {
      toast.error('Erro ao deletar proposta');
    }
  };

  if (propostaSelecionada) {
    return (
      <div className="space-y-4">
        <Button variant="outline" onClick={() => setPropostaSelecionada(null)}>
          ← Voltar para Lista
        </Button>
        <PropostaDetalhadaView proposta={propostaSelecionada} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Propostas Detalhadas</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Gerencie todas as propostas detalhadas do sistema
        </p>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Buscar por produto, cliente ou vendedor..."
                value={filtro}
                onChange={(e) => setFiltro(e.target.value)}
                className="w-full"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Propostas */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      ) : propostasFiltradas.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-gray-500 dark:text-gray-400">
              Nenhuma proposta encontrada
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {propostasFiltradas.map((proposta) => (
            <Card key={proposta.id}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-2">
                      <h3 className="font-semibold text-lg">#{proposta.id}</h3>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(proposta.data_criacao).toLocaleDateString('pt-BR')}
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Produto</p>
                        <p className="font-medium">{proposta.produto_nome || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Cliente</p>
                        <p className="font-medium">{proposta.cliente_nome || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Vendedor</p>
                        <p className="font-medium">{proposta.vendedor_nome || 'N/A'}</p>
                      </div>
                    </div>
                    {proposta.rendimento_total_litros && (
                      <div className="mt-4">
                        <p className="text-sm text-gray-600 dark:text-gray-400">Rendimento Total</p>
                        <p className="text-xl font-bold text-green-600">
                          {proposta.rendimento_total_litros.toFixed(2)} litros
                        </p>
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleVisualizar(proposta.id)}
                    >
                      <Eye className="h-4 w-4 mr-2" />
                      Ver
                    </Button>
                    {isAdmin && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeletar(proposta.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

