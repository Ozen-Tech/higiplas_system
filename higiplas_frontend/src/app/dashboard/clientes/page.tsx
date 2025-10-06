"use client";

import { useState, useEffect } from 'react';
import { ClienteListItemV2 } from '@/types';
import Link from 'next/link';
import { useClientesV2 } from '@/hooks/useClientesV2';
import { Header } from '@/components/dashboard/Header';
import { CustomTable, Column } from '@/components/dashboard/CustomTable';
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
} from '@heroicons/react/24/outline';

export default function ClientesPage() {
  const { 
    clientes, 
    fetchClientes, 
    searchClientes,
    deleteCliente 
  } = useClientesV2();
  
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchClientes();
  }, [fetchClientes]);

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      await fetchClientes();
      return;
    }
    
    await searchClientes(searchTerm);
  };

  const handleDelete = async (cliente: { id: number; nome: string }) => {
    if (window.confirm(`Tem certeza que deseja remover o cliente "${cliente.nome}"?`)) {
      try {
        await deleteCliente(cliente.id);
      } catch (error) {
        console.error('Erro ao excluir cliente:', error);
      }
    }
  };

  const columns: Column<ClienteListItemV2>[] = [
    {
      accessor: 'nome',
      header: 'Nome',
      render: (cliente) => (
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
              <span className="text-xs font-medium text-indigo-600">
                {cliente.nome.charAt(0).toUpperCase()}
              </span>
            </div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-900 dark:text-white">
              {cliente.nome}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              <PhoneIcon className="w-3 h-3 inline mr-1" />
              {cliente.telefone}
            </div>
          </div>
        </div>
      ),
    },
    {
      accessor: 'bairro',
      header: 'Localização',
      render: (cliente) => (
        <div className="text-sm text-gray-900 dark:text-white">
          {cliente.bairro && cliente.cidade ? (
            <>
              <MapPinIcon className="w-3 h-3 inline mr-1 text-gray-400" />
              {cliente.bairro}, {cliente.cidade}
            </>
          ) : (
            <span className="text-gray-400">Não informado</span>
          )}
        </div>
      ),
    },
    {
      accessor: 'status',
      header: 'Status',
      render: (cliente) => (
        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
          cliente.status === 'ATIVO' 
            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
            : cliente.status === 'INATIVO'
            ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
            : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
        }`}>
          {cliente.status}
        </span>
      ),
    },
    {
      accessor: 'actions',
      header: 'Ações',
      render: (cliente) => (
        <div className="flex items-center space-x-2">
          <Link href={`/dashboard/clientes/${cliente.id}`}>
            <Button variant="secondary" className="p-1">
              <EyeIcon className="h-4 w-4" />
            </Button>
          </Link>
          <Link href={`/dashboard/clientes/${cliente.id}/editar`}>
            <Button variant="secondary" className="p-1">
              <PencilIcon className="h-4 w-4" />
            </Button>
          </Link>
          <button
            onClick={() => handleDelete(cliente)}
            className="p-1 text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <UserGroupIcon className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Clientes
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Gerencie seus clientes
              </p>
            </div>
          </div>
          <Link href="/dashboard/clientes/novo-v2">
            <Button>
              <UserPlusIcon className="h-4 w-4 mr-2" />
              Novo Cliente
            </Button>
          </Link>
        </div>
      </Header>

      <div className="p-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="p-6">
            <div className="flex gap-4 mb-6">
              <div className="flex-1">
                <Input
                  label=""
                  placeholder="Buscar clientes..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button variant="secondary" onClick={handleSearch}>
                <MagnifyingGlassIcon className="h-4 w-4 mr-2" />
                Buscar
              </Button>
            </div>

            <CustomTable
              data={clientes}
              columns={columns}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
