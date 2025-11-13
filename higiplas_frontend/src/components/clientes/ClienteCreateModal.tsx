'use client';

import { useState } from 'react';
import { useClientesV2 } from '@/hooks/useClientesV2';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { X } from 'lucide-react';

interface ClienteCreateModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function ClienteCreateModal({
  open,
  onClose,
  onSuccess,
}: ClienteCreateModalProps) {
  const { createCliente, loading } = useClientesV2();

  const [nome, setNome] = useState('');
  const [telefone, setTelefone] = useState('');
  const [tipoPessoa, setTipoPessoa] = useState<'FISICA' | 'JURIDICA'>('FISICA');
  const [cpfCnpj, setCpfCnpj] = useState('');
  const [bairro, setBairro] = useState('');
  const [cidade, setCidade] = useState('');
  const [observacoes, setObservacoes] = useState('');
  const [referenciaLocalizacao, setReferenciaLocalizacao] = useState('');

  const handleSalvar = async () => {
    if (!nome || !telefone) {
      return;
    }

    try {
      await createCliente({
        nome,
        telefone,
        tipo_pessoa: tipoPessoa,
        cpf_cnpj: cpfCnpj || undefined,
        bairro: bairro || undefined,
        cidade: cidade || undefined,
        observacoes: observacoes || undefined,
        referencia_localizacao: referenciaLocalizacao || undefined,
      });
      onSuccess();
      // Limpar campos
      setNome('');
      setTelefone('');
      setTipoPessoa('FISICA');
      setCpfCnpj('');
      setBairro('');
      setCidade('');
      setObservacoes('');
      setReferenciaLocalizacao('');
    } catch (err) {
      console.error('Erro ao criar cliente:', err);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-800" onClick={(e) => e.stopPropagation()}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl">Novo Cliente</CardTitle>
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
              {loading ? 'Salvando...' : 'Salvar Cliente'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

