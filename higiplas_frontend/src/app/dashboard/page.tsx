'use client'

import { useState, useEffect } from "react";
import axios from "axios";

enum PerfilUsuario {
  ADMIN = "ADMIN",
  GESTOR = "GESTOR",
  OPERADOR = "OPERADOR",
}

interface Usuario {
  id: number;
  nome: string;
  email: string;
  empresa_id: number;
  perfil: PerfilUsuario;
}

interface Cliente {
  id: number;
  nome: string;
  telefone?: string;
  endereco?: string;
}

interface ItemEstoque {
  id: number;
  nome: string;
  quantidade: number;
  preco: number;
}

export default function VendaPage() {
  const [step, setStep] = useState<number>(1);

  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [clienteSelecionado, setClienteSelecionado] = useState<Cliente | null>(null);
  const [itens, setItens] = useState<ItemEstoque[]>([]);
  const [itensSelecionados, setItensSelecionados] = useState<ItemEstoque[]>([]);

  // Fetch do usuário logado
  useEffect(() => {
    const fetchUsuario = async () => {
      try {
        const res = await axios.get<Usuario>('/api/usuarios/me'); // endpoint que retorna dados do usuário logado
        setUsuario(res.data);
      } catch (err) {
        console.error("Erro ao buscar usuário logado", err);
      }
    };
    fetchUsuario();
  }, []);

  // Fetch de clientes
  useEffect(() => {
    const fetchClientes = async () => {
      try {
        const res = await axios.get<Cliente[]>('/api/clientes');
        setClientes(res.data);
      } catch (err) {
        console.error("Erro ao buscar clientes", err);
      }
    };
    fetchClientes();
  }, []);

  // Fetch de itens do estoque
  useEffect(() => {
    const fetchItens = async () => {
      try {
        const res = await axios.get<ItemEstoque[]>('/api/itens');
        setItens(res.data);
      } catch (err) {
        console.error("Erro ao buscar itens", err);
      }
    };
    fetchItens();
  }, []);

  const adicionarItem = (item: ItemEstoque) => {
    setItensSelecionados(prev => [...prev, item]);
  };

  const removerItem = (id: number) => {
    setItensSelecionados(prev => prev.filter(i => i.id !== id));
  };

  const confirmarVenda = async () => {
    if (!usuario) return;
    if (!clienteSelecionado) return alert("Selecione um cliente");
    if (itensSelecionados.length === 0) return alert("Selecione pelo menos um item");

    try {
      await axios.post('/api/vendas', {
        usuario_id: usuario.id,
        cliente_id: clienteSelecionado.id,
        itens: itensSelecionados.map(i => ({ id: i.id, quantidade: 1 }))
      });
      alert("Venda confirmada!");
      setStep(1);
      setClienteSelecionado(null);
      setItensSelecionados([]);
    } catch (err) {
      console.error("Erro ao confirmar venda", err);
      alert("Erro ao confirmar venda");
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Registro de Venda</h1>

      {step === 1 && (
        <div>
          <h2 className="text-xl font-semibold mb-2">Passo 1: Selecionar Cliente</h2>
          <ul className="mb-4">
            {clientes.map(c => (
              <li key={c.id}>
                <button
                  className={`p-2 rounded mb-1 border ${clienteSelecionado?.id === c.id ? "bg-blue-200" : "bg-gray-100"}`}
                  onClick={() => setClienteSelecionado(c)}
                >
                  {c.nome}
                </button>
              </li>
            ))}
          </ul>
          <button
            disabled={!clienteSelecionado}
            className="px-4 py-2 bg-blue-500 text-white rounded"
            onClick={() => setStep(2)}
          >
            Próximo
          </button>
        </div>
      )}

      {step === 2 && (
        <div>
          <h2 className="text-xl font-semibold mb-2">Passo 2: Selecionar Itens</h2>
          <ul className="mb-4">
            {itens.map(item => (
              <li key={item.id} className="mb-2">
                <span>{item.nome} - R$ {item.preco.toFixed(2)}</span>
                <button
                  className="ml-2 px-2 py-1 bg-green-300 rounded"
                  onClick={() => adicionarItem(item)}
                  disabled={itensSelecionados.some(i => i.id === item.id)}
                >
                  Adicionar
                </button>
              </li>
            ))}
          </ul>
          <button
            className="px-4 py-2 bg-gray-300 rounded mr-2"
            onClick={() => setStep(1)}
          >
            Voltar
          </button>
          <button
            className="px-4 py-2 bg-blue-500 text-white rounded"
            onClick={() => setStep(3)}
          >
            Próximo
          </button>
        </div>
      )}

      {step === 3 && (
        <div>
          <h2 className="text-xl font-semibold mb-2">Passo 3: Revisão da Venda</h2>
          <ul className="mb-4">
            {itensSelecionados.map(i => (
              <li key={i.id}>
                {i.nome} - R$ {i.preco.toFixed(2)}
                <button className="ml-2 text-red-500" onClick={() => removerItem(i.id)}>Remover</button>
              </li>
            ))}
          </ul>
          <button
            className="px-4 py-2 bg-gray-300 rounded mr-2"
            onClick={() => setStep(2)}
          >
            Voltar
          </button>
          <button
            className="px-4 py-2 bg-blue-500 text-white rounded"
            onClick={() => setStep(4)}
          >
            Próximo
          </button>
        </div>
      )}

      {step === 4 && (
        <div>
          <h2 className="text-xl font-semibold mb-2">Passo 4: Confirmar Venda</h2>
          {usuario?.perfil === PerfilUsuario.GESTOR || usuario?.perfil === PerfilUsuario.ADMIN ? (
            <button
              className="px-4 py-2 bg-green-600 text-white rounded"
              onClick={confirmarVenda}
            >
              Confirmar Venda
            </button>
          ) : (
            <div className="p-4 bg-yellow-100 rounded">
              Apenas gestores podem confirmar a venda.
            </div>
          )}
          <button
            className="px-4 py-2 bg-gray-300 rounded mt-2"
            onClick={() => setStep(3)}
          >
            Voltar
          </button>
        </div>
      )}
    </div>
  );
}
