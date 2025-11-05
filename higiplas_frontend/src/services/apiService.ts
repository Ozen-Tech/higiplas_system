// /src/services/apiService.ts - VERSÃO FINAL COM DOWNLOAD DE ARQUIVO

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

// Função helper para acessar localStorage de forma segura (apenas no cliente)
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem("authToken");
}

async function request(endpoint: string, options: RequestInit = {}) {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  // Só adiciona Content-Type: json se houver um corpo e não for FormData
  if (options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const errorDetail = errorBody?.detail ? JSON.stringify(errorBody.detail) : response.statusText;
    throw new Error(`[${response.status}] ${errorDetail}`);
  }
  
  if (response.status === 204) {
    return null;
  }

  // Retorna a resposta completa para o JSON, para consistência
  const data = await response.json();
  return { data, headers: response.headers };
}


// ========== NOVA FUNÇÃO ESPECÍFICA PARA DOWNLOADS ==========
async function requestBlob(endpoint: string) {
  const token = getAuthToken();
  const headers = new Headers();

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const errorDetail = errorBody?.detail ? JSON.stringify(errorBody.detail) : response.statusText;
    throw new Error(`[${response.status}] ${errorDetail}`);
  }

  // Retorna o objeto de resposta completo, que contém o blob e os cabeçalhos
  return response;
}


export const apiService = {
  get: (endpoint: string) => request(endpoint),
  post: (endpoint: string, body: unknown) => request(endpoint, { method: 'POST', body: JSON.stringify(body) }),
  put: (endpoint: string, body: unknown) => request(endpoint, { method: 'PUT', body: JSON.stringify(body) }),
  delete: (endpoint: string) => request(endpoint, { method: 'DELETE' }),
  postFormData: (endpoint: string, formData: FormData) => request(endpoint, { method: 'POST', body: formData }),

  // ========== ADICIONAMOS O NOVO MÉTODO AO SERVIÇO ==========
  getBlob: (endpoint: string) => requestBlob(endpoint),
};