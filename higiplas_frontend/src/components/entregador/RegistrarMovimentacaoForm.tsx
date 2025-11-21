'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, Search, Package } from 'lucide-react';
import { MotivoMovimentacao, MovimentacaoPendenteCreate, Product } from '@/types';
import { useMovimentacoesPendentes } from '@/hooks/useMovimentacoesPendentes';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';

export function RegistrarMovimentacaoForm() {
  const router = useRouter();
  const { criarMovimentacao } = useMovimentacoesPendentes();
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  
  const [tipoMovimentacao, setTipoMovimentacao] = useState<'ENTRADA' | 'SAIDA'>('SAIDA');
  const [produtoSelecionado, setProdutoSelecionado] = useState<Product | null>(null);
  const [termoBusca, setTermoBusca] = useState('');
  const [produtosEncontrados, setProdutosEncontrados] = useState<Product[]>([]);
  const [quantidade, setQuantidade] = useState('');
  const [motivoMovimentacao, setMotivoMovimentacao] = useState<MotivoMovimentacao | ''>('');
  const [observacaoMotivo, setObservacaoMotivo] = useState('');
  const [observacao, setObservacao] = useState('');

  const buscarProdutos = async (termo: string) => {
    if (!termo || termo.trim().length < 2) {
      setProdutosEncontrados([]);
      return;
    }

    setSearching(true);
    try {
      const response = await apiService.get(`/produtos/buscar/?q=${encodeURIComponent(termo.trim())}`);
      const produtos = (response?.data || []).map((p: Product) => ({
        id: p.id,
        nome: p.nome,
        codigo: p.codigo,
        categoria: p.categoria,
        quantidade_em_estoque: p.quantidade_em_estoque,
        unidade_medida: p.unidade_medida,
      }));
      setProdutosEncontrados(produtos);
    } catch (error) {
      console.error('Erro ao buscar produtos:', error);
      toast.error('Erro ao buscar produtos');
    } finally {
      setSearching(false);
    }
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (termoBusca) {
        buscarProdutos(termoBusca);
      } else {
        setProdutosEncontrados([]);
        // Não limpar produto selecionado automaticamente quando o campo está vazio
      }
    }, 300);

    return () => clearTimeout(timeoutId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [termoBusca]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!produtoSelecionado) {
      toast.error('Selecione um produto');
      return;
    }

    if (!quantidade || parseFloat(quantidade) <= 0) {
      toast.error('Informe uma quantidade válida');
      return;
    }

    if (!motivoMovimentacao) {
      toast.error('Selecione o motivo da movimentação');
      return;
    }

    setLoading(true);
    try {
      const movimentacao: MovimentacaoPendenteCreate = {
        produto_id: produtoSelecionado.id,
        quantidade: parseFloat(quantidade),
        tipo_movimentacao: tipoMovimentacao,
        motivo_movimentacao: motivoMovimentacao as MotivoMovimentacao,
        observacao: observacao || null,
        observacao_motivo: observacaoMotivo || null,
      };

      await criarMovimentacao(movimentacao);
      
      // Limpar formulário
      setProdutoSelecionado(null);
      setTermoBusca('');
      setQuantidade('');
      setMotivoMovimentacao('');
      setObservacaoMotivo('');
      setObservacao('');
      
      router.push('/entregador/app');
    } catch (error) {
      console.error('Erro ao criar movimentação:', error);
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
        <form onSubmit={handleSubmit} className="space-y-4">
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

          {/* Busca de Produto */}
          <div>
            <Label htmlFor="produto">Produto *</Label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <Input
                id="produto"
                placeholder="Buscar por nome ou código..."
                value={termoBusca}
                onChange={(e) => {
                  const novoTermo = e.target.value;
                  setTermoBusca(novoTermo);
                  // Se o usuário está editando e o termo não corresponde ao produto selecionado, limpar seleção
                  if (produtoSelecionado && novoTermo !== produtoSelecionado.nome && novoTermo !== produtoSelecionado.codigo) {
                    setProdutoSelecionado(null);
                  }
                  if (!novoTermo) {
                    setProdutoSelecionado(null);
                    setProdutosEncontrados([]);
                  }
                }}
                className="pl-10 h-11"
              />
            </div>
            {searching && (
              <div className="mt-2 flex items-center gap-2 text-sm text-gray-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                Buscando...
              </div>
            )}
            {/* Lista de produtos encontrados - sempre visível quando há resultados */}
            {produtosEncontrados.length > 0 && (
              <div className="mt-2 border rounded-lg max-h-48 overflow-y-auto bg-white dark:bg-gray-800 shadow-sm">
                {produtosEncontrados.map((produto) => {
                  const isSelected = produtoSelecionado?.id === produto.id;
                  return (
                    <button
                      key={produto.id}
                      type="button"
                      onClick={() => {
                        setProdutoSelecionado(produto);
                        setTermoBusca(produto.nome);
                        // Não limpar a lista para permitir ver outras opções
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
            {produtoSelecionado && (
              <div className="mt-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="font-medium text-blue-900 dark:text-blue-100">{produtoSelecionado.nome}</div>
                    <div className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                      Código: {produtoSelecionado.codigo} | Estoque atual: {produtoSelecionado.quantidade_em_estoque} {produtoSelecionado.unidade_medida}
                    </div>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setProdutoSelecionado(null);
                      setTermoBusca('');
                      setProdutosEncontrados([]);
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
            <Label htmlFor="quantidade">Quantidade *</Label>
            <Input
              id="quantidade"
              type="number"
              step="0.01"
              min="0.01"
              value={quantidade}
              onChange={(e) => setQuantidade(e.target.value)}
              placeholder="0.00"
              className="h-11"
              required
            />
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
                'Enviar Registro'
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}

