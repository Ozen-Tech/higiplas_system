"use client";

import { useState, useEffect, useCallback } from "react";
import { Header } from "@/components/dashboard/Header";
import ClientLayout from "@/components/ClientLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiService } from "@/services/apiService";
import { ClipboardDocumentCheckIcon, ArrowPathIcon } from "lucide-react";
import toast from "react-hot-toast";

interface Product {
  id: number;
  nome: string;
  codigo?: string;
  quantidade_em_estoque: number;
}

interface ItemContagem {
  produto_id: number;
  quantidade_fisica: number;
}

export default function ContagemEstoquePage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [fisica, setFisica] = useState<Record<number, string>>({});

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiService.get("/produtos/");
      const list = Array.isArray(res?.data) ? res.data : res?.data?.data ?? [];
      setProducts(list);
      setFisica({});
    } catch (e) {
      console.error(e);
      toast.error("Erro ao carregar produtos");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const setFisicaFor = (produtoId: number, value: string) => {
    setFisica((prev) => ({ ...prev, [produtoId]: value }));
  };

  const itensParaAjuste: ItemContagem[] = [];
  for (const p of products) {
    const v = fisica[p.id];
    if (v === undefined || v === "") continue;
    const q = parseFloat(v.replace(",", "."));
    if (isNaN(q) || q < 0) continue;
    const atual = p.quantidade_em_estoque ?? 0;
    if (Math.abs(q - atual) >= 1e-6) {
      itensParaAjuste.push({ produto_id: p.id, quantidade_fisica: q });
    }
  }

  const handleAplicarAjustes = async () => {
    if (itensParaAjuste.length === 0) {
      toast.error("Informe a quantidade física em pelo menos um produto com diferença em relação ao estoque atual.");
      return;
    }
    setSubmitting(true);
    try {
      const res = await apiService.post("/movimentacoes/ajuste-inventario", { itens: itensParaAjuste });
      const data = res?.data ?? res;
      const criadas = data?.movimentacoes_criadas ?? 0;
      const erros = data?.erros ?? [];
      if (criadas > 0) {
        toast.success(`${criadas} ajuste(s) aplicado(s).`);
        fetchProducts();
      }
      if (erros.length > 0) {
        toast.error(`${erros.length} item(ns) com erro. Veja o console.`);
        console.warn("Erros no ajuste:", erros);
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Erro ao aplicar ajustes";
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const diff = (p: Product) => {
    const v = fisica[p.id];
    if (v === undefined || v === "") return null;
    const q = parseFloat(v.replace(",", "."));
    if (isNaN(q)) return null;
    const atual = p.quantidade_em_estoque ?? 0;
    return q - atual;
  };

  return (
    <ClientLayout>
      <Header />
      <main className="p-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ClipboardDocumentCheckIcon className="h-6 w-6" />
                <CardTitle>Contagem de Estoque (Inventário)</CardTitle>
              </div>
              <Button variant="outline" size="sm" onClick={fetchProducts} disabled={loading}>
                <ArrowPathIcon className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                Atualizar lista
              </Button>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Informe a quantidade física contada por produto. Ao clicar em &quot;Aplicar ajustes&quot;, o sistema criará movimentações de correção para alinhar o estoque digital ao físico.
            </p>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-gray-500">Carregando produtos...</p>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2 px-2">Produto</th>
                        <th className="text-left py-2 px-2">Código</th>
                        <th className="text-right py-2 px-2">Estoque atual</th>
                        <th className="text-right py-2 px-2">Qtd. física</th>
                        <th className="text-right py-2 px-2">Diferença</th>
                      </tr>
                    </thead>
                    <tbody>
                      {products.map((p) => {
                        const d = diff(p);
                        return (
                          <tr key={p.id} className="border-b border-gray-100 dark:border-gray-800">
                            <td className="py-2 px-2">{p.nome}</td>
                            <td className="py-2 px-2">{p.codigo ?? "-"}</td>
                            <td className="text-right py-2 px-2">{p.quantidade_em_estoque ?? 0}</td>
                            <td className="py-2 px-2">
                              <Input
                                type="text"
                                inputMode="decimal"
                                placeholder="Física"
                                className="w-24 text-right"
                                value={fisica[p.id] ?? ""}
                                onChange={(e) => setFisicaFor(p.id, e.target.value)}
                              />
                            </td>
                            <td className="text-right py-2 px-2">
                              {d !== null && (
                                <span className={d > 0 ? "text-green-600" : d < 0 ? "text-red-600" : "text-gray-500"}>
                                  {d > 0 ? "+" : ""}{d}
                                </span>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                <div className="mt-4 flex justify-end">
                  <Button
                    onClick={handleAplicarAjustes}
                    disabled={submitting || itensParaAjuste.length === 0}
                  >
                    {submitting ? "Aplicando..." : `Aplicar ajustes (${itensParaAjuste.length})`}
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </main>
    </ClientLayout>
  );
}
