'use client';

import { useState } from 'react';
import { MovimentacaoPendente, MotivoMovimentacao } from '@/types';
import { useMovimentacoesPendentesAdmin } from '@/hooks/useMovimentacoesPendentesAdmin';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, Edit } from 'lucide-react';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';

interface ProdutoBusca {
  id: number;
  nome: string;
  codigo: string;
  unidade_medida: string;
}

interface EdicaoMovimentacao {
  quantidade?: number;
  tipo_movimentacao?: 'ENTRADA' | 'SAIDA';
  produto_id?: number;
  motivo_movimentacao?: MotivoMovimentacao;
  observacao?: string;
  observacao_motivo?: string;
}

interface EditarMovimentacaoModalProps {
  movimentacao: MovimentacaoPendente;
  onClose: () => void;
}

export function EditarMovimentacaoModal({ movimentacao, onClose }: EditarMovimentacaoModalProps) {
  const { editarMovimentacao, editarEConfirmarMovimentacao } = useMovimentacoesPendentesAdmin();
  const [loading, setLoading] = useState(false);
  const [confirmarAposEditar, setConfirmarAposEditar] = useState(false);
  
  const [produtoId, setProdutoId] = useState(movimentacao.produto_id);
  const [produtoSelecionado, setProdutoSelecionado] = useState<ProdutoBusca | null>(movimentacao.produto ? {
    id: movimentacao.produto.id,
    nome: movimentacao.produto.nome,
    codigo: movimentacao.produto.codigo,
    unidade_medida: movimentacao.produto.unidade_medida,
  } : null);
  const [termoBusca, setTermoBusca] = useState('');
  const [produtosEncontrados, setProdutosEncontrados] = useState<ProdutoBusca[]>([]);
  const [quantidade, setQuantidade] = useState(movimentacao.quantidade.toString());
  const [tipoMovimentacao, setTipoMovimentacao] = useState<'ENTRADA' | 'SAIDA'>(movimentacao.tipo_movimentacao);
  const [motivoMovimentacao, setMotivoMovimentacao] = useState<MotivoMovimentacao | ''>(
    movimentacao.motivo_movimentacao || ''
  );
  const [observacao, setObservacao] = useState(movimentacao.observacao || '');
  const [observacaoMotivo, setObservacaoMotivo] = useState(movimentacao.observacao_motivo || '');

  const buscarProdutos = async (termo: string) => {
    if (!termo || termo.trim().length < 2) {
      setProdutosEncontrados([]);
      return;
    }

    try {
      const response = await apiService.get(`/produtos/buscar?q=${encodeURIComponent(termo.trim())}`);
      const produtos = (response?.data || []).map((p: { id: number; nome: string; codigo: string; unidade_medida: string }) => ({
        id: p.id,
        nome: p.nome,
        codigo: p.codigo,
        unidade_medida: p.unidade_medida,
      }));
      setProdutosEncontrados(produtos);
    } catch (error) {
      console.error('Erro ao buscar produtos:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!quantidade || parseFloat(quantidade) <= 0) {
      toast.error('Informe uma quantidade válida');
      return;
    }

    setLoading(true);
    try {
      const edicao: EdicaoMovimentacao = {
        quantidade: parseFloat(quantidade),
        tipo_movimentacao: tipoMovimentacao,
      };

      if (produtoId !== movimentacao.produto_id) {
        edicao.produto_id = produtoId;
      }

      if (motivoMovimentacao) {
        edicao.motivo_movimentacao = motivoMovimentacao;
      }

      if (observacao !== movimentacao.observacao) {
        edicao.observacao = observacao;
      }

      if (observacaoMotivo !== movimentacao.observacao_motivo) {
        edicao.observacao_motivo = observacaoMotivo;
      }

      if (confirmarAposEditar) {
        await editarEConfirmarMovimentacao(movimentacao.id, edicao);
      } else {
        await editarMovimentacao(movimentacao.id, edicao);
      }
      onClose();
    } catch (error) {
      console.error('Erro ao editar:', error);
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
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 transition-opacity overflow-y-auto py-8">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-full max-w-2xl border border-gray-200 dark:border-gray-700 my-auto">
        <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">
          Editar e Confirmar Movimentação
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="produto">Produto</Label>
            <Input
              id="produto"
              placeholder="Buscar produto..."
              value={termoBusca || produtoSelecionado?.nome || ''}
              onChange={(e) => {
                setTermoBusca(e.target.value);
                buscarProdutos(e.target.value);
              }}
              className="h-11"
            />
            {produtosEncontrados.length > 0 && (
              <div className="mt-2 border rounded-lg max-h-48 overflow-y-auto">
                {produtosEncontrados.map((produto) => (
                  <button
                    key={produto.id}
                    type="button"
                    onClick={() => {
                      setProdutoSelecionado(produto);
                      setProdutoId(produto.id);
                      setTermoBusca(produto.nome);
                      setProdutosEncontrados([]);
                    }}
                    className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 border-b last:border-b-0"
                  >
                    <div className="font-medium">{produto.nome}</div>
                    <div className="text-sm text-gray-500">Código: {produto.codigo}</div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="tipo">Tipo</Label>
              <Select value={tipoMovimentacao} onValueChange={(v) => setTipoMovimentacao(v as 'ENTRADA' | 'SAIDA')}>
                <SelectTrigger id="tipo" className="h-11">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="SAIDA">Saída</SelectItem>
                  <SelectItem value="ENTRADA">Entrada</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="quantidade">Quantidade</Label>
              <Input
                id="quantidade"
                type="number"
                step="0.01"
                min="0.01"
                value={quantidade}
                onChange={(e) => setQuantidade(e.target.value)}
                className="h-11"
                required
              />
            </div>
          </div>

          <div>
            <Label htmlFor="motivo">Motivo</Label>
            <Select
              value={motivoMovimentacao}
              onValueChange={(v) => setMotivoMovimentacao(v as MotivoMovimentacao)}
            >
              <SelectTrigger id="motivo" className="h-11">
                <SelectValue />
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

          <div>
            <Label htmlFor="observacaoMotivo">Observação do Motivo</Label>
            <Textarea
              id="observacaoMotivo"
              value={observacaoMotivo}
              onChange={(e) => setObservacaoMotivo(e.target.value)}
              rows={2}
            />
          </div>

          <div>
            <Label htmlFor="observacao">Observação</Label>
            <Textarea
              id="observacao"
              value={observacao}
              onChange={(e) => setObservacao(e.target.value)}
              rows={3}
            />
          </div>

          <div className="space-y-3 pt-4">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="confirmar"
                checked={confirmarAposEditar}
                onChange={(e) => setConfirmarAposEditar(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <Label htmlFor="confirmar" className="text-sm font-normal cursor-pointer">
                Confirmar e aplicar ao estoque após editar
              </Label>
            </div>
            <div className="flex gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={loading}
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
                    Salvando...
                  </>
                ) : (
                  <>
                    <Edit className="mr-2 h-4 w-4" />
                    {confirmarAposEditar ? 'Salvar e Confirmar' : 'Salvar'}
                  </>
                )}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

