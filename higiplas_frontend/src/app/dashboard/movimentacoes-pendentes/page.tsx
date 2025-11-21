'use client';

import { useState } from 'react';
import { Header } from '@/components/dashboard/Header';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2 } from 'lucide-react';
import { useMovimentacoesPendentesAdmin } from '@/hooks/useMovimentacoesPendentesAdmin';
import { MovimentacaoPendente } from '@/types';
import { MovimentacoesPendentesTable } from '@/components/admin/MovimentacoesPendentesTable';
import { ConfirmarMovimentacaoModal } from '@/components/admin/ConfirmarMovimentacaoModal';
import { EditarMovimentacaoModal } from '@/components/admin/EditarMovimentacaoModal';
import { RejeitarMovimentacaoModal } from '@/components/admin/RejeitarMovimentacaoModal';

export default function MovimentacoesPendentesPage() {
  const [statusFilter, setStatusFilter] = useState<string>('PENDENTE');
  const [selectedMovimentacao, setSelectedMovimentacao] = useState<MovimentacaoPendente | null>(null);
  const [modalType, setModalType] = useState<'confirmar' | 'editar' | 'rejeitar' | null>(null);

  const { movimentacoes, loading, carregarMovimentacoes } = useMovimentacoesPendentesAdmin(statusFilter);

  const handleConfirmar = (movimentacao: MovimentacaoPendente) => {
    setSelectedMovimentacao(movimentacao);
    setModalType('confirmar');
  };

  const handleEditar = (movimentacao: MovimentacaoPendente) => {
    setSelectedMovimentacao(movimentacao);
    setModalType('editar');
  };

  const handleRejeitar = (movimentacao: MovimentacaoPendente) => {
    setSelectedMovimentacao(movimentacao);
    setModalType('rejeitar');
  };

  const handleCloseModal = () => {
    setSelectedMovimentacao(null);
    setModalType(null);
    carregarMovimentacoes();
  };

  const pendentes = movimentacoes.filter(m => m.status === 'PENDENTE').length;

  return (
    <>
      <Header>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 w-full">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Solicitações de Movimentação
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Aprove, edite ou rejeite movimentações de estoque solicitadas pelos entregadores
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="PENDENTE">Pendentes ({pendentes})</SelectItem>
                <SelectItem value="CONFIRMADO">Confirmadas</SelectItem>
                <SelectItem value="REJEITADO">Rejeitadas</SelectItem>
                <SelectItem value="">Todas</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </Header>

      <Card className="mt-6">
        <CardContent className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : (
            <MovimentacoesPendentesTable
              movimentacoes={movimentacoes}
              onConfirmar={handleConfirmar}
              onEditar={handleEditar}
              onRejeitar={handleRejeitar}
            />
          )}
        </CardContent>
      </Card>

      {selectedMovimentacao && modalType === 'confirmar' && (
        <ConfirmarMovimentacaoModal
          movimentacao={selectedMovimentacao}
          onClose={handleCloseModal}
        />
      )}

      {selectedMovimentacao && modalType === 'editar' && (
        <EditarMovimentacaoModal
          movimentacao={selectedMovimentacao}
          onClose={handleCloseModal}
        />
      )}

      {selectedMovimentacao && modalType === 'rejeitar' && (
        <RejeitarMovimentacaoModal
          movimentacao={selectedMovimentacao}
          onClose={handleCloseModal}
        />
      )}
    </>
  );
}

