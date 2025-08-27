'use client';

import { useState } from 'react';
import { Header } from '@/components/dashboard/Header';
import { apiService } from '@/services/apiService';
import { DocumentTextIcon, CheckCircleIcon, ExclamationTriangleIcon, XMarkIcon, EyeIcon } from '@heroicons/react/24/outline';
import Button from '@/components/Button';

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
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [tipoMovimentacao, setTipoMovimentacao] = useState<'ENTRADA' | 'SAIDA'>('SAIDA');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [previewData, setPreviewData] = useState<PreviewResult | null>(null);
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const [error, setError] = useState<string>('');
  const [showModal, setShowModal] = useState(false);
  const [selectedProducts, setSelectedProducts] = useState<number[]>([]);
  const [selectedSimilarProducts, setSelectedSimilarProducts] = useState<{[key: number]: number}>({});

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
        setError('');
        setPreviewData(null);
        setResult(null);
      } else {
        setError('Por favor, selecione apenas arquivos PDF.');
        setSelectedFile(null);
      }
    }
  };

  const handlePreviewPDF = async () => {
    if (!selectedFile) {
      setError('Por favor, selecione um arquivo PDF.');
      return;
    }

    setIsProcessing(true);
    setError('');
    setPreviewData(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('arquivo', selectedFile);
      formData.append('tipo_movimentacao', tipoMovimentacao);

      const response = await apiService.postFormData('/movimentacoes/preview-pdf', formData);
      
      if (response?.data) {
        // Garantir que os arrays sempre existam
        const previewDataWithDefaults = {
          ...response?.data,
          produtos_encontrados: response?.data?.produtos_encontrados || [],
          produtos_nao_encontrados: response?.data?.produtos_nao_encontrados || []
        };
        
        setPreviewData(previewDataWithDefaults);
        setShowModal(true);
        
        // Selecionar todos os produtos encontrados por padrão
        const produtosEncontrados = previewDataWithDefaults.produtos_encontrados;
        setSelectedProducts(produtosEncontrados.map((_: ProdutoPreview, index: number) => index));
      }
      
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const errorMessage = error.response?.data?.detail || 'Erro ao processar PDF';
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
    setError('');

    try {
      const produtosConfirmados = selectedProducts.map(index => 
        previewData?.produtos_encontrados[index]
      );

      const dados = {
        produtos_confirmados: produtosConfirmados,
        tipo_movimentacao: previewData?.tipo_movimentacao,
        nota_fiscal: previewData?.nota_fiscal
      };

      const response = await apiService.post('/movimentacoes/confirmar-movimentacoes', dados);
      
      if (response?.data) {
        setResult(response.data);
      }
      setShowModal(false);
      setPreviewData(null);
      setSelectedFile(null);
      
    } catch (err: unknown) {
      console.error('Erro ao confirmar movimentações:', err);
      const error = err as { response?: { data?: { detail?: string } } };
      const errorMessage = error.response?.data?.detail || 'Erro ao confirmar movimentações';
      setError(errorMessage);
      // Manter o modal aberto em caso de erro para que o usuário possa tentar novamente
      // setShowModal(false); // Comentado para manter o modal aberto
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
    if (!previewData || !previewData?.produtos_encontrados) return;
    setSelectedProducts(previewData.produtos_encontrados.map((_, index) => index));
  };

  const deselectAllProducts = () => {
    setSelectedProducts([]);
  };

  const handleAssociarProdutoSimilar = async (produtoNaoEncontradoIndex: number, produtoSimilarId: number) => {
    try {
      const produtoNaoEncontrado = previewData?.produtos_nao_encontrados[produtoNaoEncontradoIndex];
      if (!produtoNaoEncontrado) return;

      const dados = {
        produto_id_sistema: produtoSimilarId,
        codigo_pdf: produtoNaoEncontrado.codigo,
        descricao_pdf: produtoNaoEncontrado.descricao_pdf,
        quantidade: produtoNaoEncontrado.quantidade,
        tipo_movimentacao: previewData?.tipo_movimentacao,
        nota_fiscal: previewData?.nota_fiscal
      };

      const response = await apiService.post('/movimentacoes/associar-produto-similar', dados);
      
      if (response?.data?.sucesso) {
        // Atualizar o estado para remover o produto da lista de não encontrados
        // e adicionar à lista de encontrados
        setPreviewData(prev => {
          if (!prev) return prev;
          
          const produtoAssociado = {
            ...produtoNaoEncontrado,
            encontrado: true,
            produto_id: produtoSimilarId,
            nome_sistema: response.data?.produto_associado?.nome || 'Nome não disponível',
            estoque_atual: response.data?.produto_associado?.estoque_atual || 0,
            estoque_projetado: response.data?.produto_associado?.estoque_projetado || 0
          };
          
          return {
            ...prev,
            produtos_encontrados: [...(prev.produtos_encontrados || []), produtoAssociado],
            produtos_nao_encontrados: (prev.produtos_nao_encontrados || []).filter((_, i) => i !== produtoNaoEncontradoIndex)
          };
        });
        
        // Adicionar o produto à seleção usando o índice correto
        setSelectedProducts(prev => {
          if (!previewData || !previewData?.produtos_encontrados) {
            return prev;
          }
          const newIndex = previewData.produtos_encontrados.length;
          return [...prev, newIndex];
        });
        
        alert('Produto associado com sucesso!');
      }
    } catch (err: unknown) {
      console.error('Erro ao associar produto similar:', err);
      const error = err as { response?: { data?: { detail?: string } } };
      const errorMessage = error.response?.data?.detail || 'Erro ao associar produto';
      alert(`Erro: ${errorMessage}`);
    }
  };

  const handleSelectSimilarProduct = (produtoNaoEncontradoIndex: number, produtoSimilarId: number) => {
    setSelectedSimilarProducts(prev => ({
      ...prev,
      [produtoNaoEncontradoIndex]: produtoSimilarId
    }));
  };

  return (
    <>
      <Header>
        <h1 className="text-xl font-bold">Movimentações de Estoque</h1>
      </Header>
      <main className="flex-1 p-4 md:p-6 overflow-y-auto">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Card de Upload */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border dark:border-gray-700">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Processar PDF de Movimentação
            </h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Faça upload de um PDF com dados de movimentação de estoque para visualização e confirmação.
            </p>

            {/* Seleção do tipo de movimentação */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Tipo de Movimentação
              </label>
              <div className="flex gap-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="ENTRADA"
                    checked={tipoMovimentacao === 'ENTRADA'}
                    onChange={(e) => setTipoMovimentacao(e.target.value as 'ENTRADA' | 'SAIDA')}
                    className="mr-2"
                  />
                  <span className="text-green-600 font-medium">Entrada</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="SAIDA"
                    checked={tipoMovimentacao === 'SAIDA'}
                    onChange={(e) => setTipoMovimentacao(e.target.value as 'ENTRADA' | 'SAIDA')}
                    className="mr-2"
                  />
                  <span className="text-red-600 font-medium">Saída</span>
                </label>
              </div>
            </div>

            {/* Upload de arquivo */}
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 mb-6">
              <div className="text-center">
                <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <label htmlFor="pdf-upload" className="cursor-pointer">
                  <span className="text-lg font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-500">
                    Clique para selecionar um arquivo PDF
                  </span>
                  <input
                    id="pdf-upload"
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </label>
                <p className="text-gray-500 dark:text-gray-400 mt-2">
                  ou arraste e solte o arquivo aqui
                </p>
              </div>
              
              {selectedFile && (
                <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-md">
                  <div className="flex items-center">
                    <DocumentTextIcon className="h-5 w-5 text-blue-500 mr-2" />
                    <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                      {selectedFile.name}
                    </span>
                    <span className="text-sm text-blue-500 ml-2">
                      ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Botão de visualizar */}
            <Button
              onClick={handlePreviewPDF}
              disabled={!selectedFile || isProcessing}
              className="w-full"
            >
              {isProcessing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Analisando PDF...
                </>
              ) : (
                <>
                  <EyeIcon className="h-4 w-4 mr-2" />
                  Visualizar Produtos do PDF
                </>
              )}
            </Button>
          </div>

          {/* Mensagem de erro */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <div className="flex items-center">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mr-2" />
                <span className="text-red-700 dark:text-red-300">{error}</span>
              </div>
            </div>
          )}

          {/* Resultado final do processamento */}
          {result && (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border dark:border-gray-700">
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
                ✅ Processamento Concluído
              </h3>
              
              <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg mb-4">
                <p className="text-green-700 dark:text-green-300 font-medium">{result?.mensagem || 'Processamento concluído'}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{result?.movimentacoes_criadas || 0}</div>
                  <div className="text-sm text-blue-700 dark:text-blue-300">Movimentações Criadas</div>
                </div>
                <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{result?.produtos_atualizados?.length || 0}</div>
                  <div className="text-sm text-purple-700 dark:text-purple-300">Produtos Atualizados</div>
                </div>
              </div>

              {result?.produtos_atualizados && result.produtos_atualizados.length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    Produtos Atualizados:
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {result.produtos_atualizados.map((produto, index) => (
                      <span key={index} className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full text-sm">
                        {produto}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Modal de Confirmação */}
      {showModal && previewData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            {/* Header do Modal */}
            <div className="flex items-center justify-between p-6 border-b dark:border-gray-700">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  Confirmar Movimentações
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Arquivo: {previewData?.arquivo || 'N/A'} | Tipo: {previewData?.tipo_movimentacao || 'N/A'}
                </p>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            {/* Informações da Nota Fiscal */}
            {(previewData?.nota_fiscal || previewData?.data_emissao || previewData?.cliente) && (
              <div className="p-6 border-b dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">Informações da Nota Fiscal</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  {previewData?.nota_fiscal && (
                    <div>
                      <span className="font-medium text-gray-700 dark:text-gray-300">NF: </span>
                      <span className="text-gray-600 dark:text-gray-400">{previewData.nota_fiscal}</span>
                    </div>
                  )}
                  {previewData?.data_emissao && (
                    <div>
                      <span className="font-medium text-gray-700 dark:text-gray-300">Data: </span>
                      <span className="text-gray-600 dark:text-gray-400">{previewData.data_emissao}</span>
                    </div>
                  )}
                  {previewData?.cliente && (
                    <div>
                      <span className="font-medium text-gray-700 dark:text-gray-300">Cliente: </span>
                      <span className="text-gray-600 dark:text-gray-400">{previewData.cliente}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Conteúdo do Modal */}
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              {/* Resumo */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{previewData?.produtos_encontrados?.length || 0}</div>
                  <div className="text-sm text-green-700 dark:text-green-300">Produtos Encontrados</div>
                </div>
                <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{previewData?.produtos_nao_encontrados?.length || 0}</div>
                  <div className="text-sm text-red-700 dark:text-red-300">Não Encontrados</div>
                </div>
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{selectedProducts.length}</div>
                  <div className="text-sm text-blue-700 dark:text-blue-300">Selecionados</div>
                </div>
              </div>

              {/* Controles de Seleção */}
              {(previewData?.produtos_encontrados?.length || 0) > 0 && (
                <div className="flex gap-2 mb-4">
                  <Button onClick={selectAllProducts} className="px-3 py-1 text-sm">
                    Selecionar Todos
                  </Button>
                  <Button onClick={deselectAllProducts} className="px-3 py-1 text-sm">
                    Desmarcar Todos
                  </Button>
                </div>
              )}

              {/* Lista de Produtos Encontrados */}
              {(previewData?.produtos_encontrados?.length || 0) > 0 && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
                    Produtos Encontrados no Sistema
                  </h4>
                  <div className="space-y-3">
                    {previewData.produtos_encontrados && previewData.produtos_encontrados.map((produto, index) => (
                      <div
                        key={index}
                        className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                          selectedProducts.includes(index)
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                            : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
                        }`}
                        onClick={() => toggleProductSelection(index)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <input
                              type="checkbox"
                              checked={selectedProducts.includes(index)}
                              onChange={() => toggleProductSelection(index)}
                              className="mr-3"
                            />
                            <div>
                              <div className="font-medium text-gray-900 dark:text-gray-100">
                                {produto?.nome_sistema || produto?.descricao_pdf || 'Nome não disponível'}
                              </div>
                              <div className="text-sm text-gray-500 dark:text-gray-400">
                                Código: {produto.codigo}
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold text-gray-900 dark:text-gray-100">
                              {produto.quantidade} unidades
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              Estoque: {produto?.estoque_atual || 0} → {produto?.estoque_projetado || 0}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Lista de Produtos Não Encontrados */}
              {(previewData?.produtos_nao_encontrados?.length || 0) > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
                    Produtos Não Encontrados no Sistema
                  </h4>
                  <div className="space-y-4">
                    {previewData.produtos_nao_encontrados && previewData.produtos_nao_encontrados.map((produto, index) => (
                      <div key={index} className="p-4 rounded-lg border border-red-200 bg-red-50 dark:bg-red-900/20">
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <div className="font-medium text-gray-900 dark:text-gray-100">
                              {produto.descricao_pdf}
                            </div>
                            <div className="text-sm text-red-600 dark:text-red-400">
                              Código: {produto.codigo} (não encontrado no sistema)
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold text-gray-900 dark:text-gray-100">
                              {produto.quantidade} unidades
                            </div>
                            <div className="text-sm text-red-600 dark:text-red-400">
                              {produto?.produtos_similares && produto.produtos_similares.length > 0 ? 'Produtos similares encontrados' : 'Não será processado'}
                            </div>
                          </div>
                        </div>
                        
                        {/* Produtos Similares */}
                        {produto?.produtos_similares && produto.produtos_similares.length > 0 && (
                          <div className="mt-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                            <h5 className="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-2">
                              Produtos similares encontrados (selecione um para associar):
                            </h5>
                            <div className="space-y-2">
                              {produto.produtos_similares.map((similar, similarIndex) => (
                                <div key={similarIndex} className="flex items-center justify-between p-2 bg-white dark:bg-gray-800 rounded border">
                                  <div className="flex items-center">
                                    <input
                                      type="radio"
                                      name={`similar-${index}`}
                                      value={similar.produto_id}
                                      checked={selectedSimilarProducts[index] === similar.produto_id}
                                      onChange={() => handleSelectSimilarProduct(index, similar.produto_id)}
                                      className="mr-2"
                                    />
                                    <div>
                                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                        {similar?.nome || 'Nome não disponível'}
                                      </div>
                                      <div className="text-xs text-gray-500 dark:text-gray-400">
                                        Código: {similar?.codigo || 'N/A'} | Estoque: {similar?.estoque_atual || 0} | Similaridade: {Math.round(similar?.score_similaridade || 0)}%
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                            {selectedSimilarProducts[index] && (
                              <div className="mt-3">
                                <Button
                                  onClick={() => handleAssociarProdutoSimilar(index, selectedSimilarProducts[index])}
                                  className="px-3 py-1 text-sm bg-green-600 hover:bg-green-700"
                                >
                                  Associar Produto Selecionado
                                </Button>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Footer do Modal */}
            <div className="flex items-center justify-between p-6 border-t dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {selectedProducts.length} de {previewData?.produtos_encontrados?.length || 0} produtos selecionados
              </div>
              <div className="flex gap-3">
                <Button
                  onClick={() => setShowModal(false)}
                  variant="secondary"
                >
                  Cancelar
                </Button>
                <Button
                  onClick={handleConfirmProcessing}
                  disabled={selectedProducts.length === 0 || isConfirming}
                >
                  {isConfirming ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Processando...
                    </>
                  ) : (
                    <>
                      <CheckCircleIcon className="h-4 w-4 mr-2" />
                      Confirmar e Processar ({selectedProducts.length})
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}