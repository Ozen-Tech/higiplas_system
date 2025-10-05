// /src/app/dashboard/clientes/novo-v2/page.tsx
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

function NovoClienteV2PageContent() {
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
  const [formCompleto, setFormCompleto] = useState<ClienteCreate>({
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

  const validateFormRapido = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formRapido.nome.trim()) {
      newErrors.nome = 'Nome é obrigatório';
    }

    if (!formRapido.telefone.trim()) {
      newErrors.telefone = 'Telefone é obrigatório';
    } else if (formRapido.telefone.replace(/\D/g, '').length < 10) {
      newErrors.telefone = 'Telefone deve ter pelo menos 10 dígitos';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateFormCompleto = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formCompleto.nome.trim()) {
      newErrors.nome = 'Nome é obrigatório';
    }

    if (!formCompleto.telefone.trim()) {
      newErrors.telefone = 'Telefone é obrigatório';
    } else if (formCompleto.telefone.replace(/\D/g, '').length < 10) {
      newErrors.telefone = 'Telefone deve ter pelo menos 10 dígitos';
    }

    if (formCompleto.cpf_cnpj) {
      const doc = formCompleto.cpf_cnpj.replace(/\D/g, '');
      if (formCompleto.tipo_pessoa === 'FISICA' && doc.length !== 11) {
        newErrors.cpf_cnpj = 'CPF deve ter 11 dígitos';
      } else if (formCompleto.tipo_pessoa === 'JURIDICA' && doc.length !== 14) {
        newErrors.cpf_cnpj = 'CNPJ deve ter 14 dígitos';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmitRapido = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateFormRapido()) {
      toast.error('Por favor, corrija os erros no formulário');
      return;
    }

    setLoading(true);
    try {
      await createClienteQuick({
        nome: formRapido.nome.trim(),
        telefone: formRapido.telefone.replace(/\D/g, '')
      });
      
      toast.success('Cliente criado rapidamente!');
      router.push('/dashboard/clientes');
    } catch {
      // Erro já tratado no hook
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitCompleto = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateFormCompleto()) {
      toast.error('Por favor, corrija os erros no formulário');
      return;
    }

    setLoading(true);
    try {
      // Limpar campos vazios
      const clienteData: ClienteCreate = {
        nome: formCompleto.nome.trim(),
        telefone: formCompleto.telefone.replace(/\D/g, ''),
        tipo_pessoa: formCompleto.tipo_pessoa,
      };

      if (formCompleto.cpf_cnpj?.trim()) {
        clienteData.cpf_cnpj = formCompleto.cpf_cnpj.replace(/\D/g, '');
      }
      if (formCompleto.bairro?.trim()) {
        clienteData.bairro = formCompleto.bairro.trim();
      }
      if (formCompleto.cidade?.trim()) {
        clienteData.cidade = formCompleto.cidade.trim();
      }
      if (formCompleto.observacoes?.trim()) {
        clienteData.observacoes = formCompleto.observacoes.trim();
      }
      if (formCompleto.referencia_localizacao?.trim()) {
        clienteData.referencia_localizacao = formCompleto.referencia_localizacao.trim();
      }
      
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
                    {modoRapido ? 'Cadastro ultra-rápido para vendedores' : 'Cadastro completo'}
                  </p>
                </div>
              </div>
              
              {/* Toggle Modo */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setModoRapido(true)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    modoRapido 
                      ? 'bg-indigo-600 text-white' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300'
                  }`}
                >
                  <LightningBoltIcon className="h-4 w-4 inline mr-1" />
                  Rápido
                </button>
                <button
                  onClick={() => setModoRapido(false)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    !modoRapido 
                      ? 'bg-indigo-600 text-white' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300'
                  }`}
                >
                  <UserIcon className="h-4 w-4 inline mr-1" />
                  Completo
                </button>
              </div>
            </div>
          </Header>

          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 dark:bg-gray-900 p-6">
            <div className="max-w-2xl mx-auto">
              
              {modoRapido ? (
                /* ============= FORMULÁRIO RÁPIDO ============= */
                <form onSubmit={handleSubmitRapido} className="space-y-6">
                  <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                    <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                      <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                        <LightningBoltIcon className="h-5 w-5 mr-2 text-yellow-500" />
                        Cadastro Ultra-Rápido
                      </h2>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        Apenas nome e telefone - perfeito para vendedores em campo
                      </p>
                    </div>
                    <div className="p-6 space-y-4">
                      <Input
                        label="Nome do Cliente *"
                        type="text"
                        value={formRapido.nome}
                        onChange={(e) => handleInputRapido('nome', e.target.value)}
                        error={errors.nome}
                        placeholder="Ex: João da Silva"
                        className="text-lg"
                      />
                      
                      <Input
                        label="WhatsApp/Telefone *"
                        type="tel"
                        value={formRapido.telefone}
                        onChange={(e) => handleInputRapido('telefone', e.target.value)}
                        error={errors.telefone}
                        placeholder="(11) 99999-9999"
                        className="text-lg"
                      />
                    </div>
                  </div>

                  {/* Botões */}
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
                      className="flex items-center space-x-2 bg-yellow-500 hover:bg-yellow-600"
                    >
                      <LightningBoltIcon className="h-5 w-5" />
                      <span>{loading ? 'Salvando...' : 'Salvar Rápido'}</span>
                    </Button>
                  </div>
                </form>
              ) : (
                /* ============= FORMULÁRIO COMPLETO ============= */
                <form onSubmit={handleSubmitCompleto} className="space-y-6">
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
                          value={formCompleto.nome}
                          onChange={(e) => handleInputCompleto('nome', e.target.value)}
                          error={errors.nome}
                          placeholder="Nome completo"
                        />
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Tipo de Pessoa
                          </label>
                          <select
                            value={formCompleto.tipo_pessoa}
                            onChange={(e) => handleInputCompleto('tipo_pessoa', e.target.value)}
                            className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                          >
                            <option value="FISICA">Pessoa Física</option>
                            <option value="JURIDICA">Pessoa Jurídica</option>
                          </select>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Input
                          label="WhatsApp/Telefone *"
                          type="tel"
                          value={formCompleto.telefone}
                          onChange={(e) => handleInputCompleto('telefone', e.target.value)}
                          error={errors.telefone}
                          placeholder="(11) 99999-9999"
                        />
                        
                        <Input
                          label={formCompleto.tipo_pessoa === 'FISICA' ? 'CPF' : 'CNPJ'}
                          type="text"
                          value={formCompleto.cpf_cnpj || ''}
                          onChange={(e) => handleInputCompleto('cpf_cnpj', e.target.value)}
                          error={errors.cpf_cnpj}
                          placeholder={formCompleto.tipo_pessoa === 'FISICA' ? '000.000.000-00' : '00.000.000/0000-00'}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Localização */}
                  <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                    <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                      <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                        <MapPinIcon className="h-5 w-5 mr-2" />
                        Localização
                      </h2>
                    </div>
                    <div className="p-6 space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Input
                          label="Bairro"
                          type="text"
                          value={formCompleto.bairro || ''}
                          onChange={(e) => handleInputCompleto('bairro', e.target.value)}
                          placeholder="Ex: Centro"
                        />
                        
                        <Input
                          label="Cidade"
                          type="text"
                          value={formCompleto.cidade || ''}
                          onChange={(e) => handleInputCompleto('cidade', e.target.value)}
                          placeholder="Ex: São Luís"
                        />
                      </div>
                      
                      <Input
                        label="Ponto de Referência"
                        type="text"
                        value={formCompleto.referencia_localizacao || ''}
                        onChange={(e) => handleInputCompleto('referencia_localizacao', e.target.value)}
                        placeholder="Ex: Próximo ao mercado central"
                      />
                    </div>
                  </div>

                  {/* Observações */}
                  <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                    <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                      <h2 className="text-lg font-medium text-gray-900 dark:text-white">
                        Observações do Vendedor
                      </h2>
                    </div>
                    <div className="p-6">
                      <textarea
                        value={formCompleto.observacoes || ''}
                        onChange={(e) => handleInputCompleto('observacoes', e.target.value)}
                        placeholder="Ex: Cliente preferencial, paga à vista, compra sempre às sextas..."
                        rows={4}
                        className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        maxLength={500}
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        {(formCompleto.observacoes || '').length}/500 caracteres
                      </p>
                    </div>
                  </div>

                  {/* Botões */}
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
              )}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

export default function NovoClienteV2Page() {
  return (
    <ClientLayout>
      <NovoClienteV2PageContent />
    </ClientLayout>
  );
}
