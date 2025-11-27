// src/components/propostas/PropostaDetalhadaBuilder.tsx

'use client';

import { useState, useEffect } from 'react';
import { usePropostaDetalhada } from '@/hooks/usePropostaDetalhada';
import { useFichasTecnicas } from '@/hooks/useFichasTecnicas';
import { useVendas } from '@/hooks/useVendas';
import { FichaTecnicaCard } from './FichaTecnicaCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ClienteSelector } from '@/components/vendedor/ClienteSelector';
import { Cliente, Produto } from '@/types/vendas';
import { FichaTecnica, PropostaDetalhadaItemCreatePayload, ComparacaoConcorrenteManualCreate } from '@/services/propostaService';
import { Calculator, Save, Loader2, Plus, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

export function PropostaDetalhadaBuilder() {
  const { clientes, produtos, buscarClientes, buscarProdutos, criarClienteCompleto, loading: vendasLoading } = useVendas();
  const { createProposta, calcularRendimento, calcularCustoPorLitro, loading } = usePropostaDetalhada();
  const { getFichaByProduto } = useFichasTecnicas();

  type ItemFormState = {
    produto: Produto | null;
    quantidade: string;
    dilucaoNumerador: string;
    dilucaoDenominador: string;
    observacoes: string;
    fichaTecnica: FichaTecnica | null;
    rendimentoCalculado: number | null;
    custoPorLitro: number | null;
    concorrenteNomeManual: string;
    concorrenteRendimentoManual: string;
    concorrenteCustoPorLitroManual: string;
  };

  const criarItemVazio = (): ItemFormState => ({
    produto: null,
    quantidade: '1',
    dilucaoNumerador: '',
    dilucaoDenominador: '',
    observacoes: '',
    fichaTecnica: null,
    rendimentoCalculado: null,
    custoPorLitro: null,
    concorrenteNomeManual: '',
    concorrenteRendimentoManual: '',
    concorrenteCustoPorLitroManual: '',
  });

  const [clienteSelecionado, setClienteSelecionado] = useState<Cliente | null>(null);
  const [itens, setItens] = useState<ItemFormState[]>([criarItemVazio()]);
  const [observacoes, setObservacoes] = useState<string>('');
  const [mostrarComparacaoManual, setMostrarComparacaoManual] = useState(false);
  const [comparacoesManuais, setComparacoesManuais] = useState<ComparacaoConcorrenteManualCreate[]>([
    { nome: '', rendimento_litro: undefined, custo_por_litro: undefined, observacoes: '' },
  ]);

  useEffect(() => {
    buscarClientes();
    buscarProdutos();
  }, [buscarClientes, buscarProdutos]);

  const atualizarItem = (index: number, updates: Partial<ItemFormState>) => {
    setItens((prev) => {
      const novos = [...prev];
      const atualizado = { ...novos[index], ...updates };

      const qtd = parseFloat(atualizado.quantidade) || 0;
      const num = parseFloat(atualizado.dilucaoNumerador) || undefined;
      const den = parseFloat(atualizado.dilucaoDenominador) || undefined;

      if (atualizado.produto && qtd > 0 && num && den) {
        const rendimento = calcularRendimento(qtd, num, den);
        atualizado.rendimentoCalculado = rendimento ?? null;
        if (atualizado.produto.preco && rendimento) {
          atualizado.custoPorLitro = calcularCustoPorLitro(
            atualizado.produto.preco,
            qtd,
            rendimento
          ) ?? null;
        } else {
          atualizado.custoPorLitro = null;
        }
      } else {
        atualizado.rendimentoCalculado = null;
        atualizado.custoPorLitro = null;
      }

      novos[index] = atualizado;
      return novos;
    });
  };

  const selecionarProduto = async (index: number, produtoId: string) => {
    const produto = produtos.find((p) => p.id === Number(produtoId)) || null;
    atualizarItem(index, { produto });

    if (produto) {
      const ficha = await getFichaByProduto(produto.id);
      atualizarItem(index, {
        fichaTecnica: ficha,
        dilucaoNumerador: ficha?.dilucao_numerador ? ficha.dilucao_numerador.toString() : '',
        dilucaoDenominador: ficha?.dilucao_denominador ? ficha.dilucao_denominador.toString() : '',
      });
    } else {
      atualizarItem(index, { fichaTecnica: null });
    }
  };

  const adicionarItem = () => {
    setItens((prev) => [...prev, criarItemVazio()]);
  };

  const removerItem = (index: number) => {
    setItens((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleComparacaoManualChange = (index: number, campo: keyof ComparacaoConcorrenteManualCreate, valor: string) => {
    setComparacoesManuais((prev) => {
      const copia = [...prev];
      const atualizado = { ...copia[index] };
      
      // Campos numéricos
      if (campo === 'rendimento_litro') {
        atualizado.rendimento_litro = valor ? Number(valor) : undefined;
      } else if (campo === 'custo_por_litro') {
        atualizado.custo_por_litro = valor ? Number(valor) : undefined;
      } else if (campo === 'ordem') {
        atualizado.ordem = valor ? Number(valor) : undefined;
      } 
      // Campos string
      else if (campo === 'nome') {
        atualizado.nome = valor;
      } else if (campo === 'observacoes') {
        atualizado.observacoes = valor;
      }
      
      copia[index] = atualizado;
      return copia;
    });
  };

  const adicionarComparacaoManual = () => {
    setComparacoesManuais((prev) => [...prev, { nome: '', rendimento_litro: undefined, custo_por_litro: undefined, observacoes: '' }]);
  };

  const removerComparacaoManual = (index: number) => {
    setComparacoesManuais((prev) => prev.filter((_, idx) => idx !== index));
  };

  const itensValidos = itens.every((item) => {
    const qtd = parseFloat(item.quantidade);
    const num = parseFloat(item.dilucaoNumerador);
    const den = parseFloat(item.dilucaoDenominador);
    return item.produto && qtd > 0 && num > 0 && den > 0;
  });

  const handleCriarProposta = async () => {
    if (!clienteSelecionado) {
      toast.error('Selecione um cliente');
      return;
    }

    if (!itensValidos) {
      toast.error('Preencha todos os itens com produto, quantidade e diluição válidos');
      return;
    }

    const payloadItens: PropostaDetalhadaItemCreatePayload[] = itens.map((item, index) => {
      const quantidade = parseFloat(item.quantidade);
      const num = parseFloat(item.dilucaoNumerador);
      const den = parseFloat(item.dilucaoDenominador);

      return {
        produto_id: item.produto!.id,
        quantidade_produto: quantidade,
        dilucao_aplicada: `${num}:${den}`,
        dilucao_numerador: num,
        dilucao_denominador: den,
        observacoes: item.observacoes || undefined,
        ordem: index + 1,
        concorrente_nome_manual: item.concorrenteNomeManual || undefined,
        concorrente_rendimento_manual: item.concorrenteRendimentoManual ? Number(item.concorrenteRendimentoManual) : undefined,
        concorrente_custo_por_litro_manual: item.concorrenteCustoPorLitroManual ? Number(item.concorrenteCustoPorLitroManual) : undefined,
      };
    });

    try {
      await createProposta({
        cliente_id: clienteSelecionado.id,
        observacoes: observacoes || undefined,
        compartilhavel: false,
        itens: payloadItens,
        comparacoes_personalizadas: mostrarComparacaoManual
          ? comparacoesManuais.filter((comp) => comp.nome?.trim())
          : undefined,
      });

      toast.success('Proposta detalhada criada com sucesso!');
      setClienteSelecionado(null);
      setItens([criarItemVazio()]);
      setObservacoes('');
      setMostrarComparacaoManual(false);
      setComparacoesManuais([{ nome: '', rendimento_litro: undefined, custo_por_litro: undefined, observacoes: '' }]);
    } catch (error) {
      console.error('Erro ao criar proposta:', error);
      let errorMessage = 'Erro ao criar proposta';
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      toast.error(errorMessage);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Dados gerais</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label>Cliente</Label>
            <ClienteSelector
              clientes={clientes}
              clienteSelecionado={clienteSelecionado}
              onSelectCliente={setClienteSelecionado}
              onCriarCliente={criarClienteCompleto}
              loading={vendasLoading}
            />
          </div>

          <div>
            <Label htmlFor="observacoes">Observações gerais</Label>
            <textarea
              id="observacoes"
              className="w-full min-h-[80px] px-3 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700"
              value={observacoes}
              onChange={(e) => setObservacoes(e.target.value)}
              placeholder="Destacar benefícios, instruções de aplicação ou condições especiais."
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <CardTitle>Produtos Higiplas incluídos</CardTitle>
          <Button variant="outline" onClick={adicionarItem}>
            <Plus className="mr-2 h-4 w-4" />
            Adicionar produto
          </Button>
        </CardHeader>
        <CardContent className="space-y-6">
          {itens.map((item, index) => (
            <Card key={index} className="border-blue-100 shadow-sm">
              <CardHeader className="flex flex-row items-center justify-between gap-4 py-4">
                <div>
                  <p className="font-semibold">
                    Produto #{index + 1}{' '}
                    {item.produto ? `- ${item.produto.nome}` : ''}
                  </p>
                  <p className="text-xs text-gray-500">
                    Informe o produto, diluição e rendimento para gerar a proposta.
                  </p>
                </div>
                {itens.length > 1 && (
                  <Button variant="ghost" size="sm" onClick={() => removerItem(index)}>
                    <Trash2 className="h-4 w-4 text-red-500" />
                    <span className="sr-only">Remover item</span>
                  </Button>
                )}
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Produto</Label>
                    <select
                      className="w-full border rounded-md px-3 py-2 dark:bg-gray-800 dark:border-gray-700"
                      value={item.produto?.id ?? ''}
                      onChange={(e) => selecionarProduto(index, e.target.value)}
                    >
                      <option value="">Selecione um produto</option>
                      {produtos.map((produto) => (
                        <option key={produto.id} value={produto.id}>
                          {produto.nome} (R$ {produto.preco.toFixed(2)})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <Label>Observações do item (opcional)</Label>
                    <Input
                      value={item.observacoes}
                      onChange={(e) => atualizarItem(index, { observacoes: e.target.value })}
                      placeholder="Ex: Limpeza pesada, cozinha industrial"
                    />
                  </div>
                </div>

                {item.fichaTecnica && <FichaTecnicaCard ficha={item.fichaTecnica} />}

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <Label>Quantidade</Label>
                    <Input
                      type="number"
                      min="0.1"
                      step="0.1"
                      value={item.quantidade}
                      onChange={(e) => atualizarItem(index, { quantidade: e.target.value })}
                      placeholder="Ex: 2"
                    />
                    <p className="text-xs text-gray-500 mt-1">Litros ou unidades</p>
                  </div>
                  <div>
                    <Label>Diluição - parte 1</Label>
                    <Input
                      type="number"
                      min="0.1"
                      step="0.1"
                      value={item.dilucaoNumerador}
                      onChange={(e) => atualizarItem(index, { dilucaoNumerador: e.target.value })}
                      placeholder="Ex: 1"
                    />
                  </div>
                  <div>
                    <Label>Diluição - parte 2</Label>
                    <Input
                      type="number"
                      min="0.1"
                      step="0.1"
                      value={item.dilucaoDenominador}
                      onChange={(e) => atualizarItem(index, { dilucaoDenominador: e.target.value })}
                      placeholder="Ex: 10"
                    />
                    <p className="text-xs text-gray-500 mt-1">1:10 = 1 parte para 10 partes</p>
                  </div>
                  <div>
                    <Label>Concorrente (nome)</Label>
                    <Input
                      value={item.concorrenteNomeManual}
                      onChange={(e) => atualizarItem(index, { concorrenteNomeManual: e.target.value })}
                      placeholder="Produto do cliente"
                    />
                    <p className="text-xs text-gray-500 mt-1">Opcional por item</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label>Rendimento concorrente (L)</Label>
                    <Input
                      type="number"
                      min="0"
                      step="0.1"
                      value={item.concorrenteRendimentoManual}
                      onChange={(e) => atualizarItem(index, { concorrenteRendimentoManual: e.target.value })}
                      placeholder="Ex: 30"
                    />
                  </div>
                  <div>
                    <Label>Custo concorrente por litro</Label>
                    <Input
                      type="number"
                      min="0"
                      step="0.1"
                      value={item.concorrenteCustoPorLitroManual}
                      onChange={(e) => atualizarItem(index, { concorrenteCustoPorLitroManual: e.target.value })}
                      placeholder="Ex: 2.5"
                    />
                  </div>
                </div>

                {item.rendimentoCalculado !== null && (
                  <Card className="bg-blue-50 dark:bg-blue-900/20">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <Calculator className="h-5 w-5 text-blue-600" />
                        <h3 className="font-semibold">Resultados do item</h3>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Rendimento total</p>
                          <p className="text-2xl font-bold text-blue-600">
                            {item.rendimentoCalculado.toFixed(2)} litros
                          </p>
                        </div>
                        {item.custoPorLitro !== null && (
                          <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Custo final por litro</p>
                            <p className="text-2xl font-bold text-green-600">
                              R$ {item.custoPorLitro.toFixed(2)}
                            </p>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </CardContent>
            </Card>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Comparação rápida com concorrentes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <label className="flex items-center gap-2 text-sm font-medium">
            <input
              type="checkbox"
              checked={mostrarComparacaoManual}
              onChange={(e) => setMostrarComparacaoManual(e.target.checked)}
            />
            Incluir tabela de produtos concorrentes do cliente
          </label>

          {mostrarComparacaoManual && (
            <div className="space-y-4">
              {comparacoesManuais.map((comparacao, index) => (
                <Card key={index}>
                  <CardHeader className="flex flex-row items-center justify-between py-3">
                    <p className="font-semibold">Concorrente #{index + 1}</p>
                    {comparacoesManuais.length > 1 && (
                      <Button variant="ghost" size="sm" onClick={() => removerComparacaoManual(index)}>
                        <Trash2 className="h-4 w-4 text-red-500" />
                        <span className="sr-only">Remover concorrente</span>
                      </Button>
                    )}
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <div>
                        <Label>Nome do produto</Label>
                        <Input
                          value={comparacao.nome}
                          onChange={(e) => handleComparacaoManualChange(index, 'nome', e.target.value)}
                          placeholder="Produto que o cliente utiliza"
                        />
                      </div>
                      <div>
                        <Label>Rendimento (L)</Label>
                        <Input
                          type="number"
                          min="0"
                          step="0.1"
                          value={comparacao.rendimento_litro ?? ''}
                          onChange={(e) => handleComparacaoManualChange(index, 'rendimento_litro', e.target.value)}
                          placeholder="Ex: 30"
                        />
                      </div>
                      <div>
                        <Label>Custo por litro</Label>
                        <Input
                          type="number"
                          min="0"
                          step="0.1"
                          value={comparacao.custo_por_litro ?? ''}
                          onChange={(e) => handleComparacaoManualChange(index, 'custo_por_litro', e.target.value)}
                          placeholder="Ex: 2.40"
                        />
                      </div>
                    </div>
                    <div>
                      <Label>Observações (opcional)</Label>
                      <Input
                        value={comparacao.observacoes ?? ''}
                        onChange={(e) => handleComparacaoManualChange(index, 'observacoes', e.target.value)}
                        placeholder="Diferenciais ou alertas"
                      />
                    </div>
                  </CardContent>
                </Card>
              ))}

              <Button variant="outline" onClick={adicionarComparacaoManual}>
                <Plus className="mr-2 h-4 w-4" />
                Adicionar concorrente
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Button
        onClick={handleCriarProposta}
        disabled={loading || !clienteSelecionado || !itensValidos}
        className="w-full"
        size="lg"
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Gerando proposta...
          </>
        ) : (
          <>
            <Save className="mr-2 h-4 w-4" />
            Gerar proposta detalhada em PDF
          </>
        )}
      </Button>
    </div>
  );
}

