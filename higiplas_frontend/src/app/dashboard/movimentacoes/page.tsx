'use client';

import { useState, useEffect, useMemo } from 'react';
import { Header } from '@/components/dashboard/Header';
import { apiService } from '@/services/apiService';
import { DocumentTextIcon, CheckCircleIcon, ExclamationTriangleIcon, EyeIcon, ArrowUpTrayIcon, CogIcon } from '@heroicons/react/24/outline';
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
  codigo_sistema?: string;
  estoque_atual?: number;
  estoque_projetado?: number;
  produtos_similares?: ProdutoSimilar[];
}

interface Vendedor {
  id: number;
  nome: string;
  email: string;
}

interface Orcamento {
  id: number;
  numero: string;
  data_criacao?: string;
  status: string;
}

interface PreviewResult {
  sucesso: boolean;
  arquivo: string;
  tipo_movimentacao: 'ENTRADA' | 'SAIDA';
  empresa_id?: number;
  nota_fiscal?: string;
  data_emissao?: string;
  cliente?: string;
  cliente_id?: number;
  cnpj_cliente?: string;
  fornecedor?: string;
  cnpj_fornecedor?: string;
  valor_total?: number;
  vendedor_id?: number;
  orcamento_id?: number;
  is_delta_plastico?: boolean;
  produtos_encontrados: ProdutoPreview[];
  produtos_nao_encontrados: ProdutoPreview[];
  produtos: ProdutoPreview[];
  total_produtos_pdf: number;
  produtos_validos: number;
  vendedores_disponiveis?: Vendedor[];
  orcamentos_disponiveis?: Orcamento[];
}

interface ProcessingResult {
  sucesso: boolean;
  mensagem: string;
  movimentacoes_criadas: number;
  produtos_atualizados: string[];
  detalhes: unknown[];
  codigos_sincronizados?: {
    produto_id: number;
    produto_nome: string;
    codigo_anterior?: string | null;
    codigo_novo: string;
  }[];
}

type WizardStep = 'UPLOAD' | 'ASSOCIACAO' | 'REVISAO';
type ProdutoFiltro = 'TODOS' | 'PRONTOS' | 'PENDENTES' | 'ALERTAS';

export default function MovimentacoesPage() {
  const [tipoMovimentacao, setTipoMovimentacao] = useState<'ENTRADA' | 'SAIDA'>('ENTRADA');
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [previewData, setPreviewData] = useState<PreviewResult | null>(null);
  const [wizardStep, setWizardStep] = useState<WizardStep>('UPLOAD');
  const [selectedProducts, setSelectedProducts] = useState<number[]>([]);
  const [selectedSimilarProducts, setSelectedSimilarProducts] = useState<{[key: number]: number}>({});
  const [searchTerms, setSearchTerms] = useState<{[key: number]: string}>({});
  const [searchResults, setSearchResults] = useState<{[key: number]: ProdutoSimilar[]}>({});
  const [isSearching, setIsSearching] = useState<{[key: number]: boolean}>({});
  const [quantidadesEditadas, setQuantidadesEditadas] = useState<{[key: number]: number}>({});
  const [filterStatus, setFilterStatus] = useState<ProdutoFiltro>('TODOS');
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const [vendedorSelecionado, setVendedorSelecionado] = useState<number | null>(null);
  const [orcamentoSelecionado, setOrcamentoSelecionado] = useState<number | null>(null);
  const searchParams = useSearchParams();

  useEffect(() => {
    const tipo = searchParams.get('tipo');
    if (tipo === 'ENTRADA' || tipo === 'SAIDA') {
      setTipoMovimentacao(tipo);
    }
  }, [searchParams]);

  useEffect(() => {
    if (!previewData) {
      setWizardStep('UPLOAD');
      setSelectedProducts([]);
      setQuantidadesEditadas({});
      setFilterStatus('TODOS');
    }
  }, [previewData]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && (file.type === 'application/pdf' || file.type === 'text/xml' || file.type === 'application/xml' || file.name.toLowerCase().endsWith('.xml'))) {
      setArquivo(file);
      setError(null);
      setResult(null);
      setPreviewData(null);
    } else {
      setError('Por favor, selecione um arquivo PDF ou XML válido.');
    }
  };

  const handleVisualizarProdutos = async () => {
    if (!arquivo) {
      setError('Por favor, selecione um arquivo PDF ou XML.');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('arquivo', arquivo);
      formData.append('tipo_movimentacao', tipoMovimentacao);

      // Detectar se é XML ou PDF e usar o endpoint apropriado
      const isXML = arquivo.name.toLowerCase().endsWith('.xml') || 
                    arquivo.type === 'text/xml' || 
                    arquivo.type === 'application/xml';
      
      const endpoint = isXML ? '/api/entrada/processar-xml' : '/movimentacoes/preview-pdf';

      const response = await apiService.postFormData(endpoint, formData);

      if (response && response.data.sucesso) {
        const preview = response.data as PreviewResult;
        setPreviewData(preview);
        const preSelecionados = preview.produtos_encontrados
          .map((produto, index) => (produto.produto_id ? index : null))
          .filter((index): index is number => index !== null);
        setSelectedProducts(preSelecionados);
        setSelectedSimilarProducts({});
        setSearchTerms({});
        setSearchResults({});
        setQuantidadesEditadas({});
        // Definir vendedor e orçamento se vierem do backend
        if (preview.vendedor_id) {
          setVendedorSelecionado(preview.vendedor_id);
        }
        if (preview.orcamento_id) {
          setOrcamentoSelecionado(preview.orcamento_id);
        }
        setWizardStep('ASSOCIACAO');
        setFilterStatus('TODOS');
      } else {
        setError(response?.data?.mensagem || `Erro ao processar o arquivo ${isXML ? 'XML' : 'PDF'}.`);
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
      setError('Por favor, selecione um arquivo PDF ou XML.');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('arquivo', arquivo);

      // Detectar se é XML ou PDF e usar o endpoint apropriado
      const isXML = arquivo.name.toLowerCase().endsWith('.xml') || 
                    arquivo.type === 'text/xml' || 
                    arquivo.type === 'application/xml';
      
      const endpoint = isXML ? '/api/entrada/processar-xml' : '/movimentacoes/processar-pdf-entrada';

      const response = await apiService.postFormData(endpoint, formData);

      if (response && response.data.sucesso) {
        setResult(response.data);
        setArquivo(null);
        const fileInput = document.getElementById('arquivo') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else {
        setError(response?.data?.mensagem || `Erro ao processar o ${isXML ? 'XML' : 'PDF'} de entrada.`);
      }
    } catch (error: unknown) {
      console.error('Erro ao processar arquivo de entrada:', error);
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
      type ProdutoConfirmado = {
        produto_id: number;
        quantidade: number;
        codigo_nf?: string;
        descricao_nf?: string;
      };
      
      const produtosSelecionados = selectedProducts
        .map(index => {
          const produto = previewData.produtos_encontrados[index];
          if (!produto?.produto_id) {
            return null;
          }
          const produtoConfirmado: ProdutoConfirmado = {
            produto_id: produto.produto_id,
            quantidade: quantidadesEditadas[index] ?? produto.quantidade,
            codigo_nf: produto.codigo,
            descricao_nf: produto.descricao_pdf
          };
          return produtoConfirmado;
        })
        .filter((item): item is ProdutoConfirmado => item !== null);
      
      if (produtosSelecionados.length === 0) {
        setError('Selecione pelo menos um produto válido para processar.');
        setIsConfirming(false);
        return;
      }

      const dados = {
        tipo_movimentacao: previewData.tipo_movimentacao,
        empresa_id: previewData.empresa_id,
        cliente_id: previewData.cliente_id,
        vendedor_id: vendedorSelecionado || previewData.vendedor_id,
        orcamento_id: orcamentoSelecionado || previewData.orcamento_id,
        produtos_confirmados: produtosSelecionados,
        nota_fiscal: previewData.nota_fiscal,
        arquivo: previewData.arquivo
      };

      const response = await apiService.post('/movimentacoes/confirmar-movimentacoes', dados);

      if (response && response.data.sucesso) {
        setResult(response.data);
        setPreviewData(null);
        setSelectedProducts([]);
        setQuantidadesEditadas({});
        setWizardStep('UPLOAD');
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
    const produto = previewData?.produtos_encontrados[index];
    if (!produto?.produto_id) {
      return;
    }
    setSelectedProducts(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  const selectAllProducts = () => {
    if (previewData?.produtos_encontrados) {
      const selecionaveis = previewData.produtos_encontrados
        .map((produto, index) => (produto.produto_id ? index : null))
        .filter((index): index is number => index !== null);
      setSelectedProducts(selecionaveis);
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

  const handleBuscarProdutosSimilares = async (produtoIndex: number, termo: string) => {
    if (!termo || termo.trim().length < 2) {
      setSearchResults(prev => {
        const newResults = { ...prev };
        delete newResults[produtoIndex];
        return newResults;
      });
      return;
    }

    setIsSearching(prev => ({ ...prev, [produtoIndex]: true }));

    try {
      const response = await apiService.get(`/movimentacoes/buscar-produtos-similares?termo=${encodeURIComponent(termo.trim())}&limit=20`);
      
      if (response && response.data) {
        setSearchResults(prev => ({
          ...prev,
          [produtoIndex]: response.data
        }));
      }
    } catch (error: unknown) {
      console.error('Erro ao buscar produtos similares:', error);
      setSearchResults(prev => {
        const newResults = { ...prev };
        delete newResults[produtoIndex];
        return newResults;
      });
    } finally {
      setIsSearching(prev => ({ ...prev, [produtoIndex]: false }));
    }
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
          nome_sistema: response.data.produto?.nome || response.data.produto_associado?.nome || 'Produto Associado',
          codigo_sistema: response.data.produto?.codigo || response.data.produto_associado?.codigo,
          estoque_atual: response.data.produto?.estoque_atual ?? produtoAssociado.estoque_atual,
          estoque_projetado: response.data.produto?.estoque_apos_movimentacao ?? produtoAssociado.estoque_projetado
        }];

        const previewAtualizado = {
          ...previewData,
          produtos_encontrados: novosProdutosEncontrados,
          produtos_nao_encontrados: novosProdutosNaoEncontrados
        };

        setPreviewData(previewAtualizado);
        const novoIndex = previewAtualizado.produtos_encontrados.length - 1;
        setSelectedProducts(prev => [...prev, novoIndex]);

        // Limpar seleção de produto similar e busca
        const novosSelectedSimilar = { ...selectedSimilarProducts };
        delete novosSelectedSimilar[produtoIndex];
        setSelectedSimilarProducts(novosSelectedSimilar);
        
        const novosSearchTerms = { ...searchTerms };
        delete novosSearchTerms[produtoIndex];
        setSearchTerms(novosSearchTerms);
        
        const novosSearchResults = { ...searchResults };
        delete novosSearchResults[produtoIndex];
        setSearchResults(novosSearchResults);
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

  const produtosComInsights = useMemo(() => {
    if (!previewData || !previewData.produtos_encontrados) return [];
    return previewData.produtos_encontrados.map((produto, index) => {
      const quantidadePlanejada = quantidadesEditadas[index] ?? produto.quantidade;
      const estoqueAtual =
        typeof produto.estoque_atual === 'number' ? produto.estoque_atual : Number(produto.estoque_atual);
      const estoqueInsuficiente =
        previewData.tipo_movimentacao === 'SAIDA' &&
        typeof estoqueAtual === 'number' &&
        !Number.isNaN(estoqueAtual) &&
        estoqueAtual < quantidadePlanejada;
      const divergenciaCodigo =
        Boolean(produto.codigo && produto.codigo_sistema && produto.codigo_sistema !== produto.codigo);
      const pendenteAssociacao = !produto.produto_id;
      let status: ProdutoFiltro = 'PRONTOS';
      if (estoqueInsuficiente || divergenciaCodigo) {
        status = 'ALERTAS';
      } else if (pendenteAssociacao) {
        status = 'PENDENTES';
      }
      return {
        ...produto,
        index,
        quantidadePlanejada,
        estoqueInsuficiente,
        divergenciaCodigo,
        pendenteAssociacao,
        status
      };
    });
  }, [previewData, quantidadesEditadas]);

  const produtosFiltrados = useMemo(() => {
    if (filterStatus === 'TODOS') {
      return produtosComInsights;
    }
    return produtosComInsights.filter(produto => produto.status === filterStatus);
  }, [produtosComInsights, filterStatus]);

  const alertasCriticos = useMemo(() => produtosComInsights.filter(produto => produto.status === 'ALERTAS'), [produtosComInsights]);

  const resumoKPIs = useMemo(() => {
    return {
      encontrados: previewData?.produtos_encontrados?.length ?? 0,
      pendentes: produtosComInsights?.filter(p => p.status === 'PENDENTES')?.length ?? 0,
      alertas: alertasCriticos?.length ?? 0,
      totalPdf: previewData?.total_produtos_pdf ?? 0
    };
  }, [previewData, produtosComInsights, alertasCriticos]);

  const quantidadeSelecionavel = produtosComInsights?.filter(produto => !produto.pendenteAssociacao)?.length ?? 0;
  const podeAvancar = quantidadeSelecionavel > 0;
  const valorTotalSelecionado = selectedProducts?.reduce((total, index) => {
    const produto = produtosComInsights?.find(item => item.index === index);
    if (!produto) return total;
    const valorLinha = (produto.valor_unitario || 0) * produto.quantidadePlanejada;
    return total + valorLinha;
  }, 0) ?? 0;

  const handleQuantidadeChange = (index: number, value: string) => {
    setQuantidadesEditadas(prev => {
      if (value === '') {
        const novoEstado = { ...prev };
        delete novoEstado[index];
        return novoEstado;
      }
      const parsed = Number(value);
      if (Number.isNaN(parsed) || parsed <= 0) {
        return prev;
      }
      return {
        ...prev,
        [index]: parsed
      };
    });
  };

  const handleAvancarParaRevisao = () => {
    if (!podeAvancar) {
      setError('Associe pelo menos um produto ao estoque antes de avançar.');
      return;
    }
    setWizardStep('REVISAO');
  };

  const handleVoltarParaAssociacao = () => {
    setWizardStep('ASSOCIACAO');
  };

  const wizardSequence: WizardStep[] = ['UPLOAD', 'ASSOCIACAO', 'REVISAO'];
  const wizardCopy: Record<WizardStep, { title: string; description: string }> = {
    UPLOAD: { title: 'Upload', description: 'PDF recebido e analisado' },
    ASSOCIACAO: { title: 'Associação', description: 'Valide correspondências e conclua pendentes' },
    REVISAO: { title: 'Revisão', description: 'Selecione e confirme as baixas' }
  };
  const currentStepIndex = wizardSequence.indexOf(wizardStep);

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
                  <p className="text-xs text-gray-500 dark:text-gray-400">PDF ou XML (NF-e)</p>
                </div>
                <input
                  id="arquivo"
                  type="file"
                  accept=".pdf,.xml"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
            </div>
            
            {arquivo && (
              <div className={`flex items-center justify-between p-3 rounded-lg border ${
                arquivo.name.toLowerCase().endsWith('.xml')
                  ? 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800'
                  : 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
              }`}>
                <div className="flex items-center">
                  <DocumentTextIcon className={`h-5 w-5 mr-2 ${
                    arquivo.name.toLowerCase().endsWith('.xml')
                      ? 'text-purple-600'
                      : 'text-blue-600'
                  }`} />
                  <div>
                    <span className={`text-sm font-medium ${
                      arquivo.name.toLowerCase().endsWith('.xml')
                        ? 'text-purple-800 dark:text-purple-200'
                        : 'text-blue-800 dark:text-blue-200'
                    }`}>{arquivo.name}</span>
                    <p className={`text-xs ${
                      arquivo.name.toLowerCase().endsWith('.xml')
                        ? 'text-purple-600 dark:text-purple-300'
                        : 'text-blue-600 dark:text-blue-300'
                    }`}>
                      {arquivo.name.toLowerCase().endsWith('.xml') ? '📄 Arquivo XML (NF-e)' : '📄 Arquivo PDF'}
                    </p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                  arquivo.name.toLowerCase().endsWith('.xml')
                    ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300'
                    : 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300'
                }`}>
                  {arquivo.name.toLowerCase().endsWith('.xml') ? 'XML' : 'PDF'}
                </span>
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
                    {arquivo?.name.toLowerCase().endsWith('.xml') ? 'Processar XML de Entrada' : 'Processar PDF de Entrada'}
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


      {previewData && (
        <section className="max-w-6xl mx-auto px-6 mt-10 mb-16">
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-3xl shadow-2xl p-8 space-y-8">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Fluxo guiado da nota</p>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{previewData.nota_fiscal || 'Nota sem número'}</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{previewData.cliente || previewData.fornecedor || 'Origem não identificada'}</p>
              </div>
              <div className="flex flex-wrap gap-3 items-center">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${previewData.tipo_movimentacao === 'ENTRADA' ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300' : 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300'}`}>
                  {previewData.tipo_movimentacao}
                </span>
                <Button variant="secondary" className="text-sm" onClick={() => setPreviewData(null)}>Descartar análise</Button>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {wizardSequence.map((step, index) => {
                const meta = wizardCopy[step];
                const isDone = index < currentStepIndex;
                const isActive = step === wizardStep;
                return (
                  <div
                    key={step}
                    className={`rounded-2xl border p-4 transition ${isDone ? 'border-emerald-400 bg-emerald-50 dark:bg-emerald-900/20' : isActive ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800'}`}
                  >
                    <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Etapa {index + 1}</div>
                    <div className="font-semibold text-gray-900 dark:text-white">{meta.title}</div>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{meta.description}</p>
                  </div>
                );
              })}
            </div>

            <div className="grid gap-8 lg:grid-cols-[2fr,1fr]">
              <div className="space-y-6">
                {wizardStep === 'ASSOCIACAO' ? (
                  <>
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="rounded-2xl border border-green-200 dark:border-green-700 bg-green-50 dark:bg-green-900/20 p-4">
                        <p className="text-xs text-green-600 dark:text-green-300 uppercase">Encontrados</p>
                        <p className="text-3xl font-bold text-green-700 dark:text-green-200">{resumoKPIs.encontrados}</p>
                      </div>
                      <div className="rounded-2xl border border-amber-200 dark:border-amber-700 bg-amber-50 dark:bg-amber-900/20 p-4">
                        <p className="text-xs text-amber-600 dark:text-amber-300 uppercase">Pendentes</p>
                        <p className="text-3xl font-bold text-amber-700 dark:text-amber-200">{resumoKPIs.pendentes + previewData.produtos_nao_encontrados.length}</p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-gray-900 dark:text-white">Produtos identificados</h3>
                        <span className="text-sm text-gray-500">Revise antes de seguir</span>
                      </div>
                      <div className="space-y-3">
                        {produtosComInsights.length === 0 && (
                          <div className="p-4 rounded-2xl border border-dashed text-sm text-gray-500 dark:text-gray-400">Nenhum produto associado até o momento.</div>
                        )}
                        {produtosComInsights.map(produto => (
                          <div key={produto.index} className="rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
                            <div className="flex items-start justify-between gap-3">
                              <div>
                                <p className="text-sm text-gray-500">Código NF: <span className="font-mono">{produto.codigo || '—'}</span></p>
                                <p className="font-semibold text-gray-900 dark:text-white">{produto.nome_sistema || produto.descricao_pdf}</p>
                                <p className="text-xs text-gray-500">Qty: {produto.quantidade}</p>
                              </div>
                              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${produto.status === 'ALERTAS' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300' : produto.status === 'PENDENTES' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300' : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'}`}>
                                {produto.status === 'ALERTAS' ? 'Alerta' : produto.status === 'PENDENTES' ? 'Pendente' : 'Pronto'}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-gray-900 dark:text-white">Produtos sem correspondência</h3>
                        <span className="text-sm text-gray-500">Associe itens antes de avançar</span>
                      </div>
                      {previewData.produtos_nao_encontrados.length === 0 ? (
                        <div className="p-4 rounded-2xl border border-emerald-200 bg-emerald-50 text-emerald-800 text-sm">Todos os itens foram associados com sucesso.</div>
                      ) : (
                        <div className="space-y-4">
                          {previewData.produtos_nao_encontrados.map((produto, index) => (
                            <div key={`pendente-${index}`} className="rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 space-y-4">
                              <div className="flex flex-col gap-1">
                                <p className="text-xs text-gray-500">Código NF: {produto.codigo}</p>
                                <p className="font-semibold text-gray-900 dark:text-white">{produto.descricao_pdf}</p>
                                <p className="text-xs text-gray-500">Quantidade: {produto.quantidade}</p>
                              </div>
                              <div className="flex flex-col gap-3 sm:flex-row">
                                <input
                                  className="flex-1 rounded-xl border border-gray-300 dark:border-gray-700 bg-transparent px-3 py-2 text-sm"
                                  placeholder="Buscar produto similar..."
                                  value={searchTerms[index] ?? produto.descricao_pdf}
                                  onChange={(event) => setSearchTerms(prev => ({ ...prev, [index]: event.target.value }))}
                                  onBlur={(event) => handleBuscarProdutosSimilares(index, event.target.value)}
                                />
                                <Button
                                  variant="secondary"
                                  onClick={() => handleBuscarProdutosSimilares(index, searchTerms[index] ?? produto.descricao_pdf)}
                                  disabled={isSearching[index]}
                                >
                                  {isSearching[index] ? 'Buscando...' : 'Buscar'}
                                </Button>
                              </div>
                              {searchResults[index]?.length ? (
                                <div className="space-y-2">
                                  {searchResults[index].map(similar => (
                                    <label key={similar.produto_id} className="flex items-center justify-between rounded-xl border border-gray-200 dark:border-gray-700 px-3 py-2 text-sm">
                                      <div className="flex-1">
                                        <p className="font-semibold">{similar.nome}</p>
                                        <p className="text-xs text-gray-500">Código: {similar.codigo} • Estoque: {similar.estoque_atual}</p>
                                      </div>
                                      <div className="flex items-center gap-3">
                                        <input
                                          type="radio"
                                          name={`similar-${index}`}
                                          checked={selectedSimilarProducts[index] === similar.produto_id}
                                          onChange={() => handleSelectSimilarProduct(index, similar.produto_id)}
                                        />
                                        <Button className="px-3 py-2 text-sm" onClick={() => handleAssociarProdutoSimilar(index, similar.produto_id)}>
                                          Associar
                                        </Button>
                                      </div>
                                    </label>
                                  ))}
                                </div>
                              ) : (
                                <p className="text-xs text-gray-500">Pesquise para encontrar correspondências.</p>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
                      <Button variant="secondary" className="text-sm" onClick={() => setPreviewData(null)}>Cancelar</Button>
                      <Button onClick={handleAvancarParaRevisao} disabled={!podeAvancar} className="bg-blue-600 hover:bg-blue-700 text-white">
                        Avançar para revisão
                      </Button>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">Checklist final de saída</h3>
                        <p className="text-sm text-gray-500">Selecione os itens que serão confirmados</p>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {(['TODOS','PRONTOS','PENDENTES','ALERTAS'] as ProdutoFiltro[]).map(filtro => (
                          <button
                            key={filtro}
                            onClick={() => setFilterStatus(filtro)}
                            className={`px-4 py-2 rounded-full text-sm font-semibold border transition ${filterStatus === filtro ? 'border-blue-500 text-blue-600 dark:text-blue-300' : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300'}`}
                          >
                            {filtro}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="flex flex-col gap-3 rounded-2xl border border-blue-200 dark:border-blue-800 bg-blue-50/60 dark:bg-blue-900/20 p-4">
                      <div className="text-sm text-gray-700 dark:text-gray-200">{selectedProducts.length} itens selecionados de {quantidadeSelecionavel} elegíveis</div>
                      <div className="flex flex-wrap gap-3">
                        <Button className="px-3 py-2 text-sm" onClick={selectAllProducts}>Selecionar todos</Button>
                        <Button className="px-3 py-2 text-sm" variant="secondary" onClick={deselectAllProducts}>Limpar seleção</Button>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {produtosFiltrados.length === 0 && (
                        <div className="p-6 text-center text-sm text-gray-500 border border-dashed rounded-2xl">Nenhum produto corresponde ao filtro atual.</div>
                      )}
                      {produtosFiltrados.map(produto => (
                        <div key={`revisao-${produto.index}`} className={`rounded-3xl border p-5 ${selectedProducts.includes(produto.index) ? 'border-blue-500 bg-blue-50/30 dark:bg-blue-900/10' : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800'}`}>
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex items-start gap-3">
                              <input
                                type="checkbox"
                                disabled={produto.pendenteAssociacao}
                                checked={selectedProducts.includes(produto.index)}
                                onChange={() => toggleProductSelection(produto.index)}
                                className="mt-1 h-4 w-4"
                              />
                              <div>
                                <p className="font-semibold text-gray-900 dark:text-white">{produto.nome_sistema || produto.descricao_pdf}</p>
                                <p className="text-xs text-gray-500">NF {produto.codigo || '—'} {produto.codigo_sistema && `• Sistema ${produto.codigo_sistema}`}</p>
                              </div>
                            </div>
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${produto.status === 'ALERTAS' ? 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300' : produto.status === 'PENDENTES' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300' : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300'}`}>
                              {produto.status === 'ALERTAS' ? 'Alerta' : produto.status === 'PENDENTES' ? 'Pendente' : 'Pronto'}
                            </span>
                          </div>
                          <div className="mt-4 grid gap-3 sm:grid-cols-4 text-sm">
                            <label className="flex flex-col gap-1">
                              Quantidade
                              <input
                                type="number"
                                min="0"
                                className="rounded-xl border border-gray-300 dark:border-gray-600 bg-transparent px-3 py-2"
                                value={quantidadesEditadas[produto.index] ?? produto.quantidade}
                                onChange={(event) => handleQuantidadeChange(produto.index, event.target.value)}
                              />
                            </label>
                            <div>
                              Estoque atual
                              <p className="font-semibold">{produto.estoque_atual ?? 0}</p>
                            </div>
                            <div>
                              Valor estimado
                              <p className="font-semibold">R$ {((produto.valor_unitario || 0) * produto.quantidadePlanejada).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
                            </div>
                            <div>
                              Alertas
                              <p className={`text-xs ${(produto.estoqueInsuficiente || produto.divergenciaCodigo) ? 'text-red-600 dark:text-red-300' : 'text-gray-500'}`}>
                                {produto.estoqueInsuficiente ? 'Estoque insuficiente' : produto.divergenciaCodigo ? 'Código divergente' : 'Nenhum'}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                      <div className="text-sm text-gray-600 dark:text-gray-300">
                        <p>Itens selecionados: <strong>{selectedProducts.length}</strong></p>
                        <p>Valor estimado: <strong>R$ {valorTotalSelecionado.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</strong></p>
                      </div>
                      <div className="flex flex-col gap-3 sm:flex-row">
                        <Button variant="secondary" onClick={handleVoltarParaAssociacao}>Voltar para associação</Button>
                        <Button
                          className="bg-red-600 hover:bg-red-700 text-white"
                          onClick={handleConfirmProcessing}
                          disabled={selectedProducts.length === 0 || isConfirming}
                        >
                          {isConfirming ? 'Confirmando...' : 'Confirmar movimentações'}
                        </Button>
                      </div>
                    </div>
                  </>
                )}
              </div>

              <aside className="space-y-5 rounded-3xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 p-6">
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide">Detalhes da NF</h4>
                  <div className="mt-3 space-y-2 text-sm text-gray-600 dark:text-gray-300">
                    <p><strong>Arquivo:</strong> {previewData.arquivo}</p>
                    <p><strong>NF:</strong> {previewData.nota_fiscal || '—'}</p>
                    <p><strong>Emissão:</strong> {previewData.data_emissao || '—'}</p>
                    {previewData.cliente && (
                      <p><strong>Cliente:</strong> {previewData.cliente}</p>
                    )}
                    {previewData.cnpj_cliente && (
                      <p><strong>CNPJ:</strong> {previewData.cnpj_cliente}</p>
                    )}
                    <p><strong>Total de itens:</strong> {previewData.total_produtos_pdf}</p>
                    {previewData.valor_total && (
                      <p><strong>Valor:</strong> R$ {previewData.valor_total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
                    )}
                    {previewData.is_delta_plastico && (
                      <p className="text-amber-600 dark:text-amber-400 font-semibold">⚠️ Delta Plástico (Entrada especial)</p>
                    )}
                  </div>
                </div>

                {previewData.tipo_movimentacao === 'SAIDA' && (
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide mb-2">
                        Vendedor Responsável
                      </h4>
                      <select
                        value={vendedorSelecionado || previewData.vendedor_id || ''}
                        onChange={(e) => setVendedorSelecionado(e.target.value ? Number(e.target.value) : null)}
                        className="w-full rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
                      >
                        <option value="">Selecione um vendedor...</option>
                        {previewData.vendedores_disponiveis?.map((vendedor) => (
                          <option key={vendedor.id} value={vendedor.id}>
                            {vendedor.nome} {vendedor.email ? `(${vendedor.email})` : ''}
                          </option>
                        ))}
                      </select>
                      {vendedorSelecionado && (
                        <p className="mt-1 text-xs text-gray-500">
                          Vendedor selecionado
                        </p>
                      )}
                    </div>

                    {previewData.cliente_id && previewData.orcamentos_disponiveis && previewData.orcamentos_disponiveis.length > 0 && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide mb-2">
                          Relacionar com Orçamento (Opcional)
                        </h4>
                        <select
                          value={orcamentoSelecionado || previewData.orcamento_id || ''}
                          onChange={(e) => setOrcamentoSelecionado(e.target.value ? Number(e.target.value) : null)}
                          className="w-full rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-gray-100"
                        >
                          <option value="">Não relacionar</option>
                          {previewData.orcamentos_disponiveis.map((orcamento) => (
                            <option key={orcamento.id} value={orcamento.id}>
                              {orcamento.numero} - {orcamento.status}
                              {orcamento.data_criacao && ` (${new Date(orcamento.data_criacao).toLocaleDateString('pt-BR')})`}
                            </option>
                          ))}
                        </select>
                        {orcamentoSelecionado && (
                          <p className="mt-1 text-xs text-green-600 dark:text-green-400">
                            ✓ Orçamento relacionado - Vendedor será atribuído automaticamente
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                )}

                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide">KPIs rápidos</h4>
                  <ul className="mt-3 space-y-2 text-sm">
                    <li className="flex items-center justify-between"><span>Encontrados</span><strong>{resumoKPIs.encontrados}</strong></li>
                    <li className="flex items-center justify-between"><span>Pendentes</span><strong>{resumoKPIs.pendentes}</strong></li>
                    <li className="flex items-center justify-between"><span>Alertas</span><strong>{resumoKPIs.alertas}</strong></li>
                    <li className="flex items-center justify-between"><span>Total PDF</span><strong>{resumoKPIs.totalPdf}</strong></li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wide">Alertas críticos</h4>
                  {alertasCriticos.length === 0 ? (
                    <p className="mt-3 text-sm text-gray-500">Sem alertas no momento.</p>
                  ) : (
                    <ul className="mt-3 space-y-2 text-sm text-red-600 dark:text-red-300">
                      {alertasCriticos.map(alerta => (
                        <li key={`alerta-${alerta.index}`}>{alerta.nome_sistema || alerta.descricao_pdf} — verifique estoque/código.</li>
                      ))}
                    </ul>
                  )}
                </div>

                <div className="rounded-2xl border border-gray-200 dark:border-gray-600 p-4 text-sm">
                  <p className="text-gray-600 dark:text-gray-300">Resumo da seleção</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">R$ {valorTotalSelecionado.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
                  <p className="text-xs text-gray-500">{selectedProducts.length} itens preparados</p>
                </div>
              </aside>
            </div>
          </div>
        </section>
      )}

    </>
  );
}