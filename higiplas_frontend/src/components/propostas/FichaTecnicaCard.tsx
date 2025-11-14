// src/components/propostas/FichaTecnicaCard.tsx

'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FichaTecnica } from '@/services/propostaService';
import { FileText, Droplet, TrendingUp } from 'lucide-react';

interface FichaTecnicaCardProps {
  ficha: FichaTecnica | null;
}

export function FichaTecnicaCard({ ficha }: FichaTecnicaCardProps) {
  if (!ficha) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-gray-500 dark:text-gray-400 text-center">
            Ficha técnica não disponível para este produto
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Ficha Técnica
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h3 className="font-semibold text-lg mb-2">{ficha.nome_produto}</h3>
        </div>

        {ficha.dilucao_recomendada && (
          <div className="flex items-start gap-3">
            <Droplet className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Diluição Recomendada</p>
              <p className="font-semibold text-lg">{ficha.dilucao_recomendada}</p>
              {ficha.dilucao_numerador && ficha.dilucao_denominador && (
                <p className="text-xs text-gray-500 dark:text-gray-500">
                  {ficha.dilucao_numerador} parte(s) para {ficha.dilucao_denominador} parte(s)
                </p>
              )}
            </div>
          </div>
        )}

        {ficha.rendimento_litro && (
          <div className="flex items-start gap-3">
            <TrendingUp className="h-5 w-5 text-green-600 mt-0.5" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Rendimento</p>
              <p className="font-semibold text-lg">
                {ficha.rendimento_litro.toFixed(2)} litros por litro do produto
              </p>
            </div>
          </div>
        )}

        {ficha.modo_uso && (
          <div>
            <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Modo de Uso</p>
            <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
              {ficha.modo_uso}
            </p>
          </div>
        )}

        {ficha.observacoes && (
          <div>
            <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Observações</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">{ficha.observacoes}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

