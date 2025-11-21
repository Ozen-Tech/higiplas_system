"use client";

import { useState } from "react";
import { apiService } from "@/services/apiService";
import { Header } from "@/components/dashboard/Header";
import ClientLayout from "@/components/ClientLayout";
import ReactMarkdown from 'react-markdown';

function InsightsPageContent() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleAsk = async () => {
    if (!question.trim()) return;
    
    setIsLoading(true);
    setAnswer("");
    
    try {
      const response = await apiService.post('/insights/ask', { question });
      setAnswer(response?.data?.answer || 'Resposta não disponível');
    } catch (err: any) {
      // Trata erros específicos da API
      let errorMessage = "Erro desconhecido ao processar a pergunta.";
      
      if (err?.response?.status === 429) {
        errorMessage = "⚠️ **Limite de requisições excedido**\n\nO limite de requisições da API foi excedido. Por favor, aguarde alguns minutos antes de tentar novamente.";
      } else if (err?.response?.status === 403) {
        errorMessage = "🔒 **Problema de permissão**\n\nProblema de permissão na API. Entre em contato com o administrador do sistema.";
      } else if (err?.response?.status === 400) {
        errorMessage = "📝 **Requisição inválida**\n\nO contexto enviado é muito grande. Tente fazer uma pergunta mais específica ou focada em menos produtos.";
      } else if (err?.response?.data?.detail) {
        errorMessage = `❌ **Erro**: ${err.response.data.detail}`;
      } else if (err instanceof Error) {
        errorMessage = `❌ **Erro**: ${err.message}`;
      }
      
      setAnswer(errorMessage);
    } finally {
       setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
      <Header>
        <h1 className="text-xl font-bold">Assistente de Análise Higiplas</h1>
        {/* Adicione mais ações se necessário */}
      </Header>
      <main className="flex-1 p-6 overflow-y-auto">
        <div className="max-w-4xl mx-auto space-y-6">
           
           {/* Campo de Pergunta */}
           <div className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md">
             <h2 className="text-lg font-semibold mb-2">Faça sua pergunta:</h2>
             <textarea
               value={question}
               onChange={(e) => setQuestion(e.target.value)}
               placeholder="Ex: Quais são os 3 produtos com menor estoque? Gere um alerta para o produto que mais vendeu no último período."
               className="w-full h-24 p-3 border rounded-md bg-gray-50 dark:bg-gray-700 border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-blue-500"
             />
             <button onClick={handleAsk} disabled={isLoading} className="mt-3 w-full sm:w-auto px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 disabled:opacity-50">
               {isLoading ? "Analisando..." : "Perguntar à IA"}
             </button>
           </div>
           
           {/* Campo de Resposta */}
           {(isLoading || answer) && (
             <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md animate-fadeIn">
                <h2 className="text-lg font-semibold mb-3">Resposta do Assistente:</h2>
                {isLoading && <p>Pensando...</p>}
                {answer && (
                   // Usar ReactMarkdown para renderizar a formatação da IA
                   <article className="prose dark:prose-invert max-w-none">
                       <ReactMarkdown>{answer}</ReactMarkdown>
                   </article>
                )}
             </div>
           )}

        </div>
      </main>
    </div>
  );
}

// Wrapper de proteção da rota
export default function InsightsPageWrapper() {
   return <ClientLayout><InsightsPageContent /></ClientLayout>
}