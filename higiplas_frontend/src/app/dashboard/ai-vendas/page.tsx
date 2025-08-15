'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Brain, 
  FileText, 
  TrendingUp, 
  Package, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  BarChart3
} from 'lucide-react';
import { apiService } from '@/services/apiService';

interface TopProduct {
  produto: string;
  total_quantidade: number;
  total_valor: number;
  numero_vendas: number;
}

interface StockSuggestion {
  produto: string;
  estoque_atual?: number;
  estoque_minimo_sugerido: number;
  justificativa: string;
  aprovado: boolean;
  data_sugestao: string;
  admin_aprovador?: string;
  data_aprovacao?: string;
}

interface AIResponse {
  question: string;
  response: string;
  included_pdf_data: boolean;
  timestamp: string;
}

export default function AIVendasPage() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const [topProducts, setTopProducts] = useState<TopProduct[]>([]);
  const [stockSuggestions, setStockSuggestions] = useState<StockSuggestion[]>([]);
  const [aiResponse, setAiResponse] = useState<AIResponse | null>(null);
  const [question, setQuestion] = useState('');
  const [processingStatus, setProcessingStatus] = useState<string>('');
  const [error, setError] = useState<string>('');

  // Carrega dados iniciais
  useEffect(() => {
    loadTopProducts();
    loadPendingApprovals();
  }, []);

  const processPDFs = async () => {
    setIsProcessing(true);
    setError('');
    
    try {
      const response = await apiService.post('/ai-pdf/process-pdfs', {
        force_reprocess: false
      });
      
      setProcessingStatus(response.data.message);
      await loadTopProducts(); // Recarrega produtos após processamento
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Erro ao processar PDFs');
    } finally {
      setIsProcessing(false);
    }
  };

  const loadTopProducts = async () => {
    try {
      const response = await apiService.get('/ai-pdf/top-selling-products?limit=10');
      setTopProducts(response.data.products || []);
    } catch (err) {
      console.error('Erro ao carregar produtos:', err);
    }
  };

  const loadPendingApprovals = async () => {
    try {
      const response = await apiService.get('/ai-pdf/pending-stock-approvals');
      setStockSuggestions(response.data.suggestions || []);
    } catch (err) {
      console.error('Erro ao carregar aprovações:', err);
    }
  };

  const queryAI = async () => {
    if (!question.trim()) return;
    
    setIsQuerying(true);
    setError('');
    
    try {
      const response = await apiService.post('/ai-pdf/ai-query', {
        question: question,
        include_pdf_data: true
      });
      
      setAiResponse(response.data);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Erro ao consultar IA');
    } finally {
      setIsQuerying(false);
    }
  };

  const generateStockSuggestions = async () => {
    setIsProcessing(true);
    setError('');
    
    try {
      const response = await apiService.post('/ai-pdf/suggest-minimum-stocks?limit=10', {});
      setProcessingStatus(response.data.message);
      await loadPendingApprovals(); // Recarrega sugestões
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Erro ao gerar sugestões de estoque');
    } finally {
      setIsProcessing(false);
    }
  };

  const approveStockSuggestion = async (productName: string) => {
    try {
      const response = await apiService.post(`/ai-pdf/approve-stock-suggestion/${encodeURIComponent(productName)}`, {});
      setProcessingStatus(response.data.message);
      await loadPendingApprovals(); // Recarrega sugestões
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Erro ao aprovar sugestão');
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Brain className="h-8 w-8 text-blue-600" />
        <div>
          <h1 className="text-3xl font-bold">IA de Vendas e Estoque</h1>
          <p className="text-gray-600">Análise inteligente baseada em dados históricos (Maio-Julho 2025)</p>
        </div>
      </div>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {processingStatus && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{processingStatus}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="ai-chat" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="ai-chat">Chat com IA</TabsTrigger>
          <TabsTrigger value="top-products">Produtos Mais Vendidos</TabsTrigger>
          <TabsTrigger value="stock-suggestions">Sugestões de Estoque</TabsTrigger>
          <TabsTrigger value="settings">Configurações</TabsTrigger>
        </TabsList>

        <TabsContent value="ai-chat" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Consulte a IA Rozana
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Sua pergunta:</label>
                <Textarea
                  placeholder="Ex: Quais são os produtos mais vendidos nos últimos 3 meses? Qual o estoque mínimo recomendado para o produto X?"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  rows={3}
                />
              </div>
              
              <Button 
                onClick={queryAI} 
                disabled={isQuerying || !question.trim()}
                className="w-full"
              >
                {isQuerying ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Consultando IA...</>
                ) : (
                  <><Brain className="h-4 w-4 mr-2" /> Perguntar à IA</>
                )}
              </Button>

              {aiResponse && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg border">
                  <div className="flex items-center gap-2 mb-2">
                    <Brain className="h-4 w-4 text-blue-600" />
                    <span className="font-medium text-blue-800">Resposta da IA Rozana:</span>
                  </div>
                  <div className="whitespace-pre-wrap text-sm text-gray-700">
                    {aiResponse.response}
                  </div>
                  <div className="mt-2 text-xs text-gray-500">
                    Pergunta: {aiResponse.question} | {new Date(aiResponse.timestamp).toLocaleString()}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="top-products" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Produtos Mais Vendidos (Maio-Julho 2025)
              </CardTitle>
            </CardHeader>
            <CardContent>
              {topProducts.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Nenhum dado encontrado. Processe os PDFs primeiro.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {topProducts.map((product, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Badge variant="outline" className="text-xs">
                          #{index + 1}
                        </Badge>
                        <div>
                          <h3 className="font-medium">{product.produto}</h3>
                          <p className="text-sm text-gray-600">
                            {product.numero_vendas} vendas realizadas
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">{product.total_quantidade} unidades</p>
                        <p className="text-sm text-green-600">
                          R$ {product.total_valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stock-suggestions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5" />
                Sugestões de Estoque Mínimo
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button 
                onClick={generateStockSuggestions} 
                disabled={isProcessing}
                className="w-full"
              >
                {isProcessing ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Gerando Sugestões...</>
                ) : (
                  <><Package className="h-4 w-4 mr-2" /> Gerar Sugestões de Estoque</>
                )}
              </Button>

              {stockSuggestions.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Package className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Nenhuma sugestão pendente. Gere sugestões primeiro.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {stockSuggestions.map((suggestion, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium">{suggestion.produto}</h3>
                        <Badge 
                          variant={suggestion.aprovado ? "default" : "secondary"}
                        >
                          {suggestion.aprovado ? "Aprovado" : "Pendente"}
                        </Badge>
                      </div>
                      
                      <div className="space-y-2 text-sm text-gray-600">
                        <p><strong>Estoque mínimo sugerido:</strong> {suggestion.estoque_minimo_sugerido} unidades</p>
                        <p><strong>Justificativa:</strong> {suggestion.justificativa}</p>
                        <p><strong>Data da sugestão:</strong> {new Date(suggestion.data_sugestao).toLocaleString()}</p>
                        
                        {suggestion.aprovado && suggestion.admin_aprovador && (
                          <p><strong>Aprovado por:</strong> {suggestion.admin_aprovador} em {new Date(suggestion.data_aprovacao!).toLocaleString()}</p>
                        )}
                      </div>

                      {!suggestion.aprovado && (
                        <Button 
                          onClick={() => approveStockSuggestion(suggestion.produto)}
                          size="sm"
                          className="mt-3"
                        >
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Aprovar Sugestão
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Processamento de PDFs
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <h3 className="font-medium mb-2">Arquivos Disponíveis:</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• HIGIPLAS - MAIO - JULHO.pdf</li>
                  <li>• HIGITEC - MAIO - JULHO.pdf</li>
                </ul>
              </div>
              
              <Button 
                onClick={processPDFs} 
                disabled={isProcessing}
                className="w-full"
              >
                {isProcessing ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Processando PDFs...</>
                ) : (
                  <><FileText className="h-4 w-4 mr-2" /> Processar PDFs de Vendas</>
                )}
              </Button>
              
              <div className="text-sm text-gray-600">
                <p><strong>Período dos dados:</strong> 01/05/2025 a 31/07/2025</p>
                <p><strong>Funcionalidades:</strong></p>
                <ul className="list-disc list-inside mt-1 space-y-1">
                  <li>Extração automática de dados de vendas</li>
                  <li>Análise de produtos mais vendidos</li>
                  <li>Cálculo inteligente de estoque mínimo</li>
                  <li>Consultas à IA com contexto histórico</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}