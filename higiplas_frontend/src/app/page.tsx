"use client";

import { useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(""); // Limpa erros anteriores

    // --- A MUDANÇA PRINCIPAL ESTÁ AQUI ---

    // 1. Criamos um corpo de dados no formato 'form-urlencoded'
    // Isso transforma { username: 'a', password: 'b' } em "username=a&password=b"
    const body = new URLSearchParams();
    body.append('username', email);
    body.append('password', password);

    try {
      // 2. Enviamos a requisição com o corpo e o cabeçalho corretos
      const response = await axios.post(
        'http://localhost:8000/users/token', // O endpoint de login do backend
        body, // Passamos o corpo formatado
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );

      // Se a requisição for bem-sucedida
      console.log("Login bem-sucedido!", response.data);
      const { access_token } = response.data;

      // Armazenar o token (ex: no localStorage) para usar em futuras requisições
      localStorage.setItem("authToken", access_token);

      // Redirecionar para a página principal ou dashboard
      router.push("/dashboard"); // Mude "/dashboard" para a sua rota protegida

    } catch (err: any) {
      // 3. Capturamos e exibimos o erro de forma clara
      console.error("Falha no login:", err); // ESSENCIAL PARA DEBUG

      if (err.response) {
        // O servidor respondeu com um status de erro (4xx, 5xx)
        setError("Credenciais inválidas. Por favor, tente novamente.");
      } else {
        // Erro de rede ou outro problema
        setError("Não foi possível conectar ao servidor. Verifique sua conexão.");
      }
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center text-gray-900">
          Login Higiplas
        </h2>
        <form className="space-y-6" onSubmit={handleLogin}>
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700"
            >
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="block w-full px-3 py-2 mt-1 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md shadow-sm appearance-none focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700"
            >
              Senha
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="block w-full px-3 py-2 mt-1 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md shadow-sm appearance-none focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          {error && <p className="text-sm text-center text-red-600">{error}</p>}
          <div>
            <button
              type="submit"
              className="w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Entrar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}