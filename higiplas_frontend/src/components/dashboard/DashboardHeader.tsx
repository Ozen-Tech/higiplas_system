// /src/components/dashboard/DashboardHeader.tsx

"use client";

import { useState } from "react";
import Image from "next/image"; // Importando para usar o logo otimizado
import UploadExcel from "@/components/UploadExcel";
import { ThemeToggleButton } from "@/components/ThemeToggleButton"; // Importando o botão de tema

// --- ESTILOS ---
const baseButtonClasses = "px-4 py-2 text-sm font-semibold rounded-lg shadow-md transition duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2";
const newProductButtonClasses = baseButtonClasses + " bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 shadow-blue-300 focus:ring-blue-500";
const downloadButtonClasses = baseButtonClasses + " bg-gradient-to-r from-gray-500 to-gray-600 text-white hover:from-gray-600 hover:to-gray-700 shadow-gray-300 focus:ring-gray-500 disabled:opacity-50";
const logoutButtonClasses = baseButtonClasses + " bg-gradient-to-r from-red-500 to-red-700 text-white hover:from-red-600 hover:to-red-800 shadow-red-300 focus:ring-red-500";
const uploadExcelWrapperClasses = "ml-2"; // Mantendo, se necessário

// --- INTERFACE ---
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
      alert("Sessão expirada. Por favor, faça login novamente.");
      setIsDownloading(false);
      onLogoutClick();
      return;
    }
    try {
      // O fetch direto é necessário aqui para lidar com o blob (arquivo)
      const response = await fetch("http://localhost:8000/produtos/download/excel", {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.status === 401) {
        throw new Error("Sua sessão expirou. Você será redirecionado para a tela de login.");
      }

      if (!response.ok) {
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
    } catch (err) {
      if (err instanceof Error) {
        alert(`Erro no download: ${err.message}`);
        if (err.message.includes("expirou")) {
            onLogoutClick();
        }
      } else {
        alert('Ocorreu um erro desconhecido no download.');
      }
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between mb-8 gap-4">
      {/* Grupo Esquerdo: Logo e Título */}
      <div className="flex items-center gap-4">
        <Image src="/HIGIPLAS-LOGO-2048x761.png" alt="Logo Higiplas" width={150} height={50} priority className="drop-shadow-lg" />
        <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100 hidden md:block">
          Produtos
        </h1>
      </div>

      {/* Grupo Direito: Ações */}
      <div className="flex items-center gap-2 flex-wrap justify-center">
        <ThemeToggleButton />
        <button onClick={handleDownloadExcel} disabled={isDownloading} className={downloadButtonClasses}>
          {isDownloading ? "Gerando..." : "Exportar"}
        </button>
        <div className={uploadExcelWrapperClasses}>
            <UploadExcel onUploadSuccess={onUploadSuccess} />
        </div>
        <button onClick={onNewProductClick} className={newProductButtonClasses}>
          + Adicionar Produto
        </button>
        <button onClick={onLogoutClick} className={logoutButtonClasses}>Sair</button>
      </div>
    </div>
  );
}