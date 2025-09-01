'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Input from '@/components/Input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Upload, FileText, CheckCircle, AlertCircle, Package, TrendingDown, Eye } from 'lucide-react';
import { apiService } from '@/services/apiService';

interface ProdutoProcessado {
  codigo: string;
  nome: string;
  quantidade_saida: number;
  estoque_anterior: number;
  estoque_atual: number;
}

interface ProdutoSemEstoque {
  codigo: string;
  descricao: string;
  quantidade_solicitada: number;
  estoque_disponivel: number;
  erro: string;
}

interface ResultadoProcessamento {
  sucesso: boolean;
  arquivo: string;
  tipo: string;
  nota_fiscal?: string;
  data_emissao?: string;
  cliente?: string;
  cnpj_cliente?: string;
  movimentacoes_criadas: number;
  produtos_processados: ProdutoProcessado[];
  produtos_sem_estoque: ProdutoSemEstoque[];
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
  cliente?: string;
  cnpj_cliente?: string;
  produtos_encontrados: ProdutoPreview[];
  produtos_nao_encontrados: ProdutoPreview[];
  total_produtos_pdf: number;
}

export default function SaidaPage() {
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [processando, setProcessando] = useState(false);
  const [visualizando, setVisualizando] = useState(false);
  const [resultado, setResultado] = useState<ResultadoProcessamento | null>(null);
  const [previewData, setPreviewData] = useState<PreviewResult | null>(null);
  const [erro, setErro] = useState<string>('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === 'application/pdf') {
        setArquivo(file);
        setErro('');
      } else {
        setErro('Por favor, selecione apenas arquivos PDF.');
        setArquivo(null);
      }
    }
  };

  const handleVisualizarProdutos = async () => {
    if (!arquivo) {
      setErro('Por favor, selecione um arquivo PDF primeiro.');
      return;
    }

    setVisualizando(true);
    setErro('');
    setPreviewData(null);

    try {
      const formData = new FormData();
      formData.append('arquivo', arquivo);
      formData.append('tipo_movimentacao', 'SAIDA');

      const response = await apiService.postFormData('/movimentacoes/preview-pdf', formData);
      if (response) {
        setPreviewData(response.data);
      }
    } catch (error: unknown) {
      if (error instanceof Error) {
        setErro(`Erro ao visualizar produtos: ${error.message}`);
      } else {
        setErro('Erro desconhecido ao visualizar produtos');
      }
    } finally {
      setVisualizando(false);
    }
  };

  const handleProcessarPDF = async () => {
    if (!arquivo) {
      setErro('Por favor, selecione um arquivo PDF primeiro.');
      return;
    }

    setProcessando(true);
    setErro('');
    setResultado(null);
    setPreviewData(null);

    try {
      const formData = new FormData();
      formData.append('arquivo', arquivo);

      const response = await apiService.postFormData('/movimentacoes/saida/processar-pdf', formData);
      if (response) {
        setResultado(response.data);
      }
    } catch (error: unknown) {
      if (error instanceof Error) {
        setErro(`Erro ao processar PDF: ${error.message}`);
      } else {
        setErro('Erro desconhecido ao processar PDF');
      }
    } finally {
      setProcessando(false);
    }
  };

  const resetForm = () => {
    setArquivo(null);
    setResultado(null);
    setPreviewData(null);
    setErro('');
    setProcessando(false);
    setVisualizando(false);
    const fileInput = document.getElementById('pdf-file') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Saída de Estoque</h1>
          <p className="text-gray-600 mt-1">Processe notas fiscais de saída para baixar produtos do estoque automaticamente</p>
        </div>
        <div className="flex items-center space-x-2">
          <Package className="h-8 w-8 text-red-600" />
          <TrendingDown className="h-6 w-6 text-red-500" />
        </div>
      </div>

      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Upload className="h-5 w-5" />
            <span>Upload de Nota Fiscal de Saída</span>
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
              disabled={processando || visualizando}
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
              className="flex-1 bg-red-600 hover:bg-red-700"
            >
              {processando ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processando...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Processar Saída
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
                    <TrendingDown className="w-5 h-5 text-purple-600" />
                    <span className="font-medium text-purple-900">Cliente</span>
                  </div>
                  <p className="text-purple-700 mt-1">{previewData.cliente || 'N/A'}</p>
                </div>
              </div>

              {/* Produtos Encontrados */}
              {previewData.produtos_encontrados.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-green-800 mb-3 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5" />
                    Produtos Encontrados ({previewData.produtos_encontrados.length})
                  </h3>
                  <div className="space-y-3">
                    {previewData.produtos_encontrados.map((produto, index) => (
                      <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                          <div>
                            <p className="text-sm text-gray-600">Código</p>
                            <p className="font-medium">{produto.codigo}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Nome no Sistema</p>
                            <p className="font-medium">{produto.nome_sistema || produto.descricao_pdf}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Quantidade</p>
                            <p className="font-medium">{produto.quantidade}</p>
                            {produto.valor_unitario && (
                              <p className="text-sm text-gray-500">R$ {produto.valor_unitario.toFixed(2)}/un</p>
                            )}
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Estoque</p>
                            <p className={`font-medium ${
                              (produto.estoque_projetado || 0) < 0 ? 'text-red-600' : 'text-green-600'
                            }`}>
                              Atual: {produto.estoque_atual || 0} → Projetado: {produto.estoque_projetado || 0}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Produtos Não Encontrados */}
              {previewData.produtos_nao_encontrados.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-red-800 mb-3 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    Produtos Não Encontrados ({previewData.produtos_nao_encontrados.length})
                  </h3>
                  <div className="space-y-3">
                    {previewData.produtos_nao_encontrados.map((produto, index) => (
                      <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          <div>
                            <p className="text-sm text-gray-600">Código</p>
                            <p className="font-medium">{produto.codigo}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Descrição no PDF</p>
                            <p className="font-medium">{produto.descricao_pdf}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Quantidade</p>
                            <p className="font-medium">{produto.quantidade}</p>
                            {produto.valor_unitario && (
                              <p className="text-sm text-gray-500">R$ {produto.valor_unitario.toFixed(2)}/un</p>
                            )}
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

      {/* Resultado do Processamento */}
      {resultado && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                {resultado.sucesso ? (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-600" />
                )}
                <span>Resultado do Processamento</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                {resultado.nota_fiscal && (
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-blue-600 font-medium">Nota Fiscal</p>
                    <p className="text-blue-900">{resultado.nota_fiscal}</p>
                  </div>
                )}
                {resultado.data_emissao && (
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-sm text-green-600 font-medium">Data de Emissão</p>
                    <p className="text-green-900">{resultado.data_emissao}</p>
                  </div>
                )}
                {resultado.cliente && (
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <p className="text-sm text-purple-600 font-medium">Cliente</p>
                    <p className="text-purple-900">{resultado.cliente}</p>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 font-medium">Total de Produtos no PDF</p>
                  <p className="text-2xl font-bold text-gray-900">{resultado.total_produtos_pdf}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-sm text-green-600 font-medium">Movimentações Criadas</p>
                  <p className="text-2xl font-bold text-green-900">{resultado.movimentacoes_criadas}</p>
                </div>
                <div className="bg-red-50 p-4 rounded-lg">
                  <p className="text-sm text-red-600 font-medium">Produtos sem Estoque</p>
                  <p className="text-2xl font-bold text-red-900">{resultado.produtos_sem_estoque.length}</p>
                </div>
              </div>

              {/* Produtos Processados */}
              {resultado.produtos_processados.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-green-800 mb-3 flex items-center space-x-2">
                    <CheckCircle className="h-5 w-5" />
                    <span>Produtos Processados com Sucesso ({resultado.produtos_processados.length})</span>
                  </h3>
                  <div className="space-y-3">
                    {resultado.produtos_processados.map((produto, index) => (
                      <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                          <div>
                            <p className="text-sm text-gray-600">Código</p>
                            <p className="font-medium">{produto.codigo}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Nome</p>
                            <p className="font-medium">{produto.nome}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Quantidade Saída</p>
                            <p className="font-medium text-red-600">-{produto.quantidade_saida}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Estoque</p>
                            <p className="font-medium">{produto.estoque_anterior} → {produto.estoque_atual}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Produtos sem Estoque */}
              {resultado.produtos_sem_estoque.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-red-800 mb-3 flex items-center space-x-2">
                    <AlertCircle className="h-5 w-5" />
                    <span>Produtos sem Estoque Suficiente ({resultado.produtos_sem_estoque.length})</span>
                  </h3>
                  <Alert className="border-red-200 bg-red-50 mb-4">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-red-800">
                      Os produtos abaixo não puderam ser processados devido ao estoque insuficiente.
                    </AlertDescription>
                  </Alert>
                  <div className="space-y-3">
                    {resultado.produtos_sem_estoque.map((produto, index) => (
                      <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                          <div>
                            <p className="text-sm text-gray-600">Código</p>
                            <p className="font-medium">{produto.codigo}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Descrição</p>
                            <p className="font-medium">{produto.descricao}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Solicitado / Disponível</p>
                            <p className="font-medium text-red-600">{produto.quantidade_solicitada} / {produto.estoque_disponivel}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Erro</p>
                            <p className="font-medium text-red-600">{produto.erro}</p>
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
    </div>
  );
}