// /src/components/vendedor/ClientQuickSearch.tsx
// Busca rápida de clientes com modal de criação

'use client';

import { useState, useEffect } from 'react';
import { Search, UserPlus, User, Phone, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ClienteV2 } from '@/types';

// Tipo simplificado para busca de clientes
interface ClienteListItem {
  id: number;
  nome: string;
  telefone: string;
  bairro?: string;
  cidade?: string;
  cpf_cnpj?: string;
}

interface ClientQuickSearchProps {
  clientes: ClienteListItem[] | ClienteV2[];
  onSelectClient: (client: ClienteListItem | ClienteV2) => void;
  onCreateClient: (nome: string, telefone: string) => Promise<ClienteV2 | null>;
  loading?: boolean;
}

export function ClientQuickSearch({
  clientes,
  onSelectClient,
  onCreateClient,
  loading = false,
}: ClientQuickSearchProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredClients, setFilteredClients] = useState<(ClienteListItem | ClienteV2)[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newClientName, setNewClientName] = useState('');
  const [newClientPhone, setNewClientPhone] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredClients([]);
      return;
    }

    const term = searchTerm.toLowerCase();
    const filtered = clientes.filter(
      (c) =>
        c.nome.toLowerCase().includes(term) ||
        c.telefone.includes(term) ||
        (c.cpf_cnpj && c.cpf_cnpj.includes(term))
    ).slice(0, 10);

    setFilteredClients(filtered);
  }, [searchTerm, clientes]);

  const handleSelectClient = (client: ClienteListItem | ClienteV2) => {
    onSelectClient(client);
    setSearchTerm('');
    setFilteredClients([]);
  };

  const handleCreateClient = async () => {
    if (!newClientName.trim() || !newClientPhone.trim()) {
      return;
    }

    setCreating(true);
    const novoCliente = await onCreateClient(newClientName, newClientPhone);
    if (novoCliente) {
      handleSelectClient(novoCliente);
      setShowCreateModal(false);
      setNewClientName('');
      setNewClientPhone('');
    }
    setCreating(false);
  };

  return (
    <div className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
        <Input
          type="text"
          placeholder="Buscar cliente por nome, telefone ou CPF/CNPJ..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10 pr-4"
          disabled={loading}
        />
      </div>

      {/* Botão de criar cliente rápido */}
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => setShowCreateModal(true)}
        className="mt-2 w-full gap-2"
      >
        <UserPlus size={16} />
        Criar Cliente Rápido
      </Button>

      {/* Resultados da busca */}
      {searchTerm && filteredClients.length > 0 && (
        <Card className="absolute z-50 w-full mt-2 max-h-96 overflow-y-auto shadow-lg">
          <CardContent className="p-2">
            <div className="space-y-1">
              {filteredClients.map((client) => (
                <button
                  key={client.id}
                  onClick={() => handleSelectClient(client)}
                  className="w-full text-left p-3 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors flex items-center gap-3 group"
                >
                  <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center flex-shrink-0">
                    <User size={18} className="text-blue-600 dark:text-blue-300" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm truncate">{client.nome}</p>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      {client.telefone && (
                        <span className="flex items-center gap-1">
                          <Phone size={12} />
                          {client.telefone}
                        </span>
                      )}
                      {client.cidade && <span>{client.cidade}</span>}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Modal de criação rápida */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <UserPlus size={20} />
                  Criar Cliente Rápido
                </CardTitle>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowCreateModal(false)}
                >
                  <X size={18} />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Nome/Razão Social *</label>
                <Input
                  placeholder="Nome completo ou razão social"
                  value={newClientName}
                  onChange={(e) => setNewClientName(e.target.value)}
                  autoFocus
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Telefone (WhatsApp) *</label>
                <Input
                  placeholder="Ex: 98912345678"
                  value={newClientPhone}
                  onChange={(e) => setNewClientPhone(e.target.value)}
                />
              </div>
              <div className="flex gap-2 pt-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowCreateModal(false)}
                  disabled={creating}
                >
                  Cancelar
                </Button>
                <Button
                  className="flex-1"
                  onClick={handleCreateClient}
                  disabled={creating || !newClientName.trim() || !newClientPhone.trim()}
                >
                  {creating ? 'Criando...' : 'Criar Cliente'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

