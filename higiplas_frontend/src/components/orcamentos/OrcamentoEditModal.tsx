'use client';

import { useState, useEffect, useMemo } from 'react';
import { Orcamento, OrcamentoUpdate, OrcamentoItemUpdate } from '@/types/orcamentos';
import { useOrcamentos } from '@/hooks/useOrcamentos';
import { useVendas } from '@/hooks/useVendas';
import { useClientesV2 } from '@/hooks/useClientesV2';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { X, Plus, Trash2, Search, PlusCircle } from 'lucide-react';
import toast from 'react-hot-toast';

interface OrcamentoEditModalProps {
  orcamento: Orcamento;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function OrcamentoEditModal({
  orcamento,
  open,
  onClose,
  onSuccess,
}: OrcamentoEditModalProps) {
  const { editarOrcamento, loading } = useOrcamentos();
  const { produtos, buscarProdutos } = useVendas();
  const { clientes, fetchClientes } = useClientesV2();

  const [clienteId, setClienteId] = useState(orcamento.cliente.id);
  const [condicaoPagamento, setCondicaoPagamento] = useState(orcamento.condicao_pagamento);
  const [status, setStatus] = useState(orcamento.status);
  const [itens, setItens] = useState<OrcamentoItemUpdate[]>(
    orcamento.itens.map(item => ({
      id: item.id,
      produto_id: item.produto.id,
      quantidade: item.quantidade,
      preco_unitario: item.preco_unitario_congelado,
    }))
  );
  const [buscaCliente, setBuscaCliente] = useState('');
  const [buscaProduto, setBuscaProduto] = useState('');
  const [isPersonalizadoModalOpen, setIsPersonalizadoModalOpen] = useState(false);
  const [novoItemNome, setNovoItemNome] = useState('');
  const [novoItemQuantidade, setNovoItemQuantidade] = useState(1);
  const [novoItemValor, setNovoItemValor] = useState(0);

  // Garantir que o cliente atual do orçamento esteja sempre na lista (Select exige valor válido)
  const clienteAtualParaSelect = useMemo(() => orcamento.cliente ? {
    id: orcamento.cliente.id,
    nome: orcamento.cliente.razao_social || (orcamento.cliente as { nome?: string }).nome || `Cliente #${orcamento.cliente.id}`,
    telefone: '',
    bairro: undefined,
    cidade: undefined,
    status: 'ATIVO',
    ultima_venda: undefined,
  } : null, [orcamento.cliente]);

  const clientesComAtual = useMemo(() => {
    if (!clienteAtualParaSelect) return clientes;
    const jaTem = clientes.some((c: { id: number }) => c.id === clienteAtualParaSelect.id);
    if (jaTem) return clientes;
    return [clienteAtualParaSelect, ...clientes];
  }, [clientes, clienteAtualParaSelect]);

  const clientesFiltrados = clientesComAtual.filter((c: { nome: string }) =>
    c.nome.toLowerCase().includes(buscaCliente.toLowerCase())
  );

  const produtosFiltrados = produtos.filter(p =>
    p.nome.toLowerCase().includes(buscaProduto.toLowerCase()) ||
    p.codigo?.toLowerCase().includes(buscaProduto.toLowerCase())
  );

  // Reinicializar itens quando o orcamento mudar ou quando o modal abrir
  useEffect(() => {
    if (open) {
      setClienteId(orcamento.cliente.id);
      setCondicaoPagamento(orcamento.condicao_pagamento);
      setStatus(orcamento.status);
      setItens(
        orcamento.itens.map(item => ({
          id: item.id,
          produto_id: item.produto.id,
          quantidade: item.quantidade,
          preco_unitario: item.preco_unitario_congelado,
        }))
      );
      fetchClientes({ limit: 200 });
      buscarProdutos();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, orcamento.id]);

  const handleSalvar = async () => {
    // Preparar itens para envio
    const itensParaEnviar: OrcamentoItemUpdate[] = itens.map(item => {
      const itemUpdate: OrcamentoItemUpdate = {
        quantidade: item.quantidade,
        preco_unitario: item.preco_unitario,
      };
      
      // Se tem nome_produto_personalizado, enviar isso ao invés de produto_id
      if (item.nome_produto_personalizado) {
        itemUpdate.nome_produto_personalizado = item.nome_produto_personalizado;
      } else if (item.produto_id) {
        itemUpdate.produto_id = item.produto_id;
      }
      
      // Manter id se existir (para itens existentes)
      if (item.id) {
        itemUpdate.id = item.id;
      }
      
      return itemUpdate;
    });

    const update: OrcamentoUpdate = {
      cliente_id: clienteId !== orcamento.cliente.id ? clienteId : undefined,
      condicao_pagamento: condicaoPagamento !== orcamento.condicao_pagamento ? condicaoPagamento : undefined,
      status: status !== orcamento.status ? status : undefined,
      itens: itensParaEnviar,
    };

    const resultado = await editarOrcamento(orcamento.id, update);
    if (resultado) {
      onSuccess();
    }
  };

  const handleAdicionarItem = () => {
    if (produtos.length === 0) {
      toast.error('Carregue os produtos primeiro');
      return;
    }
    const primeiroProduto = produtos[0];
    setItens([...itens, {
      produto_id: primeiroProduto.id,
      quantidade: 1,
      preco_unitario: primeiroProduto.preco,
    }]);
  };

  const handleAdicionarItemPersonalizado = () => {
    if (!novoItemNome || novoItemQuantidade <= 0 || novoItemValor <= 0) {
      toast.error('Preencha todos os campos corretamente.');
      return;
    }

    // Para itens personalizados, precisamos criar o produto primeiro no backend
    // Por enquanto, vamos adicionar um item temporário que será tratado no backend
    // O backend criará o produto automaticamente quando o orçamento for atualizado
    const novoItem: OrcamentoItemUpdate = {
      quantidade: novoItemQuantidade,
      preco_unitario: novoItemValor,
      nome_produto_personalizado: novoItemNome,
    };
    setItens([...itens, novoItem]);
    
    setNovoItemNome('');
    setNovoItemQuantidade(1);
    setNovoItemValor(0);
    setIsPersonalizadoModalOpen(false);
    toast.success('Item personalizado adicionado!');
  };

  const handleRemoverItem = (index: number) => {
    setItens(itens.filter((_, i) => i !== index));
  };

  const handleAtualizarItem = (index: number, campo: 'produto_id' | 'quantidade' | 'preco_unitario' | 'nome_produto_personalizado', valor: number | string) => {
    setItens(prevItens => {
      const novosItens = [...prevItens];
      novosItens[index] = {
        ...novosItens[index],
        [campo]: valor,
      };
      return novosItens;
    });
  };

  const calcularTotal = () => {
    return itens.reduce((acc, item) => acc + (item.quantidade * item.preco_unitario), 0);
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-800" onClick={(e) => e.stopPropagation()}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl">Editar Orçamento #{orcamento.id}</CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose} disabled={loading}>
            <X size={20} />
          </Button>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Cliente */}
          <div>
            <Label>Cliente</Label>
            <div className="mt-2 space-y-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <Input
                  placeholder="Buscar cliente..."
                  value={buscaCliente}
                  onChange={(e) => setBuscaCliente(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={clienteId.toString()} onValueChange={(v) => setClienteId(parseInt(v))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {clientesFiltrados.map(cliente => (
                    <SelectItem key={cliente.id} value={cliente.id.toString()}>
                      {cliente.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Condição de Pagamento e Status */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Condição de Pagamento</Label>
              <Select value={condicaoPagamento} onValueChange={setCondicaoPagamento}>
                <SelectTrigger className="mt-2">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="À vista">À vista</SelectItem>
                  <SelectItem value="7 dias">7 dias</SelectItem>
                  <SelectItem value="14 dias">14 dias</SelectItem>
                  <SelectItem value="21 dias">21 dias</SelectItem>
                  <SelectItem value="30 dias">30 dias</SelectItem>
                  <SelectItem value="45 dias">45 dias</SelectItem>
                  <SelectItem value="60 dias">60 dias</SelectItem>
                  <SelectItem value="90 dias">90 dias</SelectItem>
                  <SelectItem value="30/60 dias">30/60 dias</SelectItem>
                  <SelectItem value="30/60/90 dias">30/60/90 dias</SelectItem>
                  <SelectItem value="Entrada + 30 dias">Entrada + 30 dias</SelectItem>
                  <SelectItem value="Entrada + 60 dias">Entrada + 60 dias</SelectItem>
                  <SelectItem value="Boleto 30 dias">Boleto 30 dias</SelectItem>
                  <SelectItem value="Boleto 60 dias">Boleto 60 dias</SelectItem>
                  <SelectItem value="Cheque 30 dias">Cheque 30 dias</SelectItem>
                  <SelectItem value="Cheque 60 dias">Cheque 60 dias</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Status</Label>
              <Select value={status} onValueChange={setStatus}>
                <SelectTrigger className="mt-2">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="RASCUNHO">Rascunho</SelectItem>
                  <SelectItem value="ENVIADO">Enviado</SelectItem>
                  <SelectItem value="APROVADO">Aprovado</SelectItem>
                  <SelectItem value="REJEITADO">Rejeitado</SelectItem>
                  <SelectItem value="FINALIZADO">Finalizado</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Itens */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <Label className="text-lg">Itens do Orçamento</Label>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={handleAdicionarItem}>
                  <Plus size={16} className="mr-2" />
                  Adicionar Item
                </Button>
                <Button variant="default" size="sm" onClick={() => setIsPersonalizadoModalOpen(true)}>
                  <PlusCircle size={16} className="mr-2" />
                  Novo Produto
                </Button>
              </div>
            </div>
            <div className="mb-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <Input
                  placeholder="Buscar produto..."
                  value={buscaProduto}
                  onChange={(e) => setBuscaProduto(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="space-y-3">
              {itens.map((item, index) => {
                const itemKey = item.id ? `item-${item.id}` : `item-${item.produto_id || item.nome_produto_personalizado || index}-${index}`;
                const isPersonalizado = !item.produto_id && !!item.nome_produto_personalizado;
                
                return (
                  <div key={itemKey} className="border rounded-lg p-4 space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                      <div className="md:col-span-2">
                        <Label>Produto</Label>
                        {isPersonalizado ? (
                          <div className="space-y-2">
                            <Input
                              value={item.nome_produto_personalizado || ''}
                              onChange={(e) => {
                                handleAtualizarItem(index, 'nome_produto_personalizado', e.target.value);
                              }}
                              placeholder="Nome do produto personalizado"
                            />
                            <span className="text-xs text-blue-600 dark:text-blue-400">Novo Produto</span>
                          </div>
                        ) : (
                          <Select
                            key={`select-${itemKey}-${item.produto_id}`}
                            value={item.produto_id?.toString() || ''}
                            onValueChange={(v) => {
                              const produtoSelecionado = produtos.find(p => p.id === parseInt(v));
                              if (produtoSelecionado) {
                                handleAtualizarItem(index, 'produto_id', produtoSelecionado.id);
                                handleAtualizarItem(index, 'preco_unitario', produtoSelecionado.preco);
                              }
                            }}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione um produto" />
                            </SelectTrigger>
                            <SelectContent>
                              {produtosFiltrados.map(prod => (
                                <SelectItem key={prod.id} value={prod.id.toString()}>
                                  {prod.nome} ({prod.codigo})
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        )}
                      </div>
                      <div>
                        <Label>Quantidade</Label>
                        <Input
                          type="number"
                          min="1"
                          value={item.quantidade}
                          onChange={(e) => handleAtualizarItem(index, 'quantidade', parseInt(e.target.value) || 1)}
                        />
                      </div>
                      <div>
                        <Label>Preço Unitário</Label>
                        <Input
                          type="number"
                          step="0.01"
                          min="0"
                          value={item.preco_unitario}
                          onChange={(e) => handleAtualizarItem(index, 'preco_unitario', parseFloat(e.target.value) || 0)}
                        />
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <div>
                        <span className="text-sm text-gray-500 dark:text-gray-400">Subtotal: </span>
                        <span className="font-semibold">
                          R$ {(item.quantidade * item.preco_unitario).toFixed(2)}
                        </span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoverItem(index)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 size={16} />
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
            {itens.length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-semibold">Total:</span>
                  <span className="text-2xl font-bold text-green-600 dark:text-green-400">
                    R$ {calcularTotal().toFixed(2)}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Ações */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="outline" onClick={onClose} disabled={loading}>
              Cancelar
            </Button>
            <Button onClick={handleSalvar} disabled={loading || itens.length === 0}>
              {loading ? 'Salvando...' : 'Salvar Alterações'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Modal de Item Personalizado */}
      {isPersonalizadoModalOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-[60] p-4" onClick={() => setIsPersonalizadoModalOpen(false)}>
          <Card className="w-full max-w-md bg-white dark:bg-gray-800" onClick={(e) => e.stopPropagation()}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PlusCircle /> Adicionar Item Personalizado
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Este produto será criado automaticamente no sistema quando o orçamento for salvo.
              </p>
              <div>
                <Label>Nome do Produto *</Label>
                <Input
                  placeholder="Ex: Produto especial sob medida"
                  value={novoItemNome}
                  onChange={(e) => setNovoItemNome(e.target.value)}
                  className="mt-2"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Quantidade *</Label>
                  <Input
                    type="number"
                    min="1"
                    value={novoItemQuantidade}
                    onChange={(e) => setNovoItemQuantidade(parseInt(e.target.value) || 1)}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label>Valor Unitário (R$) *</Label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    value={novoItemValor}
                    onChange={(e) => setNovoItemValor(parseFloat(e.target.value) || 0)}
                    className="mt-2"
                  />
                </div>
              </div>
            </CardContent>
            <div className="flex justify-end gap-4 p-6 pt-0">
              <Button variant="ghost" onClick={() => {
                setIsPersonalizadoModalOpen(false);
                setNovoItemNome('');
                setNovoItemQuantidade(1);
                setNovoItemValor(0);
              }}>
                Cancelar
              </Button>
              <Button onClick={handleAdicionarItemPersonalizado}>
                Adicionar
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

