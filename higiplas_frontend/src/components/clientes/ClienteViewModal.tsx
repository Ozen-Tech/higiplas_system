'use client';

import { ClienteV2 } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ClienteKPIsComponent } from './ClienteKPIs';
import { X } from 'lucide-react';

interface ClienteViewModalProps {
  cliente: ClienteV2;
  open: boolean;
  onClose: () => void;
}

export function ClienteViewModal({
  cliente,
  open,
  onClose,
}: ClienteViewModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-800" onClick={(e) => e.stopPropagation()}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl">Detalhes do Cliente #{cliente.id}</CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X size={20} />
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Nome/Razão Social</label>
              <p className="text-lg font-semibold mt-1">{cliente.nome}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Telefone</label>
              <p className="mt-1">{cliente.telefone || 'N/A'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Status</label>
              <div className="mt-1">
                <Badge variant={cliente.status === 'ATIVO' ? 'default' : 'secondary'}>
                  {cliente.status}
                </Badge>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Tipo de Pessoa</label>
              <p className="mt-1">{cliente.tipo_pessoa === 'FISICA' ? 'Pessoa Física' : 'Pessoa Jurídica'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">CPF/CNPJ</label>
              <p className="mt-1">{cliente.cpf_cnpj || 'N/A'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Bairro</label>
              <p className="mt-1">{cliente.bairro || 'N/A'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Cidade</label>
              <p className="mt-1">{cliente.cidade || 'N/A'}</p>
            </div>
            {cliente.referencia_localizacao && (
              <div className="md:col-span-2">
                <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Referência de Localização</label>
                <p className="mt-1">{cliente.referencia_localizacao}</p>
              </div>
            )}
            {cliente.observacoes && (
              <div className="md:col-span-2">
                <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Observações</label>
                <p className="mt-1 whitespace-pre-wrap">{cliente.observacoes}</p>
              </div>
            )}
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Vendedor</label>
              <p className="mt-1">{cliente.vendedor_nome || `ID: ${cliente.vendedor_id}`}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Data de Criação</label>
              <p className="mt-1">{new Date(cliente.criado_em).toLocaleDateString('pt-BR')}</p>
            </div>
            {cliente.atualizado_em && (
              <div>
                <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Última Atualização</label>
                <p className="mt-1">{new Date(cliente.atualizado_em).toLocaleDateString('pt-BR')}</p>
              </div>
            )}
            {cliente.total_vendas !== undefined && (
              <div>
                <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Total de Vendas</label>
                <p className="mt-1 font-semibold text-green-600">R$ {cliente.total_vendas.toFixed(2)}</p>
              </div>
            )}
            {cliente.ultima_venda && (
              <div>
                <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Última Venda</label>
                <p className="mt-1">{new Date(cliente.ultima_venda).toLocaleDateString('pt-BR')}</p>
              </div>
            )}
          </div>

          <ClienteKPIsComponent clienteId={cliente.id} />

          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="outline" onClick={onClose}>
              Fechar
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

