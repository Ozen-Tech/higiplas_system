'use client';

import { useState, useEffect } from 'react';
import { Header } from '@/components/dashboard/Header';
import { useClientesV2 } from '@/hooks/useClientesV2';
import { ClienteListItemV2, ClienteV2 } from '@/types';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Edit, Eye, Trash2, Search, Filter, Plus } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { ClienteCreateModal } from '@/components/clientes/ClienteCreateModal';
import { ClienteEditModal } from '@/components/clientes/ClienteEditModal';
import { ClienteViewModal } from '@/components/clientes/ClienteViewModal';

export default function ClientesAdminPage() {
  const { user } = useAuth();
  const { 
    clientes, 
    loading, 
    error, 
    fetchClientes, 
    deleteCliente,
    getClienteById 
  } = useClientesV2();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('TODOS');
  const [selectedCliente, setSelectedCliente] = useState<ClienteV2 | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [viewModalOpen, setViewModalOpen] = useState(false);

  const isAdmin = user?.perfil?.toUpperCase() === 'ADMIN' || user?.perfil?.toUpperCase() === 'GESTOR';

  useEffect(() => {
    if (isAdmin) {
      // Buscar todos os clientes da empresa sem filtros
      fetchClientes({ limit: 1000, skip: 0 });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin]);

  if (!isAdmin) {
    return (
      <>
        <Header>
          <h1 className="text-xl font-bold">Acesso Negado</h1>
        </Header>
        <main className="flex-1 p-6">
          <Card>
            <CardContent className="p-6 text-center">
              <p className="text-red-600">Apenas administradores ou gestores podem acessar esta página.</p>
            </CardContent>
          </Card>
        </main>
      </>
    );
  }

  const handleDelete = async (cliente: ClienteListItemV2) => {
    if (!confirm(`Tem certeza que deseja excluir o cliente "${cliente.nome}"? Esta ação não pode ser desfeita.`)) {
      return;
    }
    
    try {
      await deleteCliente(cliente.id);
      fetchClientes({ limit: 200 });
    } catch (err) {
      console.error('Erro ao excluir cliente:', err);
    }
  };

  const handleView = async (cliente: ClienteListItemV2) => {
    const clienteCompleto = await getClienteById(cliente.id);
    if (clienteCompleto) {
      setSelectedCliente(clienteCompleto);
      setViewModalOpen(true);
    }
  };

  const handleEdit = async (cliente: ClienteListItemV2) => {
    const clienteCompleto = await getClienteById(cliente.id);
    if (clienteCompleto) {
      setSelectedCliente(clienteCompleto);
      setEditModalOpen(true);
    }
  };

  const clientesFiltrados = clientes.filter(cliente => {
    const matchSearch = 
      cliente.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cliente.telefone?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cliente.id.toString().includes(searchTerm);
    
    const matchStatus = statusFilter === 'TODOS' || cliente.status === statusFilter;
    
    return matchSearch && matchStatus;
  });

  return (
    <>
      <Header>
        <h1 className="text-xl font-bold">Gerenciar Clientes</h1>
      </Header>
      <main className="flex-1 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Filtros */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter size={20} /> Filtros
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                  <Input
                    placeholder="Buscar por nome, telefone ou ID..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filtrar por status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="TODOS">Todos os status</SelectItem>
                    <SelectItem value="ATIVO">Ativo</SelectItem>
                    <SelectItem value="INATIVO">Inativo</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Lista de Clientes */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Clientes ({clientesFiltrados.length})</CardTitle>
              <Button onClick={() => setCreateModalOpen(true)} className="gap-2">
                <Plus size={16} />
                Novo Cliente
              </Button>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-12">
                  <p className="text-gray-500">Carregando clientes...</p>
                </div>
              ) : error ? (
                <div className="text-center py-12">
                  <p className="text-red-500">{error}</p>
                </div>
              ) : clientesFiltrados.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p>Nenhum cliente encontrado.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>#ID</TableHead>
                        <TableHead>Nome/Razão Social</TableHead>
                        <TableHead>Telefone</TableHead>
                        <TableHead>Bairro</TableHead>
                        <TableHead>Cidade</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-center">Ações</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {clientesFiltrados.map((cliente) => (
                        <TableRow key={cliente.id}>
                          <TableCell className="font-mono">#{cliente.id}</TableCell>
                          <TableCell className="font-medium">{cliente.nome}</TableCell>
                          <TableCell>{cliente.telefone || 'N/A'}</TableCell>
                          <TableCell>{cliente.bairro || 'N/A'}</TableCell>
                          <TableCell>{cliente.cidade || 'N/A'}</TableCell>
                          <TableCell>
                            <Badge variant={cliente.status === 'ATIVO' ? 'default' : 'secondary'}>
                              {cliente.status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center justify-center gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleView(cliente)}
                                title="Visualizar"
                              >
                                <Eye size={16} />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleEdit(cliente)}
                                title="Editar"
                              >
                                <Edit size={16} />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDelete(cliente)}
                                className="text-red-600 hover:text-red-700"
                                title="Excluir"
                              >
                                <Trash2 size={16} />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Modais */}
      {selectedCliente && (
        <>
          <ClienteViewModal
            cliente={selectedCliente}
            open={viewModalOpen}
            onClose={() => {
              setViewModalOpen(false);
              setSelectedCliente(null);
            }}
          />
          <ClienteEditModal
            cliente={selectedCliente}
            open={editModalOpen}
            onClose={() => {
              setEditModalOpen(false);
              setSelectedCliente(null);
            }}
            onSuccess={() => {
              setEditModalOpen(false);
              setSelectedCliente(null);
              fetchClientes({ limit: 200 });
            }}
          />
        </>
      )}
      <ClienteCreateModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSuccess={() => {
          setCreateModalOpen(false);
          fetchClientes({ limit: 200 });
        }}
      />
    </>
  );
}

