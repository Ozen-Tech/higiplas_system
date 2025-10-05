// /src/app/dashboard/clientes/page-v2.tsx
"use client";

import { useState, useMemo, useEffect } from 'react';
import Link from 'next/link';
import { useClientesV2, ClienteListItem } from '@/hooks/useClientesV2';
import { Header } from '@/components/dashboard/Header';
import { CustomTable, Column } from '@/components/dashboard/CustomTable';
import ClientLayout from '@/components/ClientLayout';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { 
  UserGroupIcon, 
  UserPlusIcon, 
  MagnifyingGlassIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  MapPinIcon,
  PhoneIcon,
  LightningBoltIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';

function ClientesV2PageContent() {
  const { 
    clientes, 
    loading, 
    fetchClientes, 
    searchClientes, 
    getClientesByBairro,
    getMeusClientes,
    deleteCliente 
  } = useClientesV2();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [bairroFilter, setBairroFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [meusClientesOnly, setMeusClientesOnly] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  // Filtrar clientes localmente
  const filteredClientes = useMemo(() => {
    let result = clientes;

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(cliente => 
        cliente.nome.toLowerCase().includes(term) ||
        cliente.telefone.includes(searchTerm) ||
        cliente.bairro?.toLowerCase().includes(term) ||
        cliente.cidade?.toLowerCase().includes(term)
      );
    }

    if (bairroFilter) {
      result = result.filter(cliente => 
        cliente.bairro?.toLowerCase().includes(bairroFilter.toLowerCase())
      );
    }

    if (statusFilter) {
      result = result.filter(cliente => cliente.status === statusFilter);
    }

    return result;
  }, [clientes, searchTerm, bairroFilter, statusFilter]);

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      await fetchClientes();
      return;
    }
    
    setIsSearching(true);
    try {
      await searchClientes(searchTerm);
    } finally {
      setIsSearching(false);
    }
  };

  const handleBairroFilter = async () => {
    if (!bairroFilter.trim()) {
      await fetchClientes();
      return;
    }
    
    setIsSearching(true);
    try {
      await getClientesByBairro(bairroFilter);
    } finally {
      setIsSearching(false);
    }
  };

  const handleMeusClientes = async () => {
    setMeusClientesOnly(!meusClientesOnly);
    
    setIsSearching(true);
    try {
      if (!meusClientesOnly) {
        await getMeusClientes();
      } else {
        await fetchClientes();
      }
    } finally {
      setIsSearching(false);
    }
  };

  const handleDelete = async (cliente: ClienteListItem) => {
    if (window.confirm(`Tem certeza que deseja remover o cliente "${cliente.nome}"?`)) {
      try {
        await deleteCliente(cliente.id);
      } catch {
        // Erro já tratado no hook
      }
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setBairroFilter('');
    setStatusFilter('');
    setMeusClientesOnly(false);
    fetchClientes();
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return "Nunca";
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      }).format(date);
    } catch {
      return "Data inválida";
    }
  };

  const formatTelefone = (telefone: string) => {
    const cleaned = telefone.replace(/\D/g, '');
    if (cleaned.length === 11) {
      return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7)}`;
    } else if (cleaned.length === 10) {
      return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 6)}-${cleaned.slice(6)}`;
    }
    return telefone;
  };

  const columns: Column<ClienteListItem>[] = [
    {
      header: 'Cliente',
      accessor: 'nome',
      render: (cliente) => (
        <div className="flex flex-col">
          <span className="font-medium text-gray-900 dark:text-white">
            {cliente.nome}
          </span>
          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mt-1">
            <PhoneIcon className="h-3 w-3 mr-1" />
            {formatTelefone(cliente.telefone)}
          </div>
        </div>
      ),
    },
    {
      header: 'Localização',
      accessor: 'bairro',
      render: (cliente) => (
        <div className="flex items-center text-sm text-gray-900 dark:text-white">
          <MapPinIcon className="h-4 w-4 mr-1 text-gray-400" />
          <div>
            {cliente.bairro && (
              <div className="font-medium">{cliente.bairro}</div>
            )}
            {cliente.cidade && (
              <div className="text-gray-500 dark:text-gray-400">{cliente.cidade}</div>
            )}
            {!cliente.bairro && !cliente.cidade && (
              <span className="text-gray-400">Não informado</span>
            )}
          </div>
        </div>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (cliente) => (
        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
          cliente.status === 'ATIVO'
            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
            : cliente.status === 'PROSPECTO'
            ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }`}>
          {cliente.status === 'ATIVO' ? 'Ativo' : 
           cliente.status === 'PROSPECTO' ? 'Prospecto' : 'Inativo'}
        </span>
      ),
    },
    {
      header: 'Última Venda',
      accessor: 'ultima_venda',
      render: (cliente) => (
        <span className="text-sm text-gray-900 dark:text-white">
          {formatDate(cliente.ultima_venda)}
        </span>
      ),
    },
    {
      header: 'Ações',
      accessor: 'actions',
      render: (cliente) => (
        <div className="flex space-x-2">
          <Link href={`/dashboard/clientes/${cliente.id}`}>
            <button className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
              <EyeIcon className="h-4 w-4" />
            </button>
          </Link>
          <Link href={`/dashboard/clientes/${cliente.id}/editar`}>
            <button className="text-yellow-600 hover:text-yellow-800 dark:text-yellow-400 dark:hover:text-yellow-300">
              <PencilIcon className="h-4 w-4" />
            </button>
          </Link>
          <button 
            onClick={() => handleDelete(cliente)}
            className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      ),
    },
  ];

  // Recarregar quando montar
  useEffect(() => {
    fetchClientes();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="flex">
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <UserGroupIcon className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Clientes v2
                  </h1>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Sistema otimizado para vendedores
                  </p>
                </div>
              </div>
              <div className="flex space-x-3">
                <Link href="/dashboard/clientes/novo-v2">
                  <Button className="flex items-center space-x-2 bg-yellow-500 hover:bg-yellow-600">
                    <LightningBoltIcon className="h-5 w-5" />
                    <span>Cadastro Rápido</span>
                  </Button>
                </Link>
                <Link href="/dashboard/clientes/novo-v2">
                  <Button className="flex items-center space-x-2">
                    <UserPlusIcon className="h-5 w-5" />
                    <span>Novo Cliente</span>
                  </Button>
                </Link>
              </div>
            </div>
          </Header>

          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 dark:bg-gray-900 p-6">
            {/* Filtros */}
            <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center space-x-4 mb-4">
                <FunnelIcon className="h-5 w-5 text-gray-400" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Filtros</h3>
                <button
                  onClick={clearFilters}
                  className="text-sm text-indigo-600 hover:text-indigo-800 dark:text-indigo-400"
                >
                  Limpar filtros
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Busca Geral */}
                <div className="flex space-x-2">
                  <Input
                    label=""
                    type="text"
                    placeholder="Buscar por nome, telefone..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                  <Button 
                    onClick={handleSearch}
                    disabled={isSearching}
                    className="flex items-center px-3"
                  >
                    <MagnifyingGlassIcon className="h-4 w-4" />
                  </Button>
                </div>

                {/* Filtro por Bairro */}
                <div className="flex space-x-2">
                  <Input
                    label=""
                    type="text"
                    placeholder="Filtrar por bairro..."
                    value={bairroFilter}
                    onChange={(e) => setBairroFilter(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleBairroFilter()}
                  />
                  <Button 
                    onClick={handleBairroFilter}
                    disabled={isSearching}
                    className="flex items-center px-3"
                  >
                    <MapPinIcon className="h-4 w-4" />
                  </Button>
                </div>

                {/* Filtro por Status */}
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Todos os status</option>
                  <option value="ATIVO">Ativo</option>
                  <option value="PROSPECTO">Prospecto</option>
                  <option value="INATIVO">Inativo</option>
                </select>

                {/* Meus Clientes */}
                <button
                  onClick={handleMeusClientes}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    meusClientesOnly
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300'
                  }`}
                >
                  Meus Clientes
                </button>
              </div>
            </div>

            {/* Estatísticas Rápidas */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <div className="flex items-center">
                  <UserGroupIcon className="h-8 w-8 text-blue-500" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total</p>
                    <p className="text-2xl font-semibold text-gray-900 dark:text-white">{filteredClientes.length}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <div className="flex items-center">
                  <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                    <div className="h-4 w-4 bg-green-500 rounded-full"></div>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Ativos</p>
                    <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                      {filteredClientes.filter(c => c.status === 'ATIVO').length}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <div className="flex items-center">
                  <div className="h-8 w-8 bg-yellow-100 rounded-full flex items-center justify-center">
                    <div className="h-4 w-4 bg-yellow-500 rounded-full"></div>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Prospectos</p>
                    <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                      {filteredClientes.filter(c => c.status === 'PROSPECTO').length}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <div className="flex items-center">
                  <MapPinIcon className="h-8 w-8 text-purple-500" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Bairros</p>
                    <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                      {new Set(filteredClientes.map(c => c.bairro).filter(Boolean)).size}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Tabela de Clientes */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-medium text-gray-900 dark:text-white">
                  Lista de Clientes ({filteredClientes.length})
                </h2>
              </div>
              
              {loading ? (
                <div className="flex justify-center items-center h-64">
                  <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-500"></div>
                </div>
              ) : filteredClientes.length === 0 ? (
                <div className="text-center py-12">
                  <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                    Nenhum cliente encontrado
                  </h3>
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    {searchTerm || bairroFilter || statusFilter ? 'Tente ajustar os filtros.' : 'Comece criando um novo cliente.'}
                  </p>
                  {!searchTerm && !bairroFilter && !statusFilter && (
                    <div className="mt-6 flex justify-center space-x-3">
                      <Link href="/dashboard/clientes/novo-v2">
                        <Button className="flex items-center space-x-2 bg-yellow-500 hover:bg-yellow-600">
                          <LightningBoltIcon className="h-5 w-5" />
                          <span>Cadastro Rápido</span>
                        </Button>
                      </Link>
                      <Link href="/dashboard/clientes/novo-v2">
                        <Button className="flex items-center space-x-2">
                          <UserPlusIcon className="h-5 w-5" />
                          <span>Novo Cliente</span>
                        </Button>
                      </Link>
                    </div>
                  )}
                </div>
              ) : (
                <CustomTable data={filteredClientes} columns={columns} />
              )}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

export default function ClientesV2Page() {
  return (
    <ClientLayout>
      <ClientesV2PageContent />
    </ClientLayout>
  );
}
