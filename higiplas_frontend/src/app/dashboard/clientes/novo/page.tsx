"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useClientesV2 } from '@/hooks/useClientesV2';
import { ClienteCreateV2 } from '@/types';
import { Header } from '@/components/dashboard/Header';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { 
  UserPlusIcon, 
  ArrowLeftIcon,
  BoltIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export default function NovoClientePage() {
  const { createCliente } = useClientesV2();

  const [formData, setFormData] = useState<ClienteCreateV2>({
    nome: '',
    telefone: '',
    tipo_pessoa: 'FISICA'
  });

  const handleSubmit = async () => {
    try {
      await createCliente(formData);
      toast.success('Cliente criado com sucesso!');
    } catch {
      toast.error('Erro ao criar cliente');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <UserPlusIcon className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Novo Cliente
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Criar novo cliente
              </p>
            </div>
          </div>
          <Link href="/dashboard/clientes">
            <Button variant="secondary">
              <ArrowLeftIcon className="h-4 w-4 mr-2" />
              Voltar
            </Button>
          </Link>
        </div>
      </Header>

      <div className="p-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nome
                </label>
                <Input
                  label=""
                  value={formData.nome}
                  onChange={(e) => setFormData(prev => ({ ...prev, nome: e.target.value }))}
                  placeholder="Nome do cliente"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Telefone
                </label>
                <Input
                  label=""
                  value={formData.telefone}
                  onChange={(e) => setFormData(prev => ({ ...prev, telefone: e.target.value }))}
                  placeholder="(11) 99999-9999"
                />
              </div>
            </div>

            <div className="mt-6 flex justify-end space-x-3">
              <Link href="/dashboard/clientes">
                <Button variant="secondary">
                  Cancelar
                </Button>
              </Link>
              <Button
                onClick={handleSubmit}
                disabled={!formData.nome.trim() || !formData.telefone.trim()}
              >
                <BoltIcon className="h-4 w-4 mr-2" />
                Criar Cliente
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
