"use client";

import { useState, useRef, useEffect } from "react";
import { apiService } from "@/services/apiService";
import { Header } from "@/components/dashboard/Header";
import ClientLayout from "@/components/ClientLayout";
import ReactMarkdown from 'react-markdown';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Send, Bot, User, Loader2, Sparkles, Trash2, Copy } from 'lucide-react';
import toast from 'react-hot-toast';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

function InsightsPageContent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickQuestions = [
    "Quais produtos estão com estoque crítico?",
    "Quais são os 5 produtos mais vendidos?",
    "Quais produtos precisam de reposição urgente?",
    "Analise a rotatividade de estoque",
    "Sugira compras prioritárias",
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (question?: string) => {
    const questionToSend = question || input.trim();
    if (!questionToSend) return;

    // Adiciona mensagem do usuário
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: questionToSend,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    
    try {
      const response = await apiService.post('/insights/ask', { question: questionToSend });
      const answer = response?.data?.answer || 'Resposta não disponível';

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: answer,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: unknown) {
      let errorMessage = "Erro desconhecido ao processar a pergunta.";
      
      if (err && typeof err === 'object' && 'response' in err) {
        const error = err as { response?: { status?: number; data?: { detail?: string } } };
        
        if (error.response?.status === 429) {
          errorMessage = "⚠️ **Limite de requisições excedido**\n\nO limite de requisições da API foi excedido. Por favor, aguarde alguns minutos antes de tentar novamente.";
        } else if (error.response?.status === 403) {
          errorMessage = "🔒 **Problema de permissão**\n\nProblema de permissão na API. Entre em contato com o administrador do sistema.";
        } else if (error.response?.status === 400) {
          errorMessage = "📝 **Requisição inválida**\n\nO contexto enviado é muito grande. Tente fazer uma pergunta mais específica ou focada em menos produtos.";
        } else if (error.response?.data?.detail) {
          errorMessage = `❌ **Erro**: ${error.response.data.detail}`;
        }
      } else if (err instanceof Error) {
        errorMessage = `❌ **Erro**: ${err.message}`;
      }

      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: errorMessage,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMsg]);
    } finally {
       setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copiado para a área de transferência!');
  };

  const clearChat = () => {
    setMessages([]);
    toast.success('Conversa limpa!');
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <Header>
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                Rozana - Analista de Estoque
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Assistente inteligente para análise de estoque
              </p>
            </div>
          </div>
          {messages.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={clearChat}
              className="flex items-center gap-2"
            >
              <Trash2 className="h-4 w-4" />
              Limpar
            </Button>
          )}
        </div>
      </Header>

      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Área de mensagens */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              <div className="p-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mb-4">
                <Bot className="h-12 w-12 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                Olá! Sou a Rozana 👋
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">
                Seu analista inteligente de estoque. Faça perguntas sobre produtos, vendas, estoque mínimo e muito mais!
              </p>
              
              <div className="w-full max-w-2xl">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Perguntas rápidas:
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {quickQuestions.map((q, idx) => (
                    <Button
                      key={idx}
                      variant="outline"
                      className="justify-start text-left h-auto py-3 px-4 hover:bg-blue-50 dark:hover:bg-gray-800 hover:border-blue-500 transition-all"
                      onClick={() => handleSend(q)}
                    >
                      <span className="text-sm">{q}</span>
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto w-full space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                        <Bot className="h-5 w-5 text-white" />
                      </div>
                    </div>
                  )}

                  <div
                    className={`flex flex-col gap-1 max-w-[80%] ${
                      message.role === 'user' ? 'items-end' : 'items-start'
                    }`}
                  >
                    <Card
                      className={`p-4 ${
                        message.role === 'user'
                          ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                          : 'bg-white dark:bg-gray-800'
                      }`}
                    >
                      {message.role === 'assistant' ? (
                        <div className="prose dark:prose-invert max-w-none prose-sm">
                          <ReactMarkdown
                            components={{
                              p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                              ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                              ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                              li: ({ children }) => <li className="ml-2">{children}</li>,
                              strong: ({ children }) => <strong className="font-bold text-gray-900 dark:text-gray-100">{children}</strong>,
                              code: ({ children }) => (
                                <code className="bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded text-sm">
                                  {children}
                                </code>
                              ),
                            }}
                          >
                            {message.content}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <p className="text-white">{message.content}</p>
                      )}
                    </Card>

                    {message.role === 'assistant' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 px-2 text-xs"
                        onClick={() => copyToClipboard(message.content)}
                      >
                        <Copy className="h-3 w-3 mr-1" />
                        Copiar
                      </Button>
                    )}

                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {message.timestamp.toLocaleTimeString('pt-BR', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
           </div>
           
                  {message.role === 'user' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-400 to-gray-500 flex items-center justify-center">
                        <User className="h-5 w-5 text-white" />
                      </div>
                    </div>
                )}
             </div>
              ))}

              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                      <Bot className="h-5 w-5 text-white" />
                    </div>
                  </div>
                  <Card className="p-4 bg-white dark:bg-gray-800">
                    <div className="flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Analisando...
                      </span>
                    </div>
                  </Card>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input area */}
        <div className="border-t bg-white dark:bg-gray-800 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-2">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Digite sua pergunta sobre estoque, vendas, produtos..."
                className="min-h-[60px] max-h-[120px] resize-none"
                disabled={isLoading}
              />
              <Button
                onClick={() => handleSend()}
                disabled={isLoading || !input.trim()}
                className="self-end"
                size="lg"
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </Button>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 ml-1">
              Pressione Enter para enviar, Shift+Enter para nova linha
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

// Wrapper de proteção da rota
export default function InsightsPageWrapper() {
  return <ClientLayout><InsightsPageContent /></ClientLayout>;
}
