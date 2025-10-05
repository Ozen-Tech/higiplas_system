// /src/app/dashboard/clientes/novo/page.tsx
"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useClientesV2, ClienteCreate } from '@/hooks/useClientesV2';
import { Header } from '@/components/dashboard/Header';
import ClientLayout from '@/components/ClientLayout';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { 
  UserPlusIcon, 
  ArrowLeftIcon,
  UserIcon,
  PhoneIcon,
  MapPinIcon,
  LightningBoltIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

function NovoClientePageContent() {
  const router = useRouter();
  const { createCliente, createClienteQuick } = useClientesV2();
  const [loading, setLoading] = useState(false);
  const [modoRapido, setModoRapido] = useState(true);
  
  // Formulário rápido (apenas nome e telefone)
  const [formRapido, setFormRapido] = useState({
    nome: '',
    telefone: ''
  });
  
  // Formulário completo
  const [formCompleto, setFormCompleto] = useState<ClienteCreateV2>({
    nome: '',
    telefone: '',
    tipo_pessoa: 'FISICA',
    cpf_cnpj: '',
    bairro: '',
    cidade: '',
    observacoes: '',
    referencia_localizacao: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleInputRapido = (field: string, value: string) => {
    setFormRapido(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleInputCompleto = (field: string, value: string) => {
    setFormCompleto(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.nome.trim()) {
      newErrors.nome = 'Nome é obrigatório';
    }

    if (formData.cpf_cnpj && formData.tipo_pessoa === 'FISICA') {
      // Validação básica de CPF (11 dígitos)
      const cpf = formData.cpf_cnpj.replace(/\D/g, '');
      if (cpf.length !== 11) {
        newErrors.cpf_cnpj = 'CPF deve ter 11 dígitos';
      }
    }

    if (formData.cpf_cnpj && formData.tipo_pessoa === 'JURIDICA') {
      // Validação básica de CNPJ (14 dígitos)
      const cnpj = formData.cpf_cnpj.replace(/\D/g, '');
      if (cnpj.length !== 14) {
        newErrors.cpf_cnpj = 'CNPJ deve ter 14 dígitos';
      }
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }

    if (formData.endereco?.cep && !/^\d{5}-?\d{3}$/.test(formData.endereco.cep)) {
      newErrors.cep = 'CEP inválido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Por favor, corrija os erros no formulário');
      return;
    }

    setLoading(true);
    try {
      // Limpar campos vazios do endereço
      const enderecoLimpo = formData.endereco ? Object.fromEntries(
        Object.entries(formData.endereco).filter(([, value]) => value && value.trim() !== '')
      ) : {};
      
      const clienteData = {
        ...formData,
        endereco: Object.keys(enderecoLimpo).length > 0 ? enderecoLimpo : undefined
      };
      
      // Remover campos vazios opcionais
      if (!clienteData.cpf_cnpj?.trim()) delete clienteData.cpf_cnpj;
      if (!clienteData.email?.trim()) delete clienteData.email;
      if (!clienteData.telefone?.trim()) delete clienteData.telefone;
      
      await createCliente(clienteData);
      toast.success('Cliente criado com sucesso!');
      router.push('/dashboard/clientes');
    } catch {
      // Erro já tratado no hook
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="flex">
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Link href="/dashboard/clientes">
                  <button className="text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200">
                    <ArrowLeftIcon className="h-6 w-6" />
                  </button>
                </Link>
                <UserPlusIcon className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Novo Cliente
                  </h1>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Cadastre um novo cliente no sistema
                  </p>
                </div>
              </div>
            </div>
          </Header>

          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 dark:bg-gray-900 p-6">
            <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-6">
              {/* Informações Básicas */}
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                    <UserIcon className="h-5 w-5 mr-2" />
                    Informações Básicas
                  </h2>
                </div>
                <div className="p-6 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label="Nome *"
                      type="text"
                      value={formData.nome}
                      onChange={(e) => handleInputChange('nome', e.target.value)}
                      error={errors.nome}
                      placeholder="Nome completo do cliente"
                    />
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Tipo de Pessoa *
                      </label>
                      <select
                        value={formData.tipo_pessoa}
                        onChange={(e) => handleInputChange('tipo_pessoa', e.target.value)}
                        className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        <option value="FISICA">Pessoa Física</option>
                        <option value="JURIDICA">Pessoa Jurídica</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label={formData.tipo_pessoa === 'FISICA' ? 'CPF' : 'CNPJ'}
                      type="text"
                      value={formData.cpf_cnpj || ''}
                      onChange={(e) => handleInputChange('cpf_cnpj', e.target.value)}
                      error={errors.cpf_cnpj}
                      placeholder={formData.tipo_pessoa === 'FISICA' ? '000.000.000-00' : '00.000.000/0000-00'}
                    />
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Status
                      </label>
                      <select
                        value={formData.ativo ? 'true' : 'false'}
                        onChange={(e) => handleInputChange('ativo', e.target.value === 'true')}
                        className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        <option value="true">Ativo</option>
                        <option value="false">Inativo</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              {/* Informações de Contato */}
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                    <EnvelopeIcon className="h-5 w-5 mr-2" />
                    Contato
                  </h2>
                </div>
                <div className="p-6 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label="Email"
                      type="email"
                      value={formData.email || ''}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      error={errors.email}
                      placeholder="email@exemplo.com"
                    />
                    
                    <Input
                      label="Telefone"
                      type="tel"
                      value={formData.telefone || ''}
                      onChange={(e) => handleInputChange('telefone', e.target.value)}
                      placeholder="(11) 99999-9999"
                    />
                  </div>
                </div>
              </div>

              {/* Endereço */}
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                    <MapPinIcon className="h-5 w-5 mr-2" />
                    Endereço
                  </h2>
                </div>
                <div className="p-6 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="md:col-span-2">
                      <Input
                        label="Logradouro"
                        type="text"
                        value={formData.endereco?.logradouro || ''}
                        onChange={(e) => handleEnderecoChange('logradouro', e.target.value)}
                        placeholder="Rua, Avenida, etc."
                      />
                    </div>
                    
                    <Input
                      label="Número"
                      type="text"
                      value={formData.endereco?.numero || ''}
                      onChange={(e) => handleEnderecoChange('numero', e.target.value)}
                      placeholder="123"
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label="Complemento"
                      type="text"
                      value={formData.endereco?.complemento || ''}
                      onChange={(e) => handleEnderecoChange('complemento', e.target.value)}
                      placeholder="Apto, Sala, etc."
                    />
                    
                    <Input
                      label="Bairro"
                      type="text"
                      value={formData.endereco?.bairro || ''}
                      onChange={(e) => handleEnderecoChange('bairro', e.target.value)}
                      placeholder="Nome do bairro"
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Input
                      label="Cidade"
                      type="text"
                      value={formData.endereco?.cidade || ''}
                      onChange={(e) => handleEnderecoChange('cidade', e.target.value)}
                      placeholder="Nome da cidade"
                    />
                    
                    <Input
                      label="Estado"
                      type="text"
                      value={formData.endereco?.estado || ''}
                      onChange={(e) => handleEnderecoChange('estado', e.target.value)}
                      placeholder="SP"
                      maxLength={2}
                    />
                    
                    <Input
                      label="CEP"
                      type="text"
                      value={formData.endereco?.cep || ''}
                      onChange={(e) => handleEnderecoChange('cep', e.target.value)}
                      error={errors.cep}
                      placeholder="00000-000"
                    />
                  </div>
                </div>
              </div>

              {/* Botões de Ação */}
              <div className="flex justify-end space-x-4">
                <Link href="/dashboard/clientes">
                  <Button 
                    type="button" 
                    className="bg-gray-500 hover:bg-gray-600 text-white"
                  >
                    Cancelar
                  </Button>
                </Link>
                <Button 
                  type="submit" 
                  disabled={loading}
                  className="flex items-center space-x-2"
                >
                  <UserPlusIcon className="h-5 w-5" />
                  <span>{loading ? 'Salvando...' : 'Salvar Cliente'}</span>
                </Button>
              </div>
            </form>
          </main>
        </div>
      </div>
    </div>
  );
}

export default function NovoClientePage() {
  return (
    <ClientLayout>
      <NovoClientePageContent />
    </ClientLayout>
  );
}