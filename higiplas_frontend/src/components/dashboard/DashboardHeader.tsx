// /src/app/components/dashboard/DashboardHeader.tsx

"use client";

import Image from "next/image";
import UploadExcel from "@/components/UploadExcel";
import { ThemeToggleButton } from "@/components/ThemeToggleButton";
import { useState } from "react";

// Estilos...
const baseButtonClasses = "px-4 py-2 text-sm font-semibold rounded-lg shadow-md transition duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2";
const newProductButtonClasses = baseButtonClasses + " bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500";
const downloadButtonClasses = baseButtonClasses + " bg-gray-600 dark:bg-gray-700 text-white hover:bg-gray-700 dark:hover:bg-gray-600 focus:ring-gray-500 disabled:opacity-50";
const logoutButtonClasses = baseButtonClasses + " bg-red-500 text-white hover:bg-red-700 focus:ring-red-500"; // Adicionei para consistência

interface DashboardHeaderProps {
  onNewProductClick: () => void;
  onUploadSuccess: () => void;
  onLogoutClick: () => void;
}

export function DashboardHeader({ onNewProductClick, onUploadSuccess, onLogoutClick }: DashboardHeaderProps) {
  const [isDownloading, setIsDownloading] = useState(false);
  
  const handleDownloadExcel = async () => {
    setIsDownloading(true);
    const token = localStorage.getItem("authToken");
    if (!token) {
        alert("Sessão expirada. Faça login novamente.");
        setIsDownloading(false);
        onLogoutClick(); // Chama a função de logout se não houver token
        return;
    }
    try {
        const response = await fetch("http://localhost:8000/produtos/download/excel", {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        // --- AQUI ESTÁ A LÓGICA CORRIGIDA ---
        if (response.status === 401) {
            alert("Sua sessão expirou. Você será redirecionado para a tela de login.");
            onLogoutClick(); // Chama a função de logout passada pelo pai
            return;
        }

        if (!response.ok) {
            // Tenta ler o erro do corpo da resposta, mesmo que seja um erro diferente de 401
            const errorData = await response.json().catch(() => ({ detail: "Erro desconhecido ao gerar o arquivo." }));
            throw new Error(errorData.detail);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "higiplas_produtos_estoque.xlsx";
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (err: any) {
        alert(`Erro no download: ${err.message}`);
    } finally {
        setIsDownloading(false);
    }
  };

  return (
    <div className="flex flex-wrap items-center justify-between mb-6 gap-4">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100">
        Produtos
      </h1>
      <div className="flex items-center gap-2 flex-wrap">
        <button onClick={handleDownloadExcel} disabled={isDownloading} className={downloadButtonClasses}>
          {isDownloading ? "Gerando..." : "Exportar"}
        </button>
        <UploadExcel onUploadSuccess={onUploadSuccess} />
        <button onClick={onNewProductClick} className={newProductButtonClasses}>
          + Adicionar Produto
        </button>
      </div>
    </div>
  );
}