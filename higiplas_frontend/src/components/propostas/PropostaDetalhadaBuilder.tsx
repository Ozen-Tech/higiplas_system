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
import { FichaTecnica } from '@/services/propostaService';
import { Calculator, Save, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

export function PropostaDetalhadaBuilder() {
  const { clientes, produtos, buscarClientes, buscarProdutos, criarClienteCompleto, loading: vendasLoading } = useVendas();
  const { createProposta, calcularRendimento, calcularCustoPorLitro, loading } = usePropostaDetalhada();
  const { getFichaByProduto } = useFichasTecnicas();

  const [clienteSelecionado, setClienteSelecionado] = useState<Cliente | null>(null);
  const [produtoSelecionado, setProdutoSelecionado] = useState<Produto | null>(null);
  const [fichaTecnica, setFichaTecnica] = useState<FichaTecnica | null>(null);
  const [quantidade, setQuantidade] = useState<string>('1');
  const [dilucaoNumerador, setDilucaoNumerador] = useState<string>('');
  const [dilucaoDenominador, setDilucaoDenominador] = useState<string>('');
  const [rendimentoCalculado, setRendimentoCalculado] = useState<number | null>(null);
  const [custoPorLitro, setCustoPorLitro] = useState<number | null>(null);
  const [observacoes, setObservacoes] = useState<string>('');
  const [termoBuscaProduto, setTermoBuscaProduto] = useState<string>('');

  useEffect(() => {
    buscarClientes();
    buscarProdutos();
  }, [buscarClientes, buscarProdutos]);

  const produtosFiltrados = produtos.filter(p =>
    p.nome.toLowerCase().includes(termoBuscaProduto.toLowerCase()) ||
    p.codigo?.toLowerCase().includes(termoBuscaProduto.toLowerCase())
  );

  useEffect(() => {
    const carregarFichaTecnica = async () => {
      if (produtoSelecionado) {
        const ficha = await getFichaByProduto(produtoSelecionado.id);
        setFichaTecnica(ficha);
        
        // Preencher diluição da ficha técnica se disponível
        if (ficha?.dilucao_numerador && ficha?.dilucao_denominador) {
          setDilucaoNumerador(ficha.dilucao_numerador.toString());
          setDilucaoDenominador(ficha.dilucao_denominador.toString());
        }
      } else {
        setFichaTecnica(null);
      }
    };

    carregarFichaTecnica();
  }, [produtoSelecionado, getFichaByProduto]);

  useEffect(() => {
    // Recalcular rendimento quando quantidade ou diluição mudar
    const qtd = parseFloat(quantidade) || 0;
    const num = parseFloat(dilucaoNumerador) || null;
    const den = parseFloat(dilucaoDenominador) || null;

    if (qtd > 0 && num && den) {
      const rendimento = calcularRendimento(qtd, num, den);
      setRendimentoCalculado(rendimento);

      // Calcular custo por litro
      if (produtoSelecionado?.preco && rendimento) {
        const custo = calcularCustoPorLitro(produtoSelecionado.preco, qtd, rendimento);
        setCustoPorLitro(custo);
      }
    } else {
      setRendimentoCalculado(null);
      setCustoPorLitro(null);
    }
  }, [quantidade, dilucaoNumerador, dilucaoDenominador, produtoSelecionado, calcularRendimento, calcularCustoPorLitro]);

  const handleCriarProposta = async () => {
    if (!clienteSelecionado || !produtoSelecionado) {
      toast.error('Selecione um cliente e um produto');
      return;
    }

    const qtd = parseFloat(quantidade);
    if (!qtd || qtd <= 0) {
      toast.error('Informe uma quantidade válida');
      return;
    }

    const num = parseFloat(dilucaoNumerador);
    const den = parseFloat(dilucaoDenominador);
    
    if (!num || !den) {
      toast.error('Informe a diluição (ex: 1:10)');
      return;
    }

    try {
      await createProposta({
        cliente_id: clienteSelecionado.id,
        produto_id: produtoSelecionado.id,
        quantidade_produto: qtd,
        dilucao_aplicada: `${num}:${den}`,
        dilucao_numerador: num,
        dilucao_denominador: den,
        observacoes: observacoes || undefined,
        compartilhavel: false,
      });

      toast.success('Proposta detalhada criada com sucesso!');
      
      // Limpar formulário
      setClienteSelecionado(null);
      setProdutoSelecionado(null);
      setQuantidade('1');
      setDilucaoNumerador('');
      setDilucaoDenominador('');
      setObservacoes('');
      setRendimentoCalculado(null);
      setCustoPorLitro(null);
    } catch (error) {
      console.error('Erro ao criar proposta:', error);
      let errorMessage = 'Erro ao criar proposta';
      
      if (error instanceof Error) {
        errorMessage = error.message;
        // Extrair mensagem de erro da API se disponível
        if (error.message.includes('[') && error.message.includes(']')) {
          try {
            const match = error.message.match(/\[(\d+)\]\s*(.+)/);
            if (match) {
              errorMessage = match[2];
            }
          } catch {
            // Se não conseguir extrair, usar a mensagem original
          }
        }
      }
      
      toast.error(errorMessage);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Nova Proposta Detalhada</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Seleção de Cliente */}
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

          {/* Seleção de Produto */}
          <div>
            <Label>Produto Girassol</Label>
            {produtoSelecionado ? (
              <Card>
                <CardContent className="p-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-semibold">{produtoSelecionado.nome}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Cód: {produtoSelecionado.codigo || 'N/A'} | 
                        Estoque: {produtoSelecionado.estoque_disponivel} | 
                        Preço: R$ {produtoSelecionado.preco.toFixed(2)}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setProdutoSelecionado(null);
                        setTermoBuscaProduto('');
                      }}
                    >
                      ✕
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-2">
                <Input
                  placeholder="Buscar produto por nome ou código..."
                  value={termoBuscaProduto}
                  onChange={(e) => setTermoBuscaProduto(e.target.value)}
                />
                <div className="max-h-64 overflow-y-auto space-y-2 border rounded-lg p-2">
                  {produtosFiltrados.length === 0 ? (
                    <p className="text-center text-gray-500 dark:text-gray-400 py-4 text-sm">
                      {termoBuscaProduto ? 'Nenhum produto encontrado' : 'Digite para buscar produtos'}
                    </p>
                  ) : (
                    produtosFiltrados.slice(0, 20).map((produto) => (
                      <div
                        key={produto.id}
                        onClick={() => {
                          setProdutoSelecionado(produto);
                          setTermoBuscaProduto('');
                        }}
                        className="p-3 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
                      >
                        <p className="font-medium">{produto.nome}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Cód: {produto.codigo || 'N/A'} | 
                          Estoque: {produto.estoque_disponivel} | 
                          R$ {produto.preco.toFixed(2)}
                        </p>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Ficha Técnica */}
          {produtoSelecionado && (
            <FichaTecnicaCard ficha={fichaTecnica} />
          )}

          {/* Quantidade e Diluição */}
          {produtoSelecionado && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="quantidade">Quantidade do Produto</Label>
                <Input
                  id="quantidade"
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={quantidade}
                  onChange={(e) => setQuantidade(e.target.value)}
                  placeholder="Ex: 1"
                />
                <p className="text-xs text-gray-500 mt-1">Em litros ou unidades</p>
              </div>

              <div>
                <Label htmlFor="dilucao-num">Diluição - Parte 1</Label>
                <Input
                  id="dilucao-num"
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={dilucaoNumerador}
                  onChange={(e) => setDilucaoNumerador(e.target.value)}
                  placeholder="Ex: 1"
                />
              </div>

              <div>
                <Label htmlFor="dilucao-den">Diluição - Parte 2</Label>
                <Input
                  id="dilucao-den"
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={dilucaoDenominador}
                  onChange={(e) => setDilucaoDenominador(e.target.value)}
                  placeholder="Ex: 10"
                />
                <p className="text-xs text-gray-500 mt-1">Ex: 1:10 significa 1 parte para 10 partes</p>
              </div>
            </div>
          )}

          {/* Resultados do Cálculo */}
          {rendimentoCalculado !== null && (
            <Card className="bg-blue-50 dark:bg-blue-900/20">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Calculator className="h-5 w-5 text-blue-600" />
                  <h3 className="font-semibold">Resultados do Cálculo</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Rendimento Total</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {rendimentoCalculado.toFixed(2)} litros
                    </p>
                  </div>
                  {custoPorLitro !== null && (
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Custo por Litro Final</p>
                      <p className="text-2xl font-bold text-green-600">
                        R$ {custoPorLitro.toFixed(2)}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Observações */}
          <div>
            <Label htmlFor="observacoes">Observações (opcional)</Label>
            <textarea
              id="observacoes"
              className="w-full min-h-[100px] px-3 py-2 border rounded-md dark:bg-gray-800 dark:border-gray-700"
              value={observacoes}
              onChange={(e) => setObservacoes(e.target.value)}
              placeholder="Observações adicionais sobre a proposta..."
            />
          </div>

          {/* Botão Criar */}
          <Button
            onClick={handleCriarProposta}
            disabled={loading || !clienteSelecionado || !produtoSelecionado || !rendimentoCalculado}
            className="w-full"
            size="lg"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Criando...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Criar Proposta Detalhada
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

