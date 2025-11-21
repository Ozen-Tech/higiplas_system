'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, Search, Package, Plus, Trash2 } from 'lucide-react';
import { MotivoMovimentacao, MovimentacaoPendenteCreate, Product } from '@/types';
import { useMovimentacoesPendentes } from '@/hooks/useMovimentacoesPendentes';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';

interface ItemMovimentacao {
  id: string;
  produto: Product | null;
  termoBusca: string;
  produtosEncontrados: Product[];
  quantidade: string;
  searching: boolean;
}

export function RegistrarMovimentacaoForm() {
  const router = useRouter();
  const { criarMovimentacao } = useMovimentacoesPendentes();
  const [loading, setLoading] = useState(false);
  
  const [tipoMovimentacao, setTipoMovimentacao] = useState<'ENTRADA' | 'SAIDA'>('SAIDA');
  const [itens, setItens] = useState<ItemMovimentacao[]>([
    {
      id: '1',
      produto: null,
      termoBusca: '',
      produtosEncontrados: [],
      quantidade: '',
      searching: false,
    }
  ]);
  const [motivoMovimentacao, setMotivoMovimentacao] = useState<MotivoMovimentacao | ''>('');
  const [observacaoMotivo, setObservacaoMotivo] = useState('');
  const [observacao, setObservacao] = useState('');

  // Buscar produtos com debounce para cada item
  useEffect(() => {
    const timeouts: NodeJS.Timeout[] = [];
    
    itens.forEach(item => {
      if (item.termoBusca && item.termoBusca.length >= 2 && !item.produto) {
        const timeoutId = setTimeout(() => {
          buscarProdutos(item.termoBusca, item.id);
        }, 300);
        timeouts.push(timeoutId);
      }
    });

    return () => {
      timeouts.forEach(timeout => clearTimeout(timeout));
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itens.map(i => `${i.id}-${i.termoBusca}`).join(',')]);

  const buscarProdutos = async (termo: string, itemId: string) => {
    if (!termo || termo.trim().length < 2) {
      setItens(prev => prev.map(item => 
        item.id === itemId 
          ? { ...item, produtosEncontrados: [], searching: false }
          : item
      ));
      return;
    }

    setItens(prev => prev.map(item => 
      item.id === itemId ? { ...item, searching: true } : item
    ));

    try {
      const response = await apiService.get(`/produtos/buscar?q=${encodeURIComponent(termo.trim())}`);
      const produtos = (response?.data || []).map((p: Product) => ({
        id: p.id,
        nome: p.nome,
        codigo: p.codigo,
        categoria: p.categoria,
        quantidade_em_estoque: p.quantidade_em_estoque,
        unidade_medida: p.unidade_medida,
      }));
      
      setItens(prev => prev.map(item => 
        item.id === itemId 
          ? { ...item, produtosEncontrados: produtos, searching: false }
          : item
      ));
    } catch (error) {
      console.error('Erro ao buscar produtos:', error);
      toast.error('Erro ao buscar produtos');
      setItens(prev => prev.map(item => 
        item.id === itemId ? { ...item, searching: false } : item
      ));
    }
  };

  const adicionarItem = () => {
    const novoId = Date.now().toString();
    setItens(prev => [...prev, {
      id: novoId,
      produto: null,
      termoBusca: '',
      produtosEncontrados: [],
      quantidade: '',
      searching: false,
    }]);
  };

  const removerItem = (itemId: string) => {
    if (itens.length === 1) {
      toast.error('É necessário ter pelo menos um item');
      return;
    }
    setItens(prev => prev.filter(item => item.id !== itemId));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validar todos os itens
    const itensInvalidos = itens.filter(item => 
      !item.produto || !item.quantidade || parseFloat(item.quantidade) <= 0
    );

    if (itensInvalidos.length > 0) {
      toast.error('Preencha todos os produtos e quantidades corretamente');
      return;
    }

    if (!motivoMovimentacao) {
      toast.error('Selecione o motivo da movimentação');
      return;
    }

    setLoading(true);
    try {
      // Criar todas as movimentações
      const promessas = itens.map(item => {
        const movimentacao: MovimentacaoPendenteCreate = {
          produto_id: item.produto!.id,
          quantidade: parseFloat(item.quantidade),
          tipo_movimentacao: tipoMovimentacao,
          motivo_movimentacao: motivoMovimentacao as MotivoMovimentacao,
          observacao: observacao || null,
          observacao_motivo: observacaoMotivo || null,
        };
        return criarMovimentacao(movimentacao);
      });

      await Promise.all(promessas);
      toast.success(`${itens.length} movimentação(ões) registrada(s) com sucesso!`);
      
      router.push('/entregador/app');
    } catch (error) {
      console.error('Erro ao criar movimentações:', error);
    } finally {
      setLoading(false);
    }
  };

  const motivos = [
    { value: MotivoMovimentacao.CARREGAMENTO, label: 'Carregamento para entrega' },
    { value: MotivoMovimentacao.DEVOLUCAO, label: 'Devolução' },
    { value: MotivoMovimentacao.AJUSTE_FISICO, label: 'Ajuste físico' },
    { value: MotivoMovimentacao.PERDA_AVARIA, label: 'Perda/Avaria' },
    { value: MotivoMovimentacao.TRANSFERENCIA_INTERNA, label: 'Transferência interna' },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Package className="h-5 w-5" />
          Registrar Movimentação
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Tipo de Movimentação */}
          <div>
            <Label htmlFor="tipo">Tipo de Movimentação *</Label>
            <Select
              value={tipoMovimentacao}
              onValueChange={(value) => setTipoMovimentacao(value as 'ENTRADA' | 'SAIDA')}
            >
              <SelectTrigger id="tipo" className="h-11">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="SAIDA">Saída de Estoque</SelectItem>
                <SelectItem value="ENTRADA">Entrada de Estoque</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Itens */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label>Itens *</Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={adicionarItem}
                className="flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Adicionar Item
              </Button>
            </div>

            {itens.map((item, index) => (
              <Card key={item.id} className="p-4 border-2">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="font-medium text-gray-900 dark:text-gray-100">
                    Item {index + 1}
                  </h3>
                  {itens.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removerItem(item.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>

                <div className="space-y-4">
                  {/* Busca de Produto */}
                  <div>
                    <Label htmlFor={`produto-${item.id}`}>Produto *</Label>
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                      <Input
                        id={`produto-${item.id}`}
                        placeholder="Buscar por nome ou código..."
                        value={item.termoBusca}
                        onChange={(e) => {
                          const novoTermo = e.target.value;
                          setItens(prev => prev.map(i => {
                            if (i.id !== item.id) return i;
                            const updated = { ...i, termoBusca: novoTermo };
                            // Se o termo não corresponde ao produto selecionado, limpar seleção
                            if (i.produto && novoTermo !== i.produto.nome && novoTermo !== i.produto.codigo) {
                              updated.produto = null;
                            }
                            if (!novoTermo) {
                              updated.produto = null;
                              updated.produtosEncontrados = [];
                            }
                            return updated;
                          }));
                        }}
                        className="pl-10 h-11"
                      />
                    </div>
                    {item.searching && (
                      <div className="mt-2 flex items-center gap-2 text-sm text-gray-500">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Buscando...
                      </div>
                    )}
                    {/* Lista de produtos encontrados */}
                    {item.produtosEncontrados.length > 0 && (
                      <div className="mt-2 border rounded-lg max-h-48 overflow-y-auto bg-white dark:bg-gray-800 shadow-sm">
                        {item.produtosEncontrados.map((produto) => {
                          const isSelected = item.produto?.id === produto.id;
                          return (
                            <button
                              key={produto.id}
                              type="button"
                              onClick={() => {
                                setItens(prev => prev.map(i => 
                                  i.id === item.id 
                                    ? { ...i, produto, termoBusca: produto.nome, produtosEncontrados: [] }
                                    : i
                                ));
                              }}
                              className={`w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 border-b last:border-b-0 transition-colors ${
                                isSelected ? 'bg-blue-50 dark:bg-blue-900/30' : ''
                              }`}
                            >
                              <div className="font-medium flex items-center gap-2">
                                {produto.nome}
                                {isSelected && (
                                  <span className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded">Selecionado</span>
                                )}
                              </div>
                              <div className="text-sm text-gray-500 dark:text-gray-400">
                                Código: {produto.codigo} | Estoque: {produto.quantidade_em_estoque} {produto.unidade_medida}
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    )}
                    {/* Indicador de produto selecionado */}
                    {item.produto && (
                      <div className="mt-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="font-medium text-blue-900 dark:text-blue-100">{item.produto.nome}</div>
                            <div className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                              Código: {item.produto.codigo} | Estoque atual: {item.produto.quantidade_em_estoque} {item.produto.unidade_medida}
                            </div>
                          </div>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setItens(prev => prev.map(i => 
                                i.id === item.id 
                                  ? { ...i, produto: null, termoBusca: '', produtosEncontrados: [] }
                                  : i
                              ));
                            }}
                            className="ml-2"
                          >
                            Limpar
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Quantidade */}
                  <div>
                    <Label htmlFor={`quantidade-${item.id}`}>Quantidade *</Label>
                    <Input
                      id={`quantidade-${item.id}`}
                      type="number"
                      step="0.01"
                      min="0.01"
                      value={item.quantidade}
                      onChange={(e) => {
                        setItens(prev => prev.map(i => 
                          i.id === item.id ? { ...i, quantidade: e.target.value } : i
                        ));
                      }}
                      placeholder="0.00"
                      className="h-11"
                      required
                    />
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Motivo da Movimentação */}
          <div>
            <Label htmlFor="motivo">Motivo da Movimentação *</Label>
            <Select
              value={motivoMovimentacao}
              onValueChange={(value) => setMotivoMovimentacao(value as MotivoMovimentacao)}
            >
              <SelectTrigger id="motivo" className="h-11">
                <SelectValue placeholder="Selecione o motivo" />
              </SelectTrigger>
              <SelectContent>
                {motivos.map((motivo) => (
                  <SelectItem key={motivo.value} value={motivo.value}>
                    {motivo.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Observação do Motivo */}
          <div>
            <Label htmlFor="observacaoMotivo">Observações sobre o motivo (opcional)</Label>
            <Textarea
              id="observacaoMotivo"
              value={observacaoMotivo}
              onChange={(e) => setObservacaoMotivo(e.target.value)}
              placeholder="Detalhes adicionais sobre o motivo..."
              rows={2}
            />
          </div>

          {/* Observações Gerais */}
          <div>
            <Label htmlFor="observacao">Observações (opcional)</Label>
            <Textarea
              id="observacao"
              value={observacao}
              onChange={(e) => setObservacao(e.target.value)}
              placeholder="Observações adicionais..."
              rows={3}
            />
          </div>

          {/* Botões */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push('/entregador/app')}
              className="flex-1"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="flex-1"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Enviando...
                </>
              ) : (
                `Enviar ${itens.length} Registro(s)`
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
