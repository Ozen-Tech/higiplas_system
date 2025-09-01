'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Input from '@/components/Input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Upload, FileText, CheckCircle, AlertCircle, Package, TrendingUp, Eye } from 'lucide-react';
import { apiService } from '@/services/apiService';

interface ProdutoProcessado {
  codigo: string;
  nome: string;
  quantidade_entrada: number;
  estoque_anterior: number;
  estoque_atual: number;
}

interface ProdutoNaoEncontrado {
  codigo: string;
  descricao: string;
  quantidade: number;
  erro: string;
}

interface ResultadoProcessamento {
  sucesso: boolean;
  arquivo: string;
  tipo: string;
  nota_fiscal?: string;
  data_emissao?: string;
  fornecedor?: string;
  cnpj_fornecedor?: string;
  movimentacoes_criadas: number;
  produtos_processados: ProdutoProcessado[];
  produtos_nao_encontrados: ProdutoNaoEncontrado[];
  total_produtos_pdf: number;
}

interface ProdutoPreview {
  codigo: string;
  descricao_pdf: string;
  quantidade: number;
  valor_unitario?: number;
  valor_total?: number;
  encontrado: boolean;
  produto_id?: number;
  nome_sistema?: string;
  estoque_atual?: number;
  estoque_projetado?: number;
  produtos_similares?: { id: number; nome: string; codigo: string; }[];
}

interface PreviewResult {
  sucesso: boolean;
  arquivo: string;
  tipo_movimentacao: string;
  nota_fiscal?: string;
  data_emissao?: string;
  fornecedor?: string;
  cnpj_fornecedor?: string;
  produtos_encontrados: ProdutoPreview[];
  produtos_nao_encontrados: ProdutoPreview[];
  total_produtos_pdf: number;
}

export default function EntradaPage() {
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [processando, setProcessando] = useState(false);
  const [visualizando, setVisualizando] = useState(false);
  const [resultado, setResultado] = useState<ResultadoProcessamento | null>(null);
  const [previewData, setPreviewData] = useState<PreviewResult | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === 'application/pdf') {
        setArquivo(file);
        setErro(null);
      } else {
        setErro('Por favor, selecione apenas arquivos PDF.');
        setArquivo(null);
      }
    }
  };

  const handleVisualizarProdutos = async () => {
    if (!arquivo) {
      setErro('Por favor, selecione um arquivo PDF.');
      return;
    }

    setVisualizando(true);
    setErro(null);
    setPreviewData(null);

    try {
      const formData = new FormData();
      formData.append('arquivo', arquivo);
      formData.append('tipo_movimentacao', 'ENTRADA');

      const response = await apiService.postFormData('/movimentacoes/preview-pdf', formData);
      if (response) {
        setPreviewData(response.data);
      }
    } catch (error: unknown) {
      console.error('Erro ao visualizar produtos:', error);
      const errorMessage = error && typeof error === 'object' && 'response' in error 
        ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail 
        : 'Erro ao analisar o arquivo PDF.';
      setErro(errorMessage || 'Erro ao analisar o arquivo PDF.');
    } finally {
      setVisualizando(false);
    }
  };

  const handleProcessarPDF = async () => {
    if (!arquivo) {
      setErro('Por favor, selecione um arquivo PDF.');
      return;
    }

    setProcessando(true);
    setErro(null);
    setResultado(null);

    try {
      const formData = new FormData();
      formData.append('arquivo', arquivo);

      const response = await apiService.postFormData('/movimentacoes/entrada/processar-pdf', formData);
      if (response) {
        setResultado(response.data);
        setPreviewData(null); // Limpar preview após processar
      }
    } catch (error: unknown) {
      console.error('Erro ao processar PDF:', error);
      const errorMessage = error && typeof error === 'object' && 'response' in error 
        ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail 
        : 'Erro ao processar o arquivo PDF.';
      setErro(errorMessage || 'Erro ao processar o arquivo PDF.');
    } finally {
      setProcessando(false);
    }
  };

  const resetForm = () => {
    setArquivo(null);
    setResultado(null);
    setPreviewData(null);
    setErro(null);
    // Reset file input
    const fileInput = document.getElementById('pdf-file') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Entrada de Estoque</h1>
          <p className="text-gray-600 mt-1">Processe notas fiscais de entrada para atualizar o estoque automaticamente</p>
        </div>
        <div className="flex items-center space-x-2">
          <Package className="h-8 w-8 text-green-600" />
          <TrendingUp className="h-6 w-6 text-green-500" />
        </div>
      </div>

      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Upload className="h-5 w-5" />
            <span>Upload de Nota Fiscal de Entrada</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Input
              label="Selecione o arquivo PDF da nota fiscal"
              id="pdf-file"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={processando}
            />
          </div>

          {arquivo && (
            <div className="flex items-center space-x-2 p-3 bg-blue-50 rounded-lg">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="text-sm text-blue-800">{arquivo.name}</span>
              <Badge variant="secondary">{(arquivo.size / 1024 / 1024).toFixed(2)} MB</Badge>
            </div>
          )}

          {erro && (
            <Alert className="border-red-200 bg-red-50 text-red-800">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{erro}</AlertDescription>
            </Alert>
          )}

          <div className="flex gap-4">
            <Button 
              onClick={handleVisualizarProdutos} 
              disabled={!arquivo || visualizando || processando}
              variant="outline"
              className="flex-1"
            >
              {visualizando ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
                  Analisando...
                </>
              ) : (
                <>
                  <Eye className="w-4 h-4 mr-2" />
                  Visualizar Produtos
                </>
              )}
            </Button>
            <Button 
              onClick={handleProcessarPDF} 
              disabled={!arquivo || processando || visualizando}
              className="flex-1 bg-green-600 hover:bg-green-700"
            >
              {processando ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processando...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Processar Entrada
                </>
              )}
            </Button>
            <Button 
              onClick={resetForm} 
              variant="outline"
              disabled={processando || visualizando}
            >
              Resetar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Preview dos Produtos */}
      {previewData && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="w-5 h-5" />
                Visualização dos Produtos
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-blue-600" />
                    <span className="font-medium text-blue-900">Nota Fiscal</span>
                  </div>
                  <p className="text-blue-700 mt-1">{previewData.nota_fiscal || 'N/A'}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Package className="w-5 h-5 text-green-600" />
                    <span className="font-medium text-green-900">Total de Produtos</span>
                  </div>
                  <p className="text-green-700 mt-1">{previewData.total_produtos_pdf}</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-purple-600" />
                    <span className="font-medium text-purple-900">Fornecedor</span>
                  </div>
                  <p className="text-purple-700 mt-1">{previewData.fornecedor || 'N/A'}</p>
                </div>
              </div>

              {previewData.produtos_encontrados.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    Produtos Encontrados ({previewData.produtos_encontrados.length})
                  </h3>
                  <div className="space-y-2">
                    {previewData.produtos_encontrados.map((produto, index) => (
                      <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <Badge variant="secondary">{produto.codigo}</Badge>
                              <span className="font-medium">{produto.nome_sistema}</span>
                            </div>
                            <p className="text-sm text-gray-600 mb-2">{produto.descricao_pdf}</p>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <span className="font-medium">Quantidade:</span>
                                <p>{produto.quantidade}</p>
                              </div>
                              {produto.valor_unitario && (
                                <div>
                                  <span className="font-medium">Valor Unit.:</span>
                                  <p>R$ {produto.valor_unitario.toFixed(2)}</p>
                                </div>
                              )}
                              <div>
                                <span className="font-medium">Estoque Atual:</span>
                                <p>{produto.estoque_atual || 0}</p>
                              </div>
                              <div>
                                <span className="font-medium">Estoque Projetado:</span>
                                <p className="text-green-600 font-medium">{produto.estoque_projetado || 0}</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {previewData.produtos_nao_encontrados.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-red-600" />
                    Produtos Não Encontrados ({previewData.produtos_nao_encontrados.length})
                  </h3>
                  <div className="space-y-2">
                    {previewData.produtos_nao_encontrados.map((produto, index) => (
                      <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <Badge variant="destructive">{produto.codigo}</Badge>
                            </div>
                            <p className="text-sm text-gray-600 mb-2">{produto.descricao_pdf}</p>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <span className="font-medium">Quantidade:</span>
                                <p>{produto.quantidade}</p>
                              </div>
                              {produto.valor_unitario && (
                                <div>
                                  <span className="font-medium">Valor Unit.:</span>
                                  <p>R$ {produto.valor_unitario.toFixed(2)}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Results Section */}
      {resultado && (
        <div className="space-y-4">
          {/* Summary Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span>Resultado do Processamento</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="space-y-1">
                  <p className="text-sm text-gray-600">Arquivo</p>
                  <p className="font-medium">{resultado.arquivo}</p>
                </div>
                
                {resultado.nota_fiscal && (
                  <div className="space-y-1">
                    <p className="text-sm text-gray-600">Nota Fiscal</p>
                    <p className="font-medium">{resultado.nota_fiscal}</p>
                  </div>
                )}
                
                {resultado.data_emissao && (
                  <div className="space-y-1">
                    <p className="text-sm text-gray-600">Data de Emissão</p>
                    <p className="font-medium">{resultado.data_emissao}</p>
                  </div>
                )}
                
                {resultado.fornecedor && (
                  <div className="space-y-1">
                    <p className="text-sm text-gray-600">Fornecedor</p>
                    <p className="font-medium">{resultado.fornecedor}</p>
                  </div>
                )}
              </div>
              
              <div className="border-t border-gray-200 my-4"></div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{resultado.movimentacoes_criadas}</p>
                  <p className="text-sm text-green-800">Movimentações Criadas</p>
                </div>
                
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">{resultado.produtos_processados.length}</p>
                  <p className="text-sm text-blue-800">Produtos Processados</p>
                </div>
                
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <p className="text-2xl font-bold text-orange-600">{resultado.produtos_nao_encontrados.length}</p>
                  <p className="text-sm text-orange-800">Produtos Não Encontrados</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Processed Products */}
          {resultado.produtos_processados.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-green-600">Produtos Processados com Sucesso</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2">Código</th>
                        <th className="text-left p-2">Nome</th>
                        <th className="text-right p-2">Qtd. Entrada</th>
                        <th className="text-right p-2">Estoque Anterior</th>
                        <th className="text-right p-2">Estoque Atual</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resultado.produtos_processados.map((produto, index) => (
                        <tr key={index} className="border-b hover:bg-gray-50">
                          <td className="p-2 font-mono">{produto.codigo}</td>
                          <td className="p-2">{produto.nome}</td>
                          <td className="p-2 text-right font-medium text-green-600">+{produto.quantidade_entrada}</td>
                          <td className="p-2 text-right">{produto.estoque_anterior}</td>
                          <td className="p-2 text-right font-medium">{produto.estoque_atual}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Products Not Found */}
          {resultado.produtos_nao_encontrados.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-orange-600">Produtos Não Encontrados</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2">Código</th>
                        <th className="text-left p-2">Descrição</th>
                        <th className="text-right p-2">Quantidade</th>
                        <th className="text-left p-2">Erro</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resultado.produtos_nao_encontrados.map((produto, index) => (
                        <tr key={index} className="border-b hover:bg-gray-50">
                          <td className="p-2 font-mono">{produto.codigo}</td>
                          <td className="p-2">{produto.descricao}</td>
                          <td className="p-2 text-right">{produto.quantidade}</td>
                          <td className="p-2 text-orange-600">{produto.erro}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}