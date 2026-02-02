'use client';

import { useState, useEffect, useCallback } from 'react';
import { Header } from '@/components/dashboard/Header';
import ClientLayout from '@/components/ClientLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { adminService, RegrasSugestaoCompra } from '@/services/adminService';
import { useAdmin } from '@/hooks/useAdmin';
import { Cog6ToothIcon, Loader2, Check } from 'lucide-react';
import toast from 'react-hot-toast';

const DEFAULTS: RegrasSugestaoCompra = {
  lead_time_dias: 7,
  cobertura_dias: 14,
  dias_analise: 90,
  min_vendas_historico: 2,
  margem_seguranca: 1.2,
  margem_adicional_cobertura: 1.15,
  dias_antecedencia_cliente: 7,
};

export default function RegrasSugestaoCompraPage() {
  const { usuario, loading: userLoading, error: userError, isAdmin } = useAdmin();
  const [regras, setRegras] = useState<RegrasSugestaoCompra>(DEFAULTS);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const carregarRegras = useCallback(async () => {
    setLoading(true);
    try {
      const data = await adminService.getRegrasSugestaoCompra();
      setRegras({
        lead_time_dias: data.lead_time_dias ?? DEFAULTS.lead_time_dias,
        cobertura_dias: data.cobertura_dias ?? DEFAULTS.cobertura_dias,
        dias_analise: data.dias_analise ?? DEFAULTS.dias_analise,
        min_vendas_historico: data.min_vendas_historico ?? DEFAULTS.min_vendas_historico,
        margem_seguranca: data.margem_seguranca ?? DEFAULTS.margem_seguranca,
        margem_adicional_cobertura: data.margem_adicional_cobertura ?? DEFAULTS.margem_adicional_cobertura,
        dias_antecedencia_cliente: data.dias_antecedencia_cliente ?? DEFAULTS.dias_antecedencia_cliente,
      });
    } catch (e) {
      console.error(e);
      toast.error('Erro ao carregar regras');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAdmin) {
      carregarRegras();
    }
  }, [isAdmin, carregarRegras]);

  const handleChange = (field: keyof RegrasSugestaoCompra, value: string) => {
    const num = field.includes('margem') ? parseFloat(value) : parseInt(value, 10);
    if (isNaN(num)) return;
    setRegras((prev) => ({ ...prev, [field]: num }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await adminService.putRegrasSugestaoCompra(regras);
      toast.success('Regras salvas com sucesso');
      carregarRegras();
    } catch (e) {
      console.error(e);
      toast.error('Erro ao salvar regras');
    } finally {
      setSaving(false);
    }
  };

  if (userLoading || !usuario) {
    return (
      <ClientLayout>
        <Header />
        <div className="p-6 flex items-center justify-center min-h-[200px]">
          <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
        </div>
      </ClientLayout>
    );
  }

  if (userError || !isAdmin) {
    return (
      <ClientLayout>
        <Header />
        <div className="p-6">
          <p className="text-red-600 dark:text-red-400">
            {userError || 'Apenas administradores ou gestores podem acessar esta página.'}
          </p>
        </div>
      </ClientLayout>
    );
  }

  return (
    <ClientLayout>
      <Header>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <Cog6ToothIcon className="h-7 w-7" />
          Regras de sugestão de compra
        </h1>
      </Header>
      <div className="p-6 max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle>Parâmetros usados na geração de sugestões</CardTitle>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Estes valores são usados pelo sistema para calcular quando e quanto comprar. Ajuste conforme a realidade da sua empresa.
            </p>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-gray-500" />
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="lead_time_dias">Lead time (dias)</Label>
                    <Input
                      id="lead_time_dias"
                      type="number"
                      min={1}
                      value={regras.lead_time_dias}
                      onChange={(e) => handleChange('lead_time_dias', e.target.value)}
                    />
                    <p className="text-xs text-gray-500">Tempo de reposição do fornecedor em dias.</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cobertura_dias">Dias de cobertura desejados</Label>
                    <Input
                      id="cobertura_dias"
                      type="number"
                      min={1}
                      value={regras.cobertura_dias}
                      onChange={(e) => handleChange('cobertura_dias', e.target.value)}
                    />
                    <p className="text-xs text-gray-500">Quantos dias de estoque o sistema considera ideal.</p>
                  </div>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="dias_analise">Dias de análise</Label>
                    <Input
                      id="dias_analise"
                      type="number"
                      min={1}
                      value={regras.dias_analise}
                      onChange={(e) => handleChange('dias_analise', e.target.value)}
                    />
                    <p className="text-xs text-gray-500">Período de histórico usado para calcular demanda.</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="min_vendas_historico">Mínimo de vendas no histórico</Label>
                    <Input
                      id="min_vendas_historico"
                      type="number"
                      min={1}
                      value={regras.min_vendas_historico}
                      onChange={(e) => handleChange('min_vendas_historico', e.target.value)}
                    />
                    <p className="text-xs text-gray-500">Mínimo de movimentações para considerar produto com histórico.</p>
                  </div>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="margem_seguranca">Margem de segurança (estoque mínimo)</Label>
                    <Input
                      id="margem_seguranca"
                      type="number"
                      min={1}
                      step={0.01}
                      value={regras.margem_seguranca}
                      onChange={(e) => handleChange('margem_seguranca', e.target.value)}
                    />
                    <p className="text-xs text-gray-500">Ex.: 1.2 = 20% a mais sobre o mínimo calculado.</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="margem_adicional_cobertura">Margem adicional (cobertura)</Label>
                    <Input
                      id="margem_adicional_cobertura"
                      type="number"
                      min={1}
                      step={0.01}
                      value={regras.margem_adicional_cobertura}
                      onChange={(e) => handleChange('margem_adicional_cobertura', e.target.value)}
                    />
                    <p className="text-xs text-gray-500">Ex.: 1.15 = 15% a mais na quantidade para cobertura.</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="dias_antecedencia_cliente">Dias de antecedência (próxima compra do cliente)</Label>
                  <Input
                    id="dias_antecedencia_cliente"
                    type="number"
                    min={1}
                    value={regras.dias_antecedencia_cliente}
                    onChange={(e) => handleChange('dias_antecedencia_cliente', e.target.value)}
                  />
                  <p className="text-xs text-gray-500">Comprar quando faltar até X dias para a próxima compra esperada do cliente.</p>
                </div>
                <div className="pt-4">
                  <Button type="submit" disabled={saving}>
                    {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Check className="h-4 w-4 mr-2" />}
                    Salvar regras
                  </Button>
                </div>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </ClientLayout>
  );
}
