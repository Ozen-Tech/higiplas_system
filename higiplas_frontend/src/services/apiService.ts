// /src/services/apiService.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

async function request(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem("authToken");
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  // --- CORREÇÃO IMPORTANTE AQUI ---
  // Só definimos Content-Type como JSON se o corpo NÃO for FormData.
  // O navegador definirá o Content-Type correto para FormData automaticamente.
  if (options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    // --- INÍCIO DA MELHORIA ---
    let errorDetail = response.statusText;
    try {
        const errorData = await response.json();
        // O FastAPI geralmente retorna erros em `errorData.detail`
        // Se for uma string, use-a. Se for um objeto, serialize-o para visualização.
        if (typeof errorData.detail === 'string') {
            errorDetail = errorData.detail;
        } else if (errorData.detail) {
            errorDetail = JSON.stringify(errorData.detail);
        }
    } catch (e) {
        // O corpo do erro não era JSON, continue com o statusText.
    }
    throw new Error(`[${response.status}] ${errorDetail}`);
    // --- FIM DA MELHORIA ---
  }
  
  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const apiService = {
  get: (endpoint: string) => request(endpoint),
  post: (endpoint: string, body: unknown) => request(endpoint, { method: 'POST', body: JSON.stringify(body) }),
  put: (endpoint: string, body: unknown) => request(endpoint, { method: 'PUT', body: JSON.stringify(body) }),
  delete: (endpoint: string) => request(endpoint, { method: 'DELETE' }),

  // --- NOVA FUNÇÃO PARA UPLOAD DE ARQUIVOS ---
  postFormData: (endpoint: string, formData: FormData) => request(endpoint, { method: 'POST', body: formData }),
};