'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Input from '@/components/Input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Upload, FileText, CheckCircle, AlertCircle, Package, TrendingUp } from 'lucide-react';
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

export default function EntradaPage() {
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [processando, setProcessando] = useState(false);
  const [resultado, setResultado] = useState<ResultadoProcessamento | null>(null);
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

          <div className="flex space-x-3">
            <Button
              onClick={handleProcessarPDF}
              disabled={!arquivo || processando}
              className="bg-green-600 hover:bg-green-700"
            >
              {processando ? 'Processando...' : 'Processar Entrada'}
            </Button>
            
            {(resultado || erro) && (
              <Button variant="outline" onClick={resetForm}>
                Novo Arquivo
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

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