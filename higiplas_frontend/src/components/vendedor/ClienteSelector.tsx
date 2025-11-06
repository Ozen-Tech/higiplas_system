'use client';

import { useState } from 'react';
import { Cliente } from '@/types/vendas';
import { ClienteV2 } from '@/types';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { UserPlus, Search, X } from 'lucide-react';

interface ClienteSelectorProps {
  clientes: Cliente[];
  clienteSelecionado: Cliente | null;
  onSelectCliente: (cliente: Cliente | null) => void;
  onCriarCliente: (nome: string, telefone: string, cnpj?: string, email?: string, endereco?: string, bairro?: string, cidade?: string) => Promise<ClienteV2 | null>;
  loading?: boolean;
}

export function ClienteSelector({
  clientes,
  clienteSelecionado,
  onSelectCliente,
  onCriarCliente,
  loading = false,
}: ClienteSelectorProps) {
  const [termoBusca, setTermoBusca] = useState('');
  const [modalAberto, setModalAberto] = useState(false);
  const [novoClienteNome, setNovoClienteNome] = useState('');
  const [novoClienteTelefone, setNovoClienteTelefone] = useState('');
  const [novoClienteCnpj, setNovoClienteCnpj] = useState('');
  const [novoClienteEmail, setNovoClienteEmail] = useState('');
  const [novoClienteEndereco, setNovoClienteEndereco] = useState('');
  const [novoClienteBairro, setNovoClienteBairro] = useState('');
  const [novoClienteCidade, setNovoClienteCidade] = useState('');

  const clientesFiltrados = clientes.filter(c =>
    c.nome.toLowerCase().includes(termoBusca.toLowerCase())
  );

  const handleCriarCliente = async () => {
    if (!novoClienteNome || !novoClienteTelefone) return;
    
    const novoCliente = await onCriarCliente(
      novoClienteNome,
      novoClienteTelefone,
      novoClienteCnpj,
      novoClienteEmail,
      novoClienteEndereco,
      novoClienteBairro,
      novoClienteCidade
    );

    if (novoCliente) {
      const clienteFormatado: Cliente = {
        id: novoCliente.id,
        nome: novoCliente.nome,
        telefone: novoCliente.telefone,
        bairro: novoCliente.bairro || null,
        cidade: novoCliente.cidade || null,
        ultima_compra: null,
      };
      onSelectCliente(clienteFormatado);
      setModalAberto(false);
      setNovoClienteNome('');
      setNovoClienteTelefone('');
      setNovoClienteCnpj('');
      setNovoClienteEmail('');
      setNovoClienteEndereco('');
      setNovoClienteBairro('');
      setNovoClienteCidade('');
    }
  };

  if (clienteSelecionado) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search size={20} /> Cliente Selecionado
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex justify-between items-center">
            <div>
              <p className="font-semibold">{clienteSelecionado.nome}</p>
              {clienteSelecionado.telefone && (
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {clienteSelecionado.telefone}
                </p>
              )}
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onSelectCliente(null)}
            >
              <X size={16} />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search size={20} /> Selecionar Cliente
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <Input
                placeholder="Buscar cliente..."
                value={termoBusca}
                onChange={(e) => setTermoBusca(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button
              onClick={() => setModalAberto(true)}
              className="gap-2"
              disabled={loading}
            >
              <UserPlus size={16} /> Novo
            </Button>
          </div>
          <div className="max-h-64 overflow-y-auto space-y-2">
            {clientesFiltrados.length === 0 ? (
              <p className="text-center text-gray-500 py-4">Nenhum cliente encontrado</p>
            ) : (
              clientesFiltrados.map((cliente) => (
                <div
                  key={cliente.id}
                  onClick={() => onSelectCliente(cliente)}
                  className="p-3 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                >
                  <p className="font-medium">{cliente.nome}</p>
                  {cliente.telefone && (
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {cliente.telefone}
                    </p>
                  )}
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {modalAberto && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserPlus size={20} /> Cadastrar Novo Cliente
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Nome/Razão Social *</label>
                  <Input
                    placeholder="Nome completo ou razão social"
                    value={novoClienteNome}
                    onChange={(e) => setNovoClienteNome(e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Telefone (WhatsApp) *</label>
                  <Input
                    placeholder="Ex: 98912345678"
                    value={novoClienteTelefone}
                    onChange={(e) => setNovoClienteTelefone(e.target.value)}
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">CNPJ/CPF</label>
                  <Input
                    placeholder="CNPJ ou CPF"
                    value={novoClienteCnpj}
                    onChange={(e) => setNovoClienteCnpj(e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Email</label>
                  <Input
                    type="email"
                    placeholder="cliente@exemplo.com"
                    value={novoClienteEmail}
                    onChange={(e) => setNovoClienteEmail(e.target.value)}
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Endereço</label>
                <Input
                  placeholder="Rua, número, complemento"
                  value={novoClienteEndereco}
                  onChange={(e) => setNovoClienteEndereco(e.target.value)}
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Bairro</label>
                  <Input
                    placeholder="Bairro"
                    value={novoClienteBairro}
                    onChange={(e) => setNovoClienteBairro(e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Cidade</label>
                  <Input
                    placeholder="Cidade"
                    value={novoClienteCidade}
                    onChange={(e) => setNovoClienteCidade(e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
            <div className="flex justify-end gap-4 p-6 pt-0">
              <Button
                variant="ghost"
                onClick={() => setModalAberto(false)}
              >
                Cancelar
              </Button>
              <Button
                onClick={handleCriarCliente}
                disabled={loading || !novoClienteNome || !novoClienteTelefone}
              >
                {loading ? 'Salvando...' : 'Salvar Cliente'}
              </Button>
            </div>
          </Card>
        </div>
      )}
    </>
  );
}

