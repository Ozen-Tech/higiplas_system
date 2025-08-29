'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Input from '@/components/Input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Upload, FileText, CheckCircle, AlertCircle, Package, TrendingDown, AlertTriangle } from 'lucide-react';
import { apiService } from '@/services/apiService';
import { useAuth } from '@/contexts/AuthContext';

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

export default function SaidaPage() {
  const { user } = useAuth();
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

      const response = await apiService.postFormData('/movimentacoes/saida/processar-pdf', formData);
      if (response) {
        setResultado(response.data);
      }
    } catch (error: any) {
      console.error('Erro ao processar PDF:', error);
      setErro(error.response?.data?.detail || 'Erro ao processar o arquivo PDF.');
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
              className="bg-red-600 hover:bg-red-700"
            >
              {processando ? 'Processando...' : 'Processar Saída'}
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
                
                {resultado.cliente && (
                  <div className="space-y-1">
                    <p className="text-sm text-gray-600">Cliente</p>
                    <p className="font-medium">{resultado.cliente}</p>
                  </div>
                )}
              </div>
              
              <div className="border-t border-gray-200 my-4"></div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <p className="text-2xl font-bold text-red-600">{resultado.movimentacoes_criadas}</p>
                  <p className="text-sm text-red-800">Movimentações Criadas</p>
                </div>
                
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">{resultado.produtos_processados.length}</p>
                  <p className="text-sm text-blue-800">Produtos Processados</p>
                </div>
                
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <p className="text-2xl font-bold text-orange-600">{resultado.produtos_sem_estoque.length}</p>
                  <p className="text-sm text-orange-800">Produtos Sem Estoque</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Processed Products */}
          {resultado.produtos_processados.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-red-600">Produtos Processados com Sucesso</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2">Código</th>
                        <th className="text-left p-2">Nome</th>
                        <th className="text-right p-2">Qtd. Saída</th>
                        <th className="text-right p-2">Estoque Anterior</th>
                        <th className="text-right p-2">Estoque Atual</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resultado.produtos_processados.map((produto, index) => (
                        <tr key={index} className="border-b hover:bg-gray-50">
                          <td className="p-2 font-mono">{produto.codigo}</td>
                          <td className="p-2">{produto.nome}</td>
                          <td className="p-2 text-right font-medium text-red-600">-{produto.quantidade_saida}</td>
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

          {/* Products Without Stock */}
          {resultado.produtos_sem_estoque.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-orange-600 flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5" />
                  <span>Produtos Sem Estoque Suficiente</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-4 p-4 bg-orange-50 rounded-lg">
                  <p className="text-sm text-orange-800">
                    <strong>Atenção:</strong> Os produtos listados abaixo não puderam ser processados devido ao estoque insuficiente.
                    Verifique o estoque disponível antes de tentar processar novamente.
                  </p>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2">Código</th>
                        <th className="text-left p-2">Descrição</th>
                        <th className="text-right p-2">Qtd. Solicitada</th>
                        <th className="text-right p-2">Estoque Disponível</th>
                        <th className="text-left p-2">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resultado.produtos_sem_estoque.map((produto, index) => (
                        <tr key={index} className="border-b hover:bg-gray-50">
                          <td className="p-2 font-mono">{produto.codigo}</td>
                          <td className="p-2">{produto.descricao}</td>
                          <td className="p-2 text-right font-medium">{produto.quantidade_solicitada}</td>
                          <td className="p-2 text-right text-orange-600 font-medium">{produto.estoque_disponivel}</td>
                          <td className="p-2">
                            <Badge className="bg-orange-100 text-orange-800 border-orange-200">
                              {produto.erro}
                            </Badge>
                          </td>
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