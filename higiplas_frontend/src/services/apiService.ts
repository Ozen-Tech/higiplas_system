// /src/services/apiService.ts

const API_BASE_URL = "http://localhost:8000";

// A função request continua a mesma, está bem implementada.
async function request(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem("authToken");
  const headers = new Headers(options.headers || {});
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  // Garante que o Content-Type só seja adicionado se houver corpo
  if (options.body) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    // Adiciona o status do erro na mensagem para facilitar a depuração
    throw new Error(`[${response.status}] ${errorData.detail}` || "Ocorreu um erro na requisição.");
  }
  
  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const apiService = {
  get: (endpoint: string) => request(endpoint),
  // Correção: Substituímos 'any' por 'unknown' para segurança de tipos.
  post: (endpoint: string, body: unknown) => request(endpoint, { method: 'POST', body: JSON.stringify(body) }),
  put: (endpoint: string, body: unknown) => request(endpoint, { method: 'PUT', body: JSON.stringify(body) }),
  delete: (endpoint: string) => request(endpoint, { method: 'DELETE' }),
};