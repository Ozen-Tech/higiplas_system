// /src/app/dashboard/clientes/page.tsx
"use client";

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { useClientes } from '@/hooks/useClientes';
import { Header } from '@/components/dashboard/Header';
import { CustomTable, Column } from '@/components/dashboard/CustomTable';
import ClientLayout from '@/components/ClientLayout';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { Cliente } from '@/types';
import { 
  UserGroupIcon, 
  UserPlusIcon, 
  MagnifyingGlassIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

function ClientesPageContent() {
  const { clientes, loading, searchClientes, deleteCliente } = useClientes();
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  // Filtrar clientes localmente se não houver termo de busca
  const filteredClientes = useMemo(() => {
    if (!searchTerm) return clientes;
    return clientes.filter(cliente => 
      cliente.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cliente.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cliente.cpf_cnpj?.includes(searchTerm) ||
      cliente.telefone?.includes(searchTerm)
    );
  }, [clientes, searchTerm]);

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;
    
    setIsSearching(true);
    try {
      await searchClientes(searchTerm);
    } finally {
      setIsSearching(false);
    }
  };

  const handleDelete = async (cliente: Cliente) => {
    if (window.confirm(`Tem certeza que deseja excluir o cliente "${cliente.nome}"?`)) {
      try {
        await deleteCliente(cliente.id);
      } catch (error) {
        // Erro já tratado no hook
      }
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const formatTipoPessoa = (tipo: string) => {
    return tipo === 'FISICA' ? 'Pessoa Física' : 'Pessoa Jurídica';
  };

  const columns: Column<Cliente>[] = [
    {
      header: 'Nome',
      accessor: 'nome',
      render: (cliente) => (
        <div className="flex flex-col">
          <span className="font-medium text-gray-900 dark:text-white">
            {cliente.nome}
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {formatTipoPessoa(cliente.tipo_pessoa)}
          </span>
        </div>
      ),
    },
    {
      header: 'Contato',
      accessor: 'email',
      render: (cliente) => (
        <div className="flex flex-col">
          {cliente.email && (
            <span className="text-sm text-gray-900 dark:text-white">
              {cliente.email}
            </span>
          )}
          {cliente.telefone && (
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {cliente.telefone}
            </span>
          )}
        </div>
      ),
    },
    {
      header: 'CPF/CNPJ',
      accessor: 'cpf_cnpj',
      render: (cliente) => (
        <span className="text-sm text-gray-900 dark:text-white">
          {cliente.cpf_cnpj || '-'}
        </span>
      ),
    },
    {
      header: 'Data Cadastro',
      accessor: 'data_cadastro',
      render: (cliente) => (
        <span className="text-sm text-gray-900 dark:text-white">
          {formatDate(cliente.data_cadastro)}
        </span>
      ),
    },
    {
      header: 'Status',
      accessor: 'ativo',
      render: (cliente) => (
        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
          cliente.ativo 
            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }`}>
          {cliente.ativo ? 'Ativo' : 'Inativo'}
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
                    Clientes
                  </h1>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Gerencie seus clientes e informações de contato
                  </p>
                </div>
              </div>
              <Link href="/dashboard/clientes/novo">
                <Button className="flex items-center space-x-2">
                  <UserPlusIcon className="h-5 w-5" />
                  <span>Novo Cliente</span>
                </Button>
              </Link>
            </div>
          </Header>

          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 dark:bg-gray-900 p-6">
            {/* Barra de Pesquisa */}
            <div className="mb-6">
              <div className="flex space-x-4">
                <div className="flex-1">
                  <Input
                    label=""
                    type="text"
                    placeholder="Buscar por nome, email, CPF/CNPJ ou telefone..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </div>
                <Button 
                  onClick={handleSearch}
                  disabled={isSearching}
                  className="flex items-center space-x-2"
                >
                  <MagnifyingGlassIcon className="h-5 w-5" />
                  <span>{isSearching ? 'Buscando...' : 'Buscar'}</span>
                </Button>
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
                    {searchTerm ? 'Tente ajustar os termos de busca.' : 'Comece criando um novo cliente.'}
                  </p>
                  {!searchTerm && (
                    <div className="mt-6">
                      <Link href="/dashboard/clientes/novo">
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

export default function ClientesPage() {
  return (
    <ClientLayout>
      <ClientesPageContent />
    </ClientLayout>
  );
}