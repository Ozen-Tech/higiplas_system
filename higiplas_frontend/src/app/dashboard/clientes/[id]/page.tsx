// /src/app/dashboard/clientes/[id]/page.tsx
"use client";

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useClientes } from '@/hooks/useClientes';
import { Header } from '@/components/dashboard/Header';
import ClientLayout from '@/components/ClientLayout';
import Button from '@/components/Button';
import { Cliente, HistoricoPagamento, ResumoVendasCliente } from '@/types';
import { 
  UserIcon, 
  PencilIcon, 
  ArrowLeftIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';

interface ClienteDetalhesProps {
  cliente: Cliente;
  historicoPagamentos: HistoricoPagamento[];
  resumoVendas: ResumoVendasCliente;
}

function ClienteDetalhes({ cliente, historicoPagamentos, resumoVendas }: ClienteDetalhesProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatTipoPessoa = (tipo: string) => {
    return tipo === 'FISICA' ? 'Pessoa Física' : 'Pessoa Jurídica';
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pago':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'pendente':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'atrasado':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Informações Básicas */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
            <UserIcon className="h-5 w-5 mr-2" />
            Informações Básicas
          </h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Nome
              </label>
              <p className="text-sm text-gray-900 dark:text-white">{cliente.nome}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Tipo de Pessoa
              </label>
              <p className="text-sm text-gray-900 dark:text-white">
                {formatTipoPessoa(cliente.tipo_pessoa)}
              </p>
            </div>
            
            {cliente.cpf_cnpj && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {cliente.tipo_pessoa === 'FISICA' ? 'CPF' : 'CNPJ'}
                </label>
                <p className="text-sm text-gray-900 dark:text-white">{cliente.cpf_cnpj}</p>
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Status
              </label>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                cliente.ativo 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              }`}>
                {cliente.ativo ? 'Ativo' : 'Inativo'}
              </span>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Data de Cadastro
              </label>
              <p className="text-sm text-gray-900 dark:text-white flex items-center">
                <CalendarIcon className="h-4 w-4 mr-1" />
                {formatDate(cliente.data_cadastro)}
              </p>
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
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {cliente.email && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email
                </label>
                <p className="text-sm text-gray-900 dark:text-white flex items-center">
                  <EnvelopeIcon className="h-4 w-4 mr-1" />
                  {cliente.email}
                </p>
              </div>
            )}
            
            {cliente.telefone && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Telefone
                </label>
                <p className="text-sm text-gray-900 dark:text-white flex items-center">
                  <PhoneIcon className="h-4 w-4 mr-1" />
                  {cliente.telefone}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Endereços */}
      {cliente.enderecos && cliente.enderecos.length > 0 && (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
              <MapPinIcon className="h-5 w-5 mr-2" />
              Endereços
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-6">
              {cliente.enderecos.map((endereco, index) => (
                <div key={index} className="border-b border-gray-200 dark:border-gray-700 pb-6 last:border-b-0">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {endereco.logradouro && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Logradouro
                        </label>
                        <p className="text-sm text-gray-900 dark:text-white">{endereco.logradouro}</p>
                      </div>
                    )}
                    
                    {endereco.numero && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Número
                        </label>
                        <p className="text-sm text-gray-900 dark:text-white">{endereco.numero}</p>
                      </div>
                    )}
                    
                    {endereco.complemento && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Complemento
                        </label>
                        <p className="text-sm text-gray-900 dark:text-white">{endereco.complemento}</p>
                      </div>
                    )}
                    
                    {endereco.bairro && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Bairro
                        </label>
                        <p className="text-sm text-gray-900 dark:text-white">{endereco.bairro}</p>
                      </div>
                    )}
                    
                    {endereco.cidade && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Cidade
                        </label>
                        <p className="text-sm text-gray-900 dark:text-white">{endereco.cidade}</p>
                      </div>
                    )}
                    
                    {endereco.estado && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Estado
                        </label>
                        <p className="text-sm text-gray-900 dark:text-white">{endereco.estado}</p>
                      </div>
                    )}
                    
                    {endereco.cep && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          CEP
                        </label>
                        <p className="text-sm text-gray-900 dark:text-white">{endereco.cep}</p>
                      </div>
                    )}
                    
                    {endereco.tipo && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Tipo
                        </label>
                        <p className="text-sm text-gray-900 dark:text-white">{endereco.tipo}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Resumo de Vendas */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
            <CurrencyDollarIcon className="h-5 w-5 mr-2" />
            Resumo de Vendas
          </h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                {resumoVendas.quantidade_orcamentos || 0}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total de Orçamentos</p>
            </div>
            
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                {formatCurrency(resumoVendas.total_vendas || 0)}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Valor Total de Vendas</p>
            </div>
            
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {formatCurrency((resumoVendas.total_vendas || 0) / (resumoVendas.quantidade_orcamentos || 1))}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Valor Médio por Orçamento</p>
            </div>
            
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {resumoVendas.mes || 'N/A'}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Período</p>
            </div>
          </div>
        </div>
      </div>

      {/* Histórico de Pagamentos */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
            <DocumentTextIcon className="h-5 w-5 mr-2" />
            Histórico de Pagamentos ({historicoPagamentos.length})
          </h2>
        </div>
        <div className="p-6">
          {historicoPagamentos.length === 0 ? (
            <p className="text-center text-gray-500 dark:text-gray-400 py-8">
              Nenhum pagamento registrado para este cliente.
            </p>
          ) : (
            <div className="space-y-4">
              {historicoPagamentos.map((pagamento) => (
                <div key={pagamento.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          getStatusColor(pagamento.status || 'pendente')
                        }`}>
                          {pagamento.status}
                        </span>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          {formatDate(pagamento.data_pagamento)}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Valor
                          </label>
                          <p className="text-sm font-semibold text-gray-900 dark:text-white">
                            {formatCurrency(pagamento.valor)}
                          </p>
                        </div>
                        
                        <div>
                          <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Método de Pagamento
                          </label>
                          <p className="text-sm text-gray-900 dark:text-white">
                            {pagamento.metodo_pagamento}
                          </p>
                        </div>
                        
                        {pagamento.observacoes && (
                          <div>
                            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                              Observações
                            </label>
                            <p className="text-sm text-gray-900 dark:text-white">
                              {pagamento.observacoes}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ClienteDetalhesPageContent() {
  const params = useParams();
  const router = useRouter();
  const { getClienteById } = useClientes();
  const [cliente, setCliente] = useState<Cliente | null>(null);
  const [historicoPagamentos, setHistoricoPagamentos] = useState<HistoricoPagamento[]>([]);
  const [resumoVendas, setResumoVendas] = useState<ResumoVendasCliente | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadClienteData = async () => {
      if (!params.id) return;
      
      try {
        setLoading(true);
        const clienteId = Array.isArray(params.id) ? params.id[0] : params.id;
        
        // Carregar dados do cliente
        const clienteData = await getClienteById(parseInt(clienteId));
        setCliente(clienteData);
        
        // Carregar histórico de pagamentos
        try {
          const historico = await apiService.get(`/clientes/${clienteId}/historico-pagamentos`);
          const historicoMapeado = historico?.data?.historico_pagamentos?.map((p: HistoricoPagamento) => ({
            ...p,
            metodo_pagamento: p.metodo_pagamento || 'Não informado',
            data_pagamento: p.data_pagamento || new Date().toISOString(),
            status: p.status || 'Pendente',
          }));
          setHistoricoPagamentos(historicoMapeado);
        } catch (error) {
          console.error('Erro ao carregar histórico de pagamentos:', error);
          setHistoricoPagamentos([]);
        }
        
        // Carregar resumo de vendas
        try {
          const resumo = await apiService.get(`/clientes/${clienteId}/resumo-vendas`);
          if (resumo?.data) {
            setResumoVendas(resumo.data);
          }
        } catch (error) {
          console.error('Erro ao carregar resumo de vendas:', error);
          setResumoVendas({
            quantidade_orcamentos: 0,
            total_vendas: 0,
            mes: 'N/A'
          });
        }
        
      } catch (error) {
        console.error('Erro ao carregar dados do cliente:', error);
        toast.error('Erro ao carregar dados do cliente');
        router.push('/dashboard/clientes');
      } finally {
        setLoading(false);
      }
    };

    loadClienteData();
  }, [params.id, getClienteById, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-500"></div>
        </div>
      </div>
    );
  }

  if (!cliente || !resumoVendas) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center py-12">
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
            Cliente não encontrado
          </h3>
          <div className="mt-6">
            <Link href="/dashboard/clientes">
              <Button>Voltar para Clientes</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

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
                <UserIcon className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {cliente.nome}
                  </h1>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Detalhes do cliente
                  </p>
                </div>
              </div>
              <Link href={`/dashboard/clientes/${cliente.id}/editar`}>
                <Button className="flex items-center space-x-2">
                  <PencilIcon className="h-5 w-5" />
                  <span>Editar</span>
                </Button>
              </Link>
            </div>
          </Header>

          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 dark:bg-gray-900 p-6">
            <ClienteDetalhes 
              cliente={cliente} 
              historicoPagamentos={historicoPagamentos}
              resumoVendas={resumoVendas}
            />
          </main>
        </div>
      </div>
    </div>
  );
}

export default function ClienteDetalhesPage() {
  return (
    <ClientLayout>
      <ClienteDetalhesPageContent />
    </ClientLayout>
  );
}