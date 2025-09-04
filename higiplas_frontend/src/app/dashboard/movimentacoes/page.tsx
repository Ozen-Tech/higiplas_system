'use client';

import { useState, useEffect } from 'react';
import { Header } from '@/components/dashboard/Header';
import { apiService } from '@/services/apiService';
import { DocumentTextIcon, CheckCircleIcon, ExclamationTriangleIcon, XMarkIcon, EyeIcon, ArrowUpTrayIcon, CogIcon } from '@heroicons/react/24/outline';
import Button from '@/components/Button';
import { useSearchParams } from 'next/navigation';

interface ProdutoSimilar {
  produto_id: number;
  nome: string;
  codigo: string;
  estoque_atual: number;
  score_similaridade: number;
}

interface ProdutoPreview {
  codigo: string;
  descricao_pdf: string;
  quantidade: number;
  valor_unitario: number;
  valor_total: number;
  encontrado: boolean;
  produto_id?: number;
  nome_sistema?: string;
  estoque_atual?: number;
  estoque_projetado?: number;
  produtos_similares?: ProdutoSimilar[];
}

interface PreviewResult {
  sucesso: boolean;
  arquivo: string;
  tipo_movimentacao: 'ENTRADA' | 'SAIDA';
  nota_fiscal?: string;
  data_emissao?: string;
  cliente?: string;
  fornecedor?: string;
  cnpj_fornecedor?: string;
  valor_total?: number;
  produtos_encontrados: ProdutoPreview[];
  produtos_nao_encontrados: ProdutoPreview[];
  total_produtos_pdf: number;
  produtos_validos: number;
}

interface ProcessingResult {
  sucesso: boolean;
  mensagem: string;
  movimentacoes_criadas: number;
  produtos_atualizados: string[];
  detalhes: unknown[];
}

export default function MovimentacoesPage() {
  const [tipoMovimentacao, setTipoMovimentacao] = useState<'ENTRADA' | 'SAIDA'>('ENTRADA');
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [previewData, setPreviewData] = useState<PreviewResult | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedProducts, setSelectedProducts] = useState<number[]>([]);
  const [selectedSimilarProducts, setSelectedSimilarProducts] = useState<{[key: number]: number}>({});
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const searchParams = useSearchParams();

  useEffect(() => {
    const tipo = searchParams.get('tipo');
    if (tipo === 'ENTRADA' || tipo === 'SAIDA') {
      setTipoMovimentacao(tipo);
    }
  }, [searchParams]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setArquivo(file);
      setError(null);
      setResult(null);
      setPreviewData(null);
    } else {
      setError('Por favor, selecione um arquivo PDF válido.');
    }
  };

  const handleVisualizarProdutos = async () => {
    if (!arquivo) {
      setError('Por favor, selecione um arquivo PDF.');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('arquivo', arquivo);
      formData.append('tipo_movimentacao', tipoMovimentacao);

      const response = await apiService.postFormData('/movimentacoes/preview-pdf', formData);

      if (response && response.data.sucesso) {
        setPreviewData(response.data);
        setSelectedProducts([]);
        setSelectedSimilarProducts({});
        setShowModal(true);
      } else {
        setError(response?.data?.mensagem || 'Erro ao processar o arquivo PDF.');
      }
    } catch (error: unknown) {
      console.error('Erro ao fazer upload:', error);
      const errorMessage = error && typeof error === 'object' && 'response' in error && 
        error.response && typeof error.response === 'object' && 'data' in error.response &&
        error.response.data && typeof error.response.data === 'object' && 'detail' in error.response.data
        ? String(error.response.data.detail)
        : 'Erro ao processar o arquivo. Tente novamente.';
      setError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const handleProcessarPDFEntrada = async () => {
    if (!arquivo) {
      setError('Por favor, selecione um arquivo PDF.');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('arquivo', arquivo);

      const response = await apiService.postFormData('/movimentacoes/processar-pdf-entrada', formData);

      if (response && response.data.sucesso) {
        setResult(response.data);
        setArquivo(null);
        const fileInput = document.getElementById('arquivo') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else {
        setError(response?.data?.mensagem || 'Erro ao processar o PDF de entrada.');
      }
    } catch (error: unknown) {
      console.error('Erro ao processar PDF de entrada:', error);
      const errorMessage = error && typeof error === 'object' && 'response' in error && 
        error.response && typeof error.response === 'object' && 'data' in error.response &&
        error.response.data && typeof error.response.data === 'object' && 'detail' in error.response.data
        ? String(error.response.data.detail)
        : 'Erro ao processar o arquivo. Tente novamente.';
      setError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleProcessarPDFSaida = async () => {
    if (!arquivo) {
      setError('Por favor, selecione um arquivo PDF.');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('arquivo', arquivo);
      formData.append('tipo_movimentacao', tipoMovimentacao);

      const response = await apiService.postFormData('/movimentacoes/processar-pdf', formData);

      if (response && response.data.sucesso) {
        setResult(response.data);
        setArquivo(null);
        const fileInput = document.getElementById('arquivo') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else {
        setError(response?.data?.mensagem || 'Erro ao processar o PDF de saída.');
      }
    } catch (error: unknown) {
      console.error('Erro ao processar PDF de saída:', error);
      const errorMessage = error && typeof error === 'object' && 'response' in error && 
        error.response && typeof error.response === 'object' && 'data' in error.response &&
        error.response.data && typeof error.response.data === 'object' && 'detail' in error.response.data
        ? String(error.response.data.detail)
        : 'Erro ao processar o arquivo. Tente novamente.';
      setError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleConfirmProcessing = async () => {
    if (!previewData || selectedProducts.length === 0) {
      setError('Selecione pelo menos um produto para processar.');
      return;
    }

    setIsConfirming(true);
    setError(null);

    try {
      const produtosSelecionados = selectedProducts.map(index => {
        const produto = previewData.produtos_encontrados[index];
        return {
          produto_id: produto.produto_id,
          quantidade: produto.quantidade
        };
      });
      
      const dados = {
        tipo_movimentacao: previewData.tipo_movimentacao,
        produtos_confirmados: produtosSelecionados,
        nota_fiscal: previewData.nota_fiscal,
        arquivo: previewData.arquivo
      };

      const response = await apiService.post('/movimentacoes/confirmar-movimentacoes', dados);

      if (response && response.data.sucesso) {
        setResult(response.data);
        setShowModal(false);
        setPreviewData(null);
        setSelectedProducts([]);
        setArquivo(null);
        const fileInput = document.getElementById('arquivo') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else {
        setError(response?.data?.mensagem || 'Erro ao confirmar as movimentações.');
      }
    } catch (error: unknown) {
      console.error('Erro ao confirmar movimentações:', error);
      const errorMessage = error && typeof error === 'object' && 'response' in error && 
        error.response && typeof error.response === 'object' && 'data' in error.response &&
        error.response.data && typeof error.response.data === 'object' && 'detail' in error.response.data
        ? String(error.response.data.detail)
        : 'Erro ao processar as movimentações. Tente novamente.';
      setError(errorMessage);
    } finally {
      setIsConfirming(false);
    }
  };

  const toggleProductSelection = (index: number) => {
    setSelectedProducts(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  const selectAllProducts = () => {
    if (previewData?.produtos_encontrados) {
      setSelectedProducts(previewData.produtos_encontrados.map((_, index) => index));
    }
  };

  const deselectAllProducts = () => {
    setSelectedProducts([]);
  };

  const handleSelectSimilarProduct = (produtoIndex: number, produtoId: number) => {
    setSelectedSimilarProducts(prev => ({
      ...prev,
      [produtoIndex]: produtoId
    }));
  };

  const handleAssociarProdutoSimilar = async (produtoIndex: number, produtoId: number) => {
    if (!previewData?.produtos_nao_encontrados[produtoIndex]) return;

    try {
      const produtoNaoEncontrado = previewData.produtos_nao_encontrados[produtoIndex];
      
      const dados = {
        codigo_pdf: produtoNaoEncontrado.codigo,
        produto_id_sistema: produtoId,
        quantidade: produtoNaoEncontrado.quantidade,
        tipo_movimentacao: previewData.tipo_movimentacao
      };

      const response = await apiService.post('/movimentacoes/associar-produto-similar', dados);

      if (response && response.data.sucesso) {
        // Atualizar os dados de preview removendo o produto da lista de não encontrados
        // e adicionando à lista de encontrados
        const novosProdutosNaoEncontrados = [...previewData.produtos_nao_encontrados];
        const produtoAssociado = novosProdutosNaoEncontrados.splice(produtoIndex, 1)[0];
        
        const novosProdutosEncontrados = [...previewData.produtos_encontrados, {
          ...produtoAssociado,
          encontrado: true,
          produto_id: produtoId,
          nome_sistema: response.data.produto_associado?.nome || 'Produto Associado'
        }];

        setPreviewData({
          ...previewData,
          produtos_encontrados: novosProdutosEncontrados,
          produtos_nao_encontrados: novosProdutosNaoEncontrados
        });

        // Limpar seleção de produto similar
        const novosSelectedSimilar = { ...selectedSimilarProducts };
        delete novosSelectedSimilar[produtoIndex];
        setSelectedSimilarProducts(novosSelectedSimilar);
      } else {
        setError(response?.data?.mensagem || 'Erro ao associar produto similar.');
      }
    } catch (error: unknown) {
      console.error('Erro ao associar produto similar:', error);
      const errorMessage = error && typeof error === 'object' && 'response' in error && 
        error.response && typeof error.response === 'object' && 'data' in error.response &&
        error.response.data && typeof error.response.data === 'object' && 'detail' in error.response.data
        ? String(error.response.data.detail)
        : 'Erro ao associar produto. Tente novamente.';
      setError(errorMessage);
    }
  };

  return (
    <>
      <Header />
      
      <div className="max-w-4xl mx-auto p-6 space-y-8">
        {/* Seletor de Tipo de Movimentação */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Tipo de Movimentação</h2>
          <div className="flex gap-4">
            <button
              onClick={() => setTipoMovimentacao('ENTRADA')}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                tipoMovimentacao === 'ENTRADA'
                  ? 'bg-green-600 text-white shadow-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              📦 Entrada de Estoque
            </button>
            <button
              onClick={() => setTipoMovimentacao('SAIDA')}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                tipoMovimentacao === 'SAIDA'
                  ? 'bg-red-600 text-white shadow-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              📤 Saída de Estoque
            </button>
          </div>
        </div>

        {/* Upload de Arquivo */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Upload de Nota Fiscal</h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-center w-full">
              <label htmlFor="arquivo" className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <ArrowUpTrayIcon className="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400" />
                  <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                    <span className="font-semibold">Clique para fazer upload</span> ou arraste e solte
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Apenas arquivos PDF</p>
                </div>
                <input
                  id="arquivo"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
            </div>
            
            {arquivo && (
              <div className="flex items-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <DocumentTextIcon className="h-5 w-5 text-blue-600 mr-2" />
                <span className="text-sm text-blue-800 dark:text-blue-200">{arquivo.name}</span>
              </div>
            )}
          </div>
        </div>

        {/* Ações */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Ações</h2>
          
          <div className="flex flex-col sm:flex-row gap-4">
            {tipoMovimentacao === 'ENTRADA' && (
              <Button
                onClick={handleProcessarPDFEntrada}
                disabled={!arquivo || isProcessing}
                className="flex-1 bg-green-600 hover:bg-green-700"
              >
                {isProcessing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Processando Entrada...
                  </>
                ) : (
                  <>
                    <CogIcon className="h-4 w-4 mr-2" />
                    Processar PDF de Entrada
                  </>
                )}
              </Button>
            )}
            
            {tipoMovimentacao === 'SAIDA' && (
              <Button
                onClick={handleProcessarPDFSaida}
                disabled={!arquivo || isProcessing}
                className="flex-1 bg-red-600 hover:bg-red-700"
              >
                {isProcessing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Processando Saída...
                  </>
                ) : (
                  <>
                    <CogIcon className="h-4 w-4 mr-2" />
                    Processar PDF de Saída
                  </>
                )}
              </Button>
            )}
            
            <Button
              onClick={handleVisualizarProdutos}
              disabled={!arquivo || isUploading}
              variant="secondary"
              className="flex-1"
            >
              {isUploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
                  Analisando...
                </>
              ) : (
                <>
                  <EyeIcon className="h-4 w-4 mr-2" />
                  Visualizar Produtos
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Mensagens de Erro */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600 mr-2" />
              <span className="text-red-800 dark:text-red-200">{error}</span>
            </div>
          </div>
        )}

        {/* Resultado do Processamento */}
        {result && (
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <CheckCircleIcon className="h-6 w-6 text-green-600 mr-2" />
              <h3 className="text-lg font-semibold text-green-800 dark:text-green-200">Processamento Concluído!</h3>
            </div>
            
            <div className="space-y-2 text-sm text-green-700 dark:text-green-300">
              <p><strong>Mensagem:</strong> {result.mensagem}</p>
              <p><strong>Movimentações criadas:</strong> {result.movimentacoes_criadas}</p>
              {result.produtos_atualizados.length > 0 && (
                <div>
                  <p><strong>Produtos atualizados:</strong></p>
                  <ul className="list-disc list-inside ml-4">
                    {result.produtos_atualizados.map((produto, index) => (
                      <li key={index}>{produto}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Modal de Preview */}
      {showModal && previewData && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in duration-200">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-7xl w-full max-h-[95vh] overflow-hidden flex flex-col border border-gray-200 dark:border-gray-700">
            {/* Header do Modal */}
            <div className="flex items-center justify-between p-6 border-b dark:border-gray-700 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/20 dark:via-indigo-900/20 dark:to-purple-900/20">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-lg">
                  <DocumentTextIcon className="h-7 w-7 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                    Preview da Nota Fiscal
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                      previewData.tipo_movimentacao === 'ENTRADA' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300'
                        : 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300'
                    }`}>
                      {previewData.tipo_movimentacao}
                    </span>
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 flex items-center gap-2">
                    <span className="inline-flex items-center gap-1">
                      📄 {previewData.arquivo}
                    </span>
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="p-2 hover:bg-white/80 dark:hover:bg-gray-700 rounded-xl transition-all duration-200 hover:scale-105 group"
              >
                <XMarkIcon className="h-6 w-6 text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-200" />
              </button>
            </div>

            {/* Informações da Nota Fiscal */}
            <div className="p-6 border-b dark:border-gray-700 bg-gradient-to-r from-gray-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-blue-900/10 dark:to-indigo-900/10">
              <div className="flex items-center mb-6">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/50 rounded-lg mr-3">
                  <DocumentTextIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <h4 className="text-lg font-bold text-gray-900 dark:text-gray-100">Informações da Nota Fiscal</h4>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
                {previewData.nota_fiscal && (
                  <div className="bg-white/80 dark:bg-gray-700/50 p-4 rounded-xl border border-gray-200 dark:border-gray-600 backdrop-blur-sm hover:shadow-md transition-all duration-200">
                    <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">📋 Nota Fiscal</div>
                    <div className="text-xl font-bold text-gray-900 dark:text-gray-100">{previewData.nota_fiscal}</div>
                  </div>
                )}
                {previewData.data_emissao && (
                  <div className="bg-white/80 dark:bg-gray-700/50 p-4 rounded-xl border border-gray-200 dark:border-gray-600 backdrop-blur-sm hover:shadow-md transition-all duration-200">
                    <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">📅 Data Emissão</div>
                    <div className="text-xl font-bold text-gray-900 dark:text-gray-100">{previewData.data_emissao}</div>
                  </div>
                )}
                {(previewData.cliente || previewData.fornecedor) && (
                  <div className="bg-white/80 dark:bg-gray-700/50 p-4 rounded-xl border border-gray-200 dark:border-gray-600 backdrop-blur-sm hover:shadow-md transition-all duration-200">
                    <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                      🏢 {previewData.tipo_movimentacao === 'ENTRADA' ? 'Fornecedor' : 'Cliente'}
                    </div>
                    <div className="text-lg font-bold text-gray-900 dark:text-gray-100 truncate" title={previewData.fornecedor || previewData.cliente}>
                      {previewData.fornecedor || previewData.cliente}
                    </div>
                  </div>
                )}
                {previewData.cnpj_fornecedor && (
                  <div className="bg-white/80 dark:bg-gray-700/50 p-4 rounded-xl border border-gray-200 dark:border-gray-600 backdrop-blur-sm hover:shadow-md transition-all duration-200">
                    <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">🆔 CNPJ</div>
                    <div className="text-lg font-bold text-gray-900 dark:text-gray-100 font-mono">{previewData.cnpj_fornecedor}</div>
                  </div>
                )}
                {previewData.valor_total && (
                  <div className="bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 p-4 rounded-xl border border-green-200 dark:border-green-700 hover:shadow-md transition-all duration-200">
                    <div className="text-xs font-semibold text-green-600 dark:text-green-400 uppercase tracking-wider mb-2">💰 Valor Total</div>
                    <div className="text-xl font-bold text-green-700 dark:text-green-300">R$ {previewData.valor_total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</div>
                  </div>
                )}
              </div>
            </div>

            {/* Conteúdo do Modal */}
            <div className="flex-1 overflow-hidden flex flex-col">
              {/* Resumo Aprimorado */}
              <div className="p-6 border-b dark:border-gray-700 bg-gradient-to-r from-gray-50/50 to-blue-50/50 dark:from-gray-900/50 dark:to-blue-900/20">
                <div className="flex items-center mb-4">
                  <div className="p-2 bg-blue-100 dark:bg-blue-900/50 rounded-lg mr-3">
                    <CogIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <h4 className="text-lg font-bold text-gray-900 dark:text-white">Resumo dos Produtos</h4>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 p-5 rounded-2xl border border-green-200 dark:border-green-700 hover:shadow-lg transition-all duration-300 hover:scale-105">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">{previewData.produtos_encontrados.length}</div>
                        <div className="text-sm font-semibold text-green-700 dark:text-green-300">✅ Encontrados</div>
                      </div>
                      <div className="p-2 bg-green-200 dark:bg-green-800 rounded-xl">
                        <CheckCircleIcon className="h-6 w-6 text-green-600 dark:text-green-400" />
                      </div>
                    </div>
                  </div>
                  <div className="bg-gradient-to-br from-red-50 to-rose-100 dark:from-red-900/30 dark:to-rose-900/30 p-5 rounded-2xl border border-red-200 dark:border-red-700 hover:shadow-lg transition-all duration-300 hover:scale-105">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-3xl font-bold text-red-600 dark:text-red-400 mb-1">{previewData.produtos_nao_encontrados.length}</div>
                        <div className="text-sm font-semibold text-red-700 dark:text-red-300">❌ Não Encontrados</div>
                      </div>
                      <div className="p-2 bg-red-200 dark:bg-red-800 rounded-xl">
                        <ExclamationTriangleIcon className="h-6 w-6 text-red-600 dark:text-red-400" />
                      </div>
                    </div>
                  </div>
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 p-5 rounded-2xl border border-blue-200 dark:border-blue-700 hover:shadow-lg transition-all duration-300 hover:scale-105">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-1">{selectedProducts.length}</div>
                        <div className="text-sm font-semibold text-blue-700 dark:text-blue-300">🔵 Selecionados</div>
                      </div>
                      <div className="p-2 bg-blue-200 dark:bg-blue-800 rounded-xl">
                        <CogIcon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                      </div>
                    </div>
                  </div>
                  <div className="bg-gradient-to-br from-purple-50 to-violet-100 dark:from-purple-900/30 dark:to-violet-900/30 p-5 rounded-2xl border border-purple-200 dark:border-purple-700 hover:shadow-lg transition-all duration-300 hover:scale-105">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-1">{previewData.total_produtos_pdf}</div>
                        <div className="text-sm font-semibold text-purple-700 dark:text-purple-300">📄 Total no PDF</div>
                      </div>
                      <div className="p-2 bg-purple-200 dark:bg-purple-800 rounded-xl">
                        <DocumentTextIcon className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Controles e Lista de Produtos */}
              <div className="flex-1 overflow-y-auto p-6">

                {/* Controles de Seleção Aprimorados */}
                {previewData.produtos_encontrados.length > 0 && (
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 p-4 bg-gradient-to-r from-blue-50/50 to-indigo-50/50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-700">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-100 dark:bg-blue-900/50 rounded-lg">
                        <CogIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                      </div>
                      <div>
                        <h4 className="text-lg font-bold text-gray-900 dark:text-white">Produtos para Processar</h4>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300 rounded-full text-sm font-semibold">
                            {selectedProducts.length} selecionados
                          </span>
                          <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm font-medium">
                            de {previewData.produtos_encontrados.length} disponíveis
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <Button 
                        onClick={selectAllProducts} 
                        className="px-5 py-2.5 text-sm font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-md hover:shadow-lg transition-all duration-200 hover:scale-105"
                      >
                        ✓ Selecionar Todos
                      </Button>
                      <Button 
                        onClick={deselectAllProducts} 
                        variant="secondary" 
                        className="px-5 py-2.5 text-sm font-semibold border-2 border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 transition-all duration-200 hover:scale-105"
                      >
                        ✗ Desmarcar Todos
                      </Button>
                    </div>
                  </div>
                )}

                {/* Lista de Produtos Encontrados Aprimorada */}
                {previewData.produtos_encontrados.length > 0 && (
                  <div className="mb-8">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-2 bg-green-100 dark:bg-green-900/50 rounded-lg">
                        <CheckCircleIcon className="h-6 w-6 text-green-600 dark:text-green-400" />
                      </div>
                      <div>
                        <h4 className="text-xl font-bold text-gray-900 dark:text-white">Produtos Encontrados</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {previewData.produtos_encontrados.length} produtos identificados no PDF
                        </p>
                      </div>
                    </div>
                    <div className="grid gap-4">
                      {previewData.produtos_encontrados.map((produto, index) => (
                        <div key={index} className={`group relative p-5 bg-white dark:bg-gray-800 border-2 rounded-xl transition-all duration-200 hover:shadow-lg ${
                          selectedProducts.includes(index) 
                            ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-900/20 shadow-md' 
                            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                        }`}>
                          <div className="flex items-start gap-4">
                            <div className="flex items-center pt-1">
                              <input
                                type="checkbox"
                                checked={selectedProducts.includes(index)}
                                onChange={() => toggleProductSelection(index)}
                                className="h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded transition-all duration-200 hover:scale-110"
                              />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-3 mb-3">
                                <div className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg">
                                  <span className="font-bold text-gray-900 dark:text-white text-sm">{produto.codigo}</span>
                                </div>
                                <div className="flex-1 min-w-0">
                                  <h5 className="font-semibold text-gray-900 dark:text-white truncate">{produto.nome_sistema || produto.descricao_pdf}</h5>
                                </div>
                              </div>
                              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                                <div className="flex items-center gap-2">
                                  <div className="p-1.5 bg-blue-100 dark:bg-blue-900/50 rounded">
                                    <span className="text-xs font-medium text-blue-600 dark:text-blue-400">QTD</span>
                                  </div>
                                  <span className="font-semibold text-gray-900 dark:text-white">{produto.quantidade}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="p-1.5 bg-purple-100 dark:bg-purple-900/50 rounded">
                                    <span className="text-xs font-medium text-purple-600 dark:text-purple-400">UNIT</span>
                                  </div>
                                  <span className="font-semibold text-gray-900 dark:text-white">R$ {produto.valor_unitario?.toFixed(2) || '0.00'}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="p-1.5 bg-green-100 dark:bg-green-900/50 rounded">
                                    <span className="text-xs font-medium text-green-600 dark:text-green-400">TOTAL</span>
                                  </div>
                                  <span className="font-bold text-green-600 dark:text-green-400">R$ {produto.valor_total?.toFixed(2) || '0.00'}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="p-1.5 bg-orange-100 dark:bg-orange-900/50 rounded">
                                    <span className="text-xs font-medium text-orange-600 dark:text-orange-400">EST</span>
                                  </div>
                                  <span className="text-sm text-gray-600 dark:text-gray-400">
                                    {produto.estoque_atual || 0} → {produto.estoque_projetado || 0}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                          {selectedProducts.includes(index) && (
                            <div className="absolute top-3 right-3">
                              <div className="p-1 bg-blue-500 rounded-full">
                                <CheckCircleIcon className="h-4 w-4 text-white" />
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Lista de Produtos Não Encontrados Aprimorada */}
                {previewData.produtos_nao_encontrados.length > 0 && (
                  <div>
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-2 bg-red-100 dark:bg-red-900/50 rounded-lg">
                        <ExclamationTriangleIcon className="h-6 w-6 text-red-600 dark:text-red-400" />
                      </div>
                      <div>
                        <h4 className="text-xl font-bold text-gray-900 dark:text-white">Produtos Não Encontrados</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {previewData.produtos_nao_encontrados.length} produtos precisam de atenção
                        </p>
                      </div>
                    </div>
                    <div className="grid gap-4">
                      {previewData.produtos_nao_encontrados.map((produto, index) => (
                        <div key={index} className="group relative p-5 bg-gradient-to-r from-red-50/80 to-rose-50/80 dark:from-red-900/20 dark:to-rose-900/20 border-2 border-red-200 dark:border-red-700 rounded-xl hover:shadow-lg transition-all duration-200">
                          <div className="flex items-start gap-4">
                            <div className="flex items-center pt-1">
                              <div className="p-2 bg-red-200 dark:bg-red-800 rounded-full">
                                <ExclamationTriangleIcon className="h-4 w-4 text-red-700 dark:text-red-300" />
                              </div>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-3 mb-3">
                                <div className="px-3 py-1 bg-red-200 dark:bg-red-800 rounded-lg">
                                  <span className="font-bold text-red-800 dark:text-red-200 text-sm">{produto.codigo}</span>
                                </div>
                                <div className="flex-1 min-w-0">
                                  <h5 className="font-semibold text-gray-900 dark:text-white truncate">{produto.descricao_pdf}</h5>
                                </div>
                              </div>
                              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
                                <div className="flex items-center gap-2">
                                  <div className="p-1.5 bg-blue-100 dark:bg-blue-900/50 rounded">
                                    <span className="text-xs font-medium text-blue-600 dark:text-blue-400">QTD</span>
                                  </div>
                                  <span className="font-semibold text-gray-900 dark:text-white">{produto.quantidade}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="p-1.5 bg-purple-100 dark:bg-purple-900/50 rounded">
                                    <span className="text-xs font-medium text-purple-600 dark:text-purple-400">UNIT</span>
                                  </div>
                                  <span className="font-semibold text-gray-900 dark:text-white">R$ {produto.valor_unitario?.toFixed(2) || '0.00'}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="p-1.5 bg-red-100 dark:bg-red-900/50 rounded">
                                    <span className="text-xs font-medium text-red-600 dark:text-red-400">TOTAL</span>
                                  </div>
                                  <span className="font-bold text-red-600 dark:text-red-400">R$ {produto.valor_total?.toFixed(2) || '0.00'}</span>
                                </div>
                              </div>
                              
                              {/* Produtos Similares */}
                              {produto.produtos_similares && produto.produtos_similares.length > 0 && (
                                <div className="mt-4 p-4 bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20 rounded-xl border-2 border-yellow-200 dark:border-yellow-700">
                                  <div className="flex items-center mb-3">
                                    <div className="p-2 bg-yellow-100 dark:bg-yellow-800 rounded-lg mr-3">
                                      <EyeIcon className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                                    </div>
                                    <h5 className="font-bold text-yellow-800 dark:text-yellow-200">
                                      Produtos Similares Encontrados
                                    </h5>
                                  </div>
                                  <div className="space-y-3">
                                    {produto.produtos_similares.map((similar, similarIndex) => (
                                      <div key={similarIndex} className="group p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-yellow-300 dark:hover:border-yellow-500 transition-all">
                                        <div className="flex items-center justify-between">
                                          <div className="flex items-center space-x-3">
                                            <input
                                              type="radio"
                                              name={`similar-${index}`}
                                              value={similar.produto_id}
                                              checked={selectedSimilarProducts[index] === similar.produto_id}
                                              onChange={() => handleSelectSimilarProduct(index, similar.produto_id)}
                                              className="h-4 w-4 text-yellow-600 border-2 border-gray-300 focus:ring-yellow-500"
                                            />
                                            <div className="flex-1">
                                              <div className="font-semibold text-gray-900 dark:text-gray-100">
                                                {similar.nome}
                                              </div>
                                              <div className="flex items-center space-x-3 mt-1 text-xs">
                                                <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded font-mono">
                                                  {similar.codigo}
                                                </span>
                                                <span className="text-gray-600 dark:text-gray-400">
                                                  Estoque: {similar.estoque_atual}
                                                </span>
                                                <span className={`px-2 py-1 rounded font-bold ${
                                                  similar.score_similaridade >= 80 
                                                    ? 'bg-green-100 text-green-700 dark:bg-green-800 dark:text-green-300'
                                                    : similar.score_similaridade >= 60
                                                    ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-800 dark:text-yellow-300'
                                                    : 'bg-red-100 text-red-700 dark:bg-red-800 dark:text-red-300'
                                                }`}>
                                                  {Math.round(similar.score_similaridade)}%
                                                </span>
                                              </div>
                                            </div>
                                          </div>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                  {selectedSimilarProducts[index] && (
                                    <div className="mt-4 flex justify-end">
                                      <Button
                                        onClick={() => handleAssociarProdutoSimilar(index, selectedSimilarProducts[index])}
                                        className="px-4 py-2 text-sm bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold rounded-lg shadow-md transition-all"
                                      >
                                        ✓ Associar Produto Selecionado
                                      </Button>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
               </div>
            </div>

            {/* Rodapé do Modal Aprimorado */}
            <div className="flex-shrink-0 px-6 py-5 bg-gradient-to-r from-gray-50 to-blue-50/30 dark:from-gray-800 dark:to-blue-900/20 border-t-2 border-gray-200 dark:border-gray-700">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900/50 rounded-lg">
                      <CheckCircleIcon className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="text-sm">
                      <div className="font-semibold text-gray-900 dark:text-white">
                        {selectedProducts.length} produtos selecionados
                      </div>
                      <div className="text-gray-600 dark:text-gray-400">
                        de {previewData.produtos_encontrados.length} disponíveis
                      </div>
                    </div>
                  </div>
                  {previewData.produtos_nao_encontrados.length > 0 && (
                    <div className="flex items-center gap-2">
                      <div className="p-2 bg-yellow-100 dark:bg-yellow-900/50 rounded-lg">
                        <ExclamationTriangleIcon className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                      </div>
                      <div className="text-sm">
                        <div className="font-semibold text-yellow-700 dark:text-yellow-300">
                          {previewData.produtos_nao_encontrados.length} não encontrados
                        </div>
                        <div className="text-yellow-600 dark:text-yellow-400">
                          precisam de atenção
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <div className="flex gap-3 w-full sm:w-auto">
                  <Button
                    onClick={() => setShowModal(false)}
                    variant="secondary"
                    className="flex-1 sm:flex-none px-6 py-3 font-semibold border-2 border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 transition-all duration-200 hover:scale-105"
                  >
                    ✗ Cancelar
                  </Button>
                  <Button
                    onClick={handleConfirmProcessing}
                    disabled={selectedProducts.length === 0 || isConfirming}
                    className="flex-1 sm:flex-none px-6 py-3 font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105 disabled:hover:scale-100"
                  >
                    {isConfirming ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                        Processando movimentações...
                      </>
                    ) : (
                      <>
                        <CheckCircleIcon className="h-5 w-5 mr-2" />
                        Confirmar e Processar ({selectedProducts.length})
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}