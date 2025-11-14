// src/hooks/useFichasTecnicas.ts

import { useState } from 'react';
import { fichaTecnicaService, FichaTecnica } from '@/services/propostaService';

export function useFichasTecnicas() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getFichaByProduto = async (produtoId: number): Promise<FichaTecnica | null> => {
    setLoading(true);
    setError(null);
    try {
      const ficha = await fichaTecnicaService.getByProduto(produtoId);
      return ficha;
    } catch {
      return null;
    } finally {
      setLoading(false);
    }
  };

  const getAllFichas = async (skip = 0, limit = 100): Promise<FichaTecnica[]> => {
    setLoading(true);
    setError(null);
    try {
      const fichas = await fichaTecnicaService.getAll(skip, limit);
      return fichas;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao buscar fichas técnicas';
      setError(errorMessage);
      return [];
    } finally {
      setLoading(false);
    }
  };

  const processarPDFs = async (pasta: string): Promise<FichaTecnica[]> => {
    setLoading(true);
    setError(null);
    try {
      const fichas = await fichaTecnicaService.processarPasta(pasta);
      return fichas;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao processar PDFs';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const createFicha = async (ficha: Partial<FichaTecnica>): Promise<FichaTecnica> => {
    setLoading(true);
    setError(null);
    try {
      const novaFicha = await fichaTecnicaService.create(ficha);
      return novaFicha;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao criar ficha técnica';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateFicha = async (fichaId: number, ficha: Partial<FichaTecnica>): Promise<FichaTecnica> => {
    setLoading(true);
    setError(null);
    try {
      const fichaAtualizada = await fichaTecnicaService.update(fichaId, ficha);
      return fichaAtualizada;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao atualizar ficha técnica';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteFicha = async (fichaId: number): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      await fichaTecnicaService.delete(fichaId);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao deletar ficha técnica';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    getFichaByProduto,
    getAllFichas,
    processarPDFs,
    createFicha,
    updateFicha,
    deleteFicha,
  };
}

