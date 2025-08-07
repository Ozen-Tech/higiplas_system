// /src/services/apiService.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

async function request(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem("authToken");
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    // Tenta extrair a mensagem de erro detalhada do corpo da resposta da API
    const errorBody = await response.json().catch(() => null); // Retorna null se o corpo não for JSON
    
    // Prioriza a mensagem de `detail` do FastAPI, senão usa o texto de status
    const errorDetail = errorBody?.detail ? JSON.stringify(errorBody.detail) : response.statusText;
    
    throw new Error(`[${response.status}] ${errorDetail}`);
  }
  
  // Retorna null para respostas "No Content"
  if (response.status === 204) {
    return null;
  }

  // Retorna o JSON para respostas de sucesso
  return response.json();
}

export const apiService = {
  get: (endpoint: string) => request(endpoint),
  post: (endpoint: string, body: unknown) => request(endpoint, { method: 'POST', body: JSON.stringify(body) }),
  put: (endpoint: string, body: unknown) => request(endpoint, { method: 'PUT', body: JSON.stringify(body) }),
  delete: (endpoint: string) => request(endpoint, { method: 'DELETE' }),
  postFormData: (endpoint: string, formData: FormData) => request(endpoint, { method: 'POST', body: formData }),
};