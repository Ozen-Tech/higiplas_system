'use client';

import { useState, useEffect } from 'react';
import { useClientesV2 } from '@/hooks/useClientesV2';
import { ClienteV2, ClienteUpdateV2 } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { X } from 'lucide-react';

interface ClienteEditModalProps {
  cliente: ClienteV2;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function ClienteEditModal({
  cliente,
  open,
  onClose,
  onSuccess,
}: ClienteEditModalProps) {
  const { updateCliente, loading } = useClientesV2();

  const [nome, setNome] = useState(cliente.nome);
  const [telefone, setTelefone] = useState(cliente.telefone);
  const [tipoPessoa, setTipoPessoa] = useState<'FISICA' | 'JURIDICA'>(cliente.tipo_pessoa);
  const [cpfCnpj, setCpfCnpj] = useState(cliente.cpf_cnpj || '');
  const [bairro, setBairro] = useState(cliente.bairro || '');
  const [cidade, setCidade] = useState(cliente.cidade || '');
  const [observacoes, setObservacoes] = useState(cliente.observacoes || '');
  const [referenciaLocalizacao, setReferenciaLocalizacao] = useState(cliente.referencia_localizacao || '');
  const [status, setStatus] = useState<'ATIVO' | 'INATIVO' | 'PROSPECTO'>(cliente.status);

  useEffect(() => {
    if (open) {
      setNome(cliente.nome);
      setTelefone(cliente.telefone);
      setTipoPessoa(cliente.tipo_pessoa);
      setCpfCnpj(cliente.cpf_cnpj || '');
      setBairro(cliente.bairro || '');
      setCidade(cliente.cidade || '');
      setObservacoes(cliente.observacoes || '');
      setReferenciaLocalizacao(cliente.referencia_localizacao || '');
      setStatus(cliente.status);
    }
  }, [open, cliente]);

  const handleSalvar = async () => {
    if (!nome || !telefone) {
      return;
    }

    const update: ClienteUpdateV2 = {
      nome,
      telefone,
      tipo_pessoa: tipoPessoa,
      cpf_cnpj: cpfCnpj || undefined,
      bairro: bairro || undefined,
      cidade: cidade || undefined,
      observacoes: observacoes || undefined,
      referencia_localizacao: referenciaLocalizacao || undefined,
      status,
    };

    try {
      await updateCliente(cliente.id, update);
      onSuccess();
    } catch (err) {
      console.error('Erro ao atualizar cliente:', err);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-800" onClick={(e) => e.stopPropagation()}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl">Editar Cliente #{cliente.id}</CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose} disabled={loading}>
            <X size={20} />
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <Label>Nome/Razão Social *</Label>
              <Input
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                placeholder="Nome completo ou razão social"
                className="mt-2"
                required
              />
            </div>
            <div>
              <Label>Telefone (WhatsApp) *</Label>
              <Input
                value={telefone}
                onChange={(e) => setTelefone(e.target.value)}
                placeholder="Ex: 98912345678"
                className="mt-2"
                required
              />
            </div>
            <div>
              <Label>Status</Label>
              <Select value={status} onValueChange={(v) => setStatus(v as 'ATIVO' | 'INATIVO' | 'PROSPECTO')}>
                <SelectTrigger className="mt-2">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ATIVO">Ativo</SelectItem>
                  <SelectItem value="INATIVO">Inativo</SelectItem>
                  <SelectItem value="PROSPECTO">Prospecto</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Tipo de Pessoa</Label>
              <Select value={tipoPessoa} onValueChange={(v) => setTipoPessoa(v as 'FISICA' | 'JURIDICA')}>
                <SelectTrigger className="mt-2">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="FISICA">Pessoa Física</SelectItem>
                  <SelectItem value="JURIDICA">Pessoa Jurídica</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>CPF/CNPJ</Label>
              <Input
                value={cpfCnpj}
                onChange={(e) => setCpfCnpj(e.target.value)}
                placeholder={tipoPessoa === 'FISICA' ? 'CPF' : 'CNPJ'}
                className="mt-2"
              />
            </div>
            <div>
              <Label>Bairro</Label>
              <Input
                value={bairro}
                onChange={(e) => setBairro(e.target.value)}
                placeholder="Bairro"
                className="mt-2"
              />
            </div>
            <div>
              <Label>Cidade</Label>
              <Input
                value={cidade}
                onChange={(e) => setCidade(e.target.value)}
                placeholder="Cidade"
                className="mt-2"
              />
            </div>
            <div className="md:col-span-2">
              <Label>Referência de Localização</Label>
              <Input
                value={referenciaLocalizacao}
                onChange={(e) => setReferenciaLocalizacao(e.target.value)}
                placeholder="Ponto de referência (ex: próximo ao mercado)"
                className="mt-2"
              />
            </div>
            <div className="md:col-span-2">
              <Label>Observações</Label>
              <textarea
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
                placeholder="Observações sobre o cliente"
                className="mt-2 w-full min-h-[100px] px-3 py-2 border rounded-md bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="outline" onClick={onClose} disabled={loading}>
              Cancelar
            </Button>
            <Button onClick={handleSalvar} disabled={loading || !nome || !telefone}>
              {loading ? 'Salvando...' : 'Salvar Alterações'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

