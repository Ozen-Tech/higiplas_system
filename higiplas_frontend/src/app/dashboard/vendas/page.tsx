"use client";

import { useState, useEffect } from "react";
import {
  Search,
  ShoppingCart,
  User,
  Package,
  ArrowLeft,
  Phone,
  DollarSign,
  TrendingUp,
  Loader2,
} from "lucide-react";
import { useVendas } from "@/hooks/useVendas";
import { Cliente, ItemCarrinho } from "@/types/vendas";

type Tela =
  | "inicio"
  | "selecionar-cliente"
  | "selecionar-produtos"
  | "revisar"
  | "sucesso";

export default function VendasMobilePage() {
  const {
    dashboard,
    clientes,
    loading,
    buscarClientes,
    buscarProdutos,
    carregarDashboard,
  } = useVendas();

  const [tela, setTela] = useState<Tela>("inicio");

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [clienteSelecionado, setClienteSelecionado] = useState<Cliente | null>(
    null
  );

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [carrinho, setCarrinho] = useState<ItemCarrinho[]>([]);

  const [busca, setBusca] = useState("");

  // Carregar dashboard ao iniciar
  useEffect(() => {
    carregarDashboard();
  }, [carregarDashboard]);

  // Resetar ao voltar para o início
  useEffect(() => {
    if (tela === "inicio") {
      setClienteSelecionado(null);
      setCarrinho([]);
      setBusca("");
    }
  }, [tela]);

  // Buscar clientes ao entrar na tela de seleção
  useEffect(() => {
    if (tela === "selecionar-cliente") {
      buscarClientes();
    }
  }, [tela, buscarClientes]);

  // Buscar produtos quando entrar na tela de seleção de produtos
  useEffect(() => {
    if (tela === "selecionar-produtos") {
      buscarProdutos();
    }
  }, [tela, buscarProdutos]);

  // ------------------------
  // TELA: INÍCIO
  // ------------------------
  if (tela === "inicio") {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-500 to-blue-600 text-white p-4">
        <div className="max-w-md mx-auto">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold mb-1">Olá, Vendedor!</h1>
            <p className="text-blue-100 text-sm">Pronto para vender hoje?</p>
          </div>

          {/* Cards de Estatísticas */}
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="w-8 h-8 animate-spin" />
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3 mb-6">
              <div className="bg-white/20 backdrop-blur rounded-2xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="w-5 h-5" />
                  <span className="text-sm font-medium">Vendas Hoje</span>
                </div>
                <p className="text-2xl font-bold">
                  R$ {dashboard?.total_vendido_hoje.toFixed(2) || "0.00"}
                </p>
              </div>
              <div className="bg-white/20 backdrop-blur rounded-2xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-5 h-5" />
                  <span className="text-sm font-medium">Pedidos</span>
                </div>
                <p className="text-2xl font-bold">
                  {dashboard?.quantidade_pedidos_hoje || 0}
                </p>
              </div>
            </div>
          )}

          {/* Meta do Dia */}
          {dashboard && dashboard.meta_dia > 0 && (
            <div className="bg-white/10 backdrop-blur rounded-2xl p-4 mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Meta do Dia</span>
                <span className="text-sm font-bold">
                  {dashboard.progresso_meta.toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-white/20 rounded-full h-3">
                <div
                  className="bg-white rounded-full h-3 transition-all duration-500"
                  style={{
                    width: `${Math.min(dashboard.progresso_meta, 100)}%`,
                  }}
                />
              </div>
              <p className="text-xs text-blue-100 mt-1">
                R$ {dashboard.total_vendido_hoje.toFixed(2)} de R${" "}
                {dashboard.meta_dia.toFixed(2)}
              </p>
            </div>
          )}

          {/* Botão Principal - Nova Venda */}
          <button
            onClick={() => setTela("selecionar-cliente")}
            className="w-full bg-white text-blue-600 rounded-2xl p-6 shadow-lg mb-4 hover:bg-blue-50 transition-all active:scale-95"
          >
            <div className="flex items-center justify-center gap-3">
              <ShoppingCart className="w-8 h-8" />
              <span className="text-xl font-bold">NOVA VENDA</span>
            </div>
          </button>

          {/* Ações Secundárias */}
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => alert("Em breve: Lista de todos os clientes")}
              className="bg-white/20 backdrop-blur rounded-xl p-4 hover:bg-white/30 transition-all"
            >
              <User className="w-6 h-6 mx-auto mb-2" />
              <span className="text-sm font-medium">Meus Clientes</span>
            </button>
            <button
              onClick={() => alert("Em breve: Catálogo de produtos")}
              className="bg-white/20 backdrop-blur rounded-xl p-4 hover:bg-white/30 transition-all"
            >
              <Package className="w-6 h-6 mx-auto mb-2" />
              <span className="text-sm font-medium">Produtos</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ------------------------
  // TELA: SELECIONAR CLIENTE
  // ------------------------
  if (tela === "selecionar-cliente") {
    const clientesFiltrados = clientes.filter(
      (c) =>
        c.nome.toLowerCase().includes(busca.toLowerCase()) ||
        c.telefone.includes(busca)
    );

    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-blue-600 text-white p-4 sticky top-0 z-10 shadow-lg">
          <div className="flex items-center gap-3 mb-3">
            <button
              onClick={() => setTela("inicio")}
              className="p-2 hover:bg-white/20 rounded-lg"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <h2 className="text-xl font-bold">Selecionar Cliente</h2>
          </div>

          {/* Busca */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Nome ou telefone..."
              value={busca}
              onChange={(e) => {
                setBusca(e.target.value);
                if (e.target.value) buscarClientes(e.target.value);
              }}
              className="w-full pl-10 pr-4 py-3 rounded-xl text-gray-900 text-lg"
              autoFocus
            />
          </div>
        </div>

        <div className="p-4 space-y-3">
          {/* Botão Novo Cliente */}
          <button
            onClick={() => {
              const nome = prompt("Nome do cliente:");
              const telefone = prompt("Telefone (WhatsApp):");
              if (nome && telefone) {
                const novoCliente: Cliente = {
                  id: -1, // será criado no backend
                  nome,
                  telefone,
                  bairro: null,
                  cidade: null,
                  ultima_compra: null,
                };
                setClienteSelecionado(novoCliente);
                setTela("selecionar-produtos");
              }
            }}
            className="w-full bg-blue-600 text-white rounded-xl py-3 font-medium hover:bg-blue-700 transition-all"
          >
            + Novo Cliente
          </button>

          {/* Lista de clientes */}
          {clientesFiltrados.map((cliente) => (
            <button
              key={cliente.id}
              onClick={() => {
                setClienteSelecionado(cliente);
                setTela("selecionar-produtos");
              }}
              className="w-full bg-white p-4 rounded-xl shadow hover:bg-blue-50 transition-all flex justify-between items-center"
            >
              <div>
                <p className="font-semibold text-gray-900">{cliente.nome}</p>
                <p className="text-sm text-gray-500 flex items-center gap-1">
                  <Phone className="w-4 h-4" /> {cliente.telefone}
                </p>
              </div>
              <ArrowLeft className="w-5 h-5 text-gray-400 rotate-180" />
            </button>
          ))}
        </div>
      </div>
    );
  }

  // Fallback: caso nenhuma tela corresponda
  return <div className="p-6 text-center text-gray-500">Carregando...</div>;
}
