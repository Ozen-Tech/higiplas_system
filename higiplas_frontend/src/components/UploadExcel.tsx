"use client";

import { useState } from "react";

// --- 1. DEFINIR A INTERFACE PARA AS PROPS ---
// Dizemos ao TypeScript que este componente espera receber uma função
// chamada 'onUploadSuccess' que não recebe argumentos e não retorna nada.
interface UploadExcelProps {
  onUploadSuccess: () => void;
}

// --- 2. USAR A INTERFACE NO COMPONENTE ---
// Usamos a interface para tipar as props que o componente recebe.
export default function UploadExcel({ onUploadSuccess }: UploadExcelProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMessage(null);
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage("Por favor, selecione um arquivo Excel.");
      return;
    }

    setLoading(true);
    setMessage(null);

    const token = localStorage.getItem("authToken");
    if (!token) {
      setMessage("Sessão expirada. Faça login novamente.");
      setLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload-excel", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const resultData = await response.json();

      if (!response.ok) {
        // Usa a mensagem de erro do backend se existir
        const errorMessage = resultData.detail || resultData.message || "Erro ao enviar arquivo.";
        throw new Error(errorMessage);
      }
      
      setMessage(resultData.message || "Arquivo enviado com sucesso!");
      setFile(null);
      // Limpa o input do arquivo para permitir o mesmo upload novamente
      if (document.getElementById("fileInput")) {
        (document.getElementById("fileInput") as HTMLInputElement).value = "";
      }

      // --- 3. CHAMAR A FUNÇÃO RECEBIDA VIA PROPS ---
      // Este é o passo crucial que notifica o componente pai (DashboardPage)
      // para recarregar a lista de produtos.
      onUploadSuccess();

    } catch (err) {
      // Correção aqui:
      if (err instanceof Error) {
        setMessage(`Erro: ${err.message}`);
      } else {
        setMessage('Ocorreu um erro desconhecido.');
      }
    } finally {
      setLoading(false);
    }
  };

  // O JSX (a parte visual) continua o mesmo.
  return (
    <div className="flex flex-col space-y-2">
      <label
        htmlFor="fileInput"
        className="cursor-pointer block text-sm font-semibold text-gray-700"
      >
        Selecionar arquivo Excel
      </label>
      <input
        id="fileInput"
        type="file"
        accept=".xls,.xlsx"
        onChange={handleFileChange}
        className="block w-full text-sm text-gray-500
          file:mr-4 file:py-2 file:px-4
          file:rounded-lg file:border-0
          file:text-sm file:font-semibold
          file:bg-gradient-to-r file:from-green-400 file:to-green-600
          file:text-white
          hover:file:from-green-500 hover:file:to-green-700
          transition
        "
      />
      <button
        onClick={handleUpload}
        disabled={loading}
        className={`px-5 py-2.5 font-semibold rounded-lg shadow-md transition duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2
          bg-gradient-to-r from-green-400 to-green-600 text-white hover:from-green-500 hover:to-green-700 shadow-green-300 focus:ring-green-400
          ${loading ? "opacity-50 cursor-not-allowed" : ""}
        `}
      >
        {loading ? "Enviando..." : "Enviar"}
      </button>
      {message && (
        <p
          className={`text-sm font-medium ${
            message.startsWith("Erro") ? "text-red-600" : "text-green-600"
          }`}
        >
          {message}
        </p>
      )}
    </div>
  );
}