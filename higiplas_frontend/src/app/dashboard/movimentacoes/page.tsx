'use client';

import { useState } from 'react';
import { Header } from '@/components/dashboard/Header';
import { apiService } from '@/services/apiService';
import { ArrowUpOnSquareIcon, DocumentTextIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import Button from '@/components/Button';

interface ProcessedMovement {
  produto_nome: string;
  quantidade: number;
  tipo_movimentacao: 'ENTRADA' | 'SAIDA';
  observacao?: string;
  status: 'success' | 'error' | 'not_found';
  message?: string;
}

interface ProcessingResult {
  movements_created: number;
  products_found: number;
  products_not_found: number;
  processed_movements: ProcessedMovement[];
}

export default function MovimentacoesPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [tipoMovimentacao, setTipoMovimentacao] = useState<'ENTRADA' | 'SAIDA'>('SAIDA');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const [error, setError] = useState<string>('');


  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
        setError('');
      } else {
        setError('Por favor, selecione apenas arquivos PDF.');
        setSelectedFile(null);
      }
    }
  };

  const handleProcessPDF = async () => {
    if (!selectedFile) {
      setError('Por favor, selecione um arquivo PDF.');
      return;
    }

    setIsProcessing(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('tipo_movimentacao', tipoMovimentacao);

      const response = await apiService.post('/processar-pdf', formData);

      setResult(response.data);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const errorMessage = error.response?.data?.detail || 'Erro ao processar PDF';
      setError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'error':
      case 'not_found':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-600 bg-green-50';
      case 'error':
      case 'not_found':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
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
              Faça upload de um PDF com dados de movimentação de estoque para processamento automático.
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

            {/* Botão de processar */}
            <Button
              onClick={handleProcessPDF}
              disabled={!selectedFile || isProcessing}
              className="w-full"
            >
              {isProcessing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processando PDF...
                </>
              ) : (
                <>
                  <ArrowUpOnSquareIcon className="h-4 w-4 mr-2" />
                  Processar PDF
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

          {/* Resultados do processamento */}
          {result && (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border dark:border-gray-700">
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
                Resultado do Processamento
              </h3>
              
              {/* Resumo */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{result.movements_created}</div>
                  <div className="text-sm text-green-700 dark:text-green-300">Movimentações Criadas</div>
                </div>
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{result.products_found}</div>
                  <div className="text-sm text-blue-700 dark:text-blue-300">Produtos Encontrados</div>
                </div>
                <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{result.products_not_found}</div>
                  <div className="text-sm text-red-700 dark:text-red-300">Produtos Não Encontrados</div>
                </div>
              </div>

              {/* Detalhes das movimentações */}
              {result.processed_movements && result.processed_movements.length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
                    Detalhes das Movimentações
                  </h4>
                  <div className="space-y-2">
                    {result.processed_movements.map((movement, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-lg border ${getStatusColor(movement.status)}`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            {getStatusIcon(movement.status)}
                            <span className="ml-2 font-medium">{movement.produto_nome}</span>
                          </div>
                          <div className="flex items-center gap-4">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              movement.tipo_movimentacao === 'ENTRADA' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {movement.tipo_movimentacao}
                            </span>
                            <span className="font-semibold">{movement.quantidade} unidades</span>
                          </div>
                        </div>
                        {movement.message && (
                          <p className="text-sm mt-2 opacity-75">{movement.message}</p>
                        )}
                        {movement.observacao && (
                          <p className="text-sm mt-1 italic">Obs: {movement.observacao}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </>
  );
}