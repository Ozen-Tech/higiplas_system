// /src/app/components/dashboard/DashboardHeader.tsx

"use client";

import UploadExcel from "@/components/UploadExcel";
import { useState } from "react";

// Estilos
const baseButtonClasses = "px-4 py-2 text-sm font-semibold rounded-lg shadow-md transition duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2";
const newProductButtonClasses = baseButtonClasses + " bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500";
const downloadButtonClasses = baseButtonClasses + " bg-gray-600 dark:bg-gray-700 text-white hover:bg-gray-700 dark:hover:bg-gray-600 focus:ring-gray-500 disabled:opacity-50";

interface DashboardHeaderProps {
  onNewProductClick: () => void;
  onUploadSuccess: () => void;
}

export function DashboardHeader({ onNewProductClick, onUploadSuccess }: DashboardHeaderProps) {
  const [isDownloading, setIsDownloading] = useState(false);
  
  const handleDownloadExcel = async () => {
    setIsDownloading(true);
    const token = localStorage.getItem("authToken");
    if (!token) { alert("Sessão expirada."); setIsDownloading(false); return; }
    try {
        const response = await fetch("http://localhost:8000/produtos/download/excel", { method: 'GET', headers: { 'Authorization': `Bearer ${token}` } });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Erro ao gerar arquivo.");
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "higiplas_produtos_estoque.xlsx";
        document.body.appendChild(a); a.click(); a.remove(); window.URL.revokeObjectURL(url);
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