// /src/app/dashboard/orcamentos/importar/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeftIcon, ArrowUpOnSquareIcon, CheckCircleIcon, ExclamationTriangleIcon, PlusCircleIcon, DocumentMagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { apiService } from '@/services/apiService';
import toast from 'react-hot-toast';
import { OrcamentoItem, Product } from '@/types'; // Supondo que você tenha esses tipos

// Definições de tipo para os dados da NF-e
interface MatchedProduct {
  produto_id: number;
  nome_db: string;
  descricao_nf: string;
  quantidade: number;
  estoque_atual: number;
  preco_venda: number;
}
interface UnmatchedProduct {
  descricao_nf: string;
  quantidade: number;
}
interface ParsedInvoiceData {
  matched: MatchedProduct[];
  unmatched: UnmatchedProduct[];
}

export default function ImportarNotaPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [parsedData, setParsedData] = useState<ParsedInvoiceData | null>(null);
  const [cliente, setCliente] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
    }
  };

  const handleParseInvoice = async () => {
    if (!file) {
      toast.error("Por favor, selecione um arquivo de imagem da NF-e.");
      return;
    }
    setIsProcessing(true);
    setParsedData(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    const promise = apiService.post('/invoices/parse-and-match', formData);

    toast.promise(promise, {
      loading: 'Analisando nota fiscal com IA...',
      success: (data) => {
        setParsedData(data);
        setIsProcessing(false);
        return 'Nota fiscal analisada com sucesso!';
      },
      error: (err) => {
        setIsProcessing(false);
        return `Erro na análise: ${err.message}`;
      }
    });
  };

  const handleCreateAndFinalize = async () => {
    if (!parsedData || parsedData.matched.length === 0 || !cliente) {
      toast.error("É necessário ter um cliente e ao menos um produto associado para finalizar.");
      return;
    }
    
    setIsProcessing(true);
    
    // 1. Criar o corpo do orçamento
    const orcamentoPayload = {
      nome_cliente: cliente,
      itens: parsedData.matched.map(p => ({
        produto_id: p.produto_id,
        quantidade: p.quantidade
      }))
    };

    try {
      // 2. Criar o orçamento (venda)
      const orcamentoCriado = await toast.promise(
        apiService.post('/orcamentos/', orcamentoPayload),
        {
          loading: 'Criando registro de venda...',
          success: 'Registro criado com sucesso!',
          error: 'Falha ao criar o registro.'
        }
      );

      // 3. Finalizar o orçamento para dar baixa no estoque
      await toast.promise(
        apiService.post(`/orcamentos/${orcamentoCriado.id}/finalizar`, {}),
        {
          loading: 'Dando baixa no estoque...',
          success: 'Baixa no estoque realizada com sucesso!',
          error: 'Falha ao dar baixa no estoque.'
        }
      );
      
      router.push(`/dashboard/orcamentos/${orcamentoCriado.id}`);

    } catch (error) {
      console.error(error);
    } finally {
      setIsProcessing(false);
    }
  };


  return (
    <div className="p-4 md:p-8 space-y-6">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-sm font-semibold text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
        <ArrowLeftIcon className="h-5 w-5" />
        Voltar
      </button>

      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border dark:border-gray-700">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Dar Baixa no Estoque por NF-e</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">Faça o upload de uma imagem (foto ou print) da nota fiscal para que a IA extraia os produtos.</p>
        
        <div className="flex flex-col md:flex-row items-center gap-4 p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
          <label htmlFor="invoice-upload" className="flex-1 w-full flex items-center justify-center px-4 py-6 bg-gray-50 dark:bg-gray-700/50 rounded-md cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
            <div className="text-center">
              <ArrowUpOnSquareIcon className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                <span className="font-semibold text-indigo-600 dark:text-indigo-400">Clique para enviar</span> ou arraste o arquivo
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">PNG, JPG, JPEG</p>
            </div>
            <input id="invoice-upload" name="invoice-upload" type="file" className="sr-only" accept="image/png, image/jpeg" onChange={handleFileChange} />
          </label>
          <div className="flex-shrink-0 w-full md:w-auto text-center md:text-left">
            {fileName && <p className="text-sm font-medium text-gray-700 dark:text-gray-200">Arquivo: <span className="font-normal text-gray-500">{fileName}</span></p>}
            <button onClick={handleParseInvoice} disabled={!file || isProcessing} className="mt-2 w-full md:w-auto inline-flex items-center justify-center gap-2 px-6 py-2 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700 disabled:bg-indigo-400 disabled:cursor-not-allowed transition-colors">
              <DocumentMagnifyingGlassIcon className="h-5 w-5" />
              {isProcessing ? 'Analisando...' : 'Analisar Nota'}
            </button>
          </div>
        </div>
      </div>

      {parsedData && (
         <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border dark:border-gray-700 animate-fadeIn">
            <h2 className="text-xl font-bold mb-4">Confirmação de Itens</h2>
            
            <div className="mb-6">
                <label htmlFor="cliente" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Nome do Cliente / Destino</label>
                <input type="text" name="cliente" id="cliente" value={cliente} onChange={(e) => setCliente(e.target.value)} className="mt-1 block w-full md:w-1/2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm p-2" required placeholder="Ex: Venda para Agromina"/>
            </div>

            {/* Itens Associados */}
            <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 flex items-center gap-2"><CheckCircleIcon className="h-6 w-6" /> Itens Associados ({parsedData.matched.length})</h3>
            <div className="overflow-x-auto mt-2">
               <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  {/* ... thead ... */}
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {parsedData.matched.map(item => (
                       <tr key={item.produto_id}>
                         <td className="px-4 py-3 text-sm">{item.nome_db} <span className="text-xs text-gray-400 block">NF: {item.descricao_nf}</span></td>
                         <td className="px-4 py-3 text-sm text-center">{item.quantidade}</td>
                       </tr>
                    ))}
                  </tbody>
               </table>
            </div>

            {/* Itens Não Associados */}
            {parsedData.unmatched.length > 0 && (
                <div className="mt-6">
                    <h3 className="text-lg font-semibold text-yellow-600 dark:text-yellow-400 flex items-center gap-2"><ExclamationTriangleIcon className="h-6 w-6" /> Itens Não Encontrados ({parsedData.unmatched.length})</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Estes itens não foram encontrados no seu estoque. Verifique se o nome está correto ou cadastre-os.</p>
                     <ul className="mt-2 list-disc list-inside text-sm text-gray-600 dark:text-gray-300">
                        {parsedData.unmatched.map((item, index) => <li key={index}>{item.descricao_nf} (Qtd: {item.quantidade})</li>)}
                     </ul>
                </div>
            )}
            
            <div className="mt-8 flex justify-end">
                <button onClick={handleCreateAndFinalize} disabled={isProcessing || !cliente || parsedData.matched.length === 0} className="w-full md:w-auto inline-flex items-center justify-center gap-2 px-6 py-2 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700 disabled:bg-green-400 disabled:cursor-not-allowed transition-colors">
                  <PlusCircleIcon className="h-5 w-5" />
                  {isProcessing ? 'Processando...' : 'Confirmar e Dar Baixa no Estoque'}
                </button>
            </div>
         </div>
      )}
    </div>
  );
}