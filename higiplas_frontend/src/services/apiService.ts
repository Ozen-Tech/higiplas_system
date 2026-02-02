// /src/services/apiService.ts - VERSÃO FINAL COM DOWNLOAD DE ARQUIVO

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

// Validação da URL da API
if (!API_BASE_URL) {
  console.error('NEXT_PUBLIC_API_URL não está configurada! Verifique as variáveis de ambiente.');
  // #region agent log
  try { fetch('http://127.0.0.1:7242/ingest/dd87b882-9f5c-4d4f-ba43-1e6325b293f7', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location: 'apiService.ts', message: 'API_BASE_URL missing', data: { hasEnv: typeof process !== 'undefined' }, timestamp: Date.now(), sessionId: 'debug-session', hypothesisId: 'H3' }) }).catch(() => {}); } catch {}
  // #endregion
}

async function request(endpoint: string, options: RequestInit = {}) {
  if (!API_BASE_URL) {
    // #region agent log
    try { fetch('http://127.0.0.1:7242/ingest/dd87b882-9f5c-4d4f-ba43-1e6325b293f7', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location: 'apiService.request', message: 'request called without API_BASE_URL', data: { endpoint: endpoint?.slice?.(0, 50) }, timestamp: Date.now(), sessionId: 'debug-session', hypothesisId: 'H3' }) }).catch(() => {}); } catch {}
    // #endregion
    throw new Error('URL da API não configurada. Verifique a variável de ambiente NEXT_PUBLIC_API_URL.');
  }

  const token = localStorage.getItem("authToken");
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  // Só adiciona Content-Type: json se houver um corpo e não for FormData
  if (options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  try {
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
  } catch (error) {
    // Tratamento específico para erros de rede/CORS
    if (error instanceof TypeError && error.message.includes('fetch')) {
      // Erro de rede (CORS, conexão, etc.)
      const errorMessage = error.message.includes('CORS') 
        ? 'Erro de CORS: O servidor não está permitindo requisições desta origem. Verifique a configuração do backend.'
        : `Erro de conexão: Não foi possível conectar ao servidor. Verifique se a API está online em ${API_BASE_URL}`;
      throw new Error(errorMessage);
    }
    // Re-lança outros erros
    throw error;
  }
}


// ========== NOVA FUNÇÃO ESPECÍFICA PARA DOWNLOADS ==========
async function requestBlob(endpoint: string) {
  if (!API_BASE_URL) {
    throw new Error('URL da API não configurada. Verifique a variável de ambiente NEXT_PUBLIC_API_URL.');
  }

  const token = localStorage.getItem("authToken");
  const headers = new Headers();

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  try {
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
  } catch (error) {
    // Tratamento específico para erros de rede/CORS
    if (error instanceof TypeError && error.message.includes('fetch')) {
      const errorMessage = error.message.includes('CORS') 
        ? 'Erro de CORS: O servidor não está permitindo requisições desta origem.'
        : `Erro de conexão: Não foi possível conectar ao servidor em ${API_BASE_URL}`;
      throw new Error(errorMessage);
    }
    throw error;
  }
}


export const apiService = {
  get: (endpoint: string) => request(endpoint),
  post: (endpoint: string, body: unknown) => request(endpoint, { method: 'POST', body: JSON.stringify(body) }),
  put: (endpoint: string, body: unknown) => request(endpoint, { method: 'PUT', body: JSON.stringify(body) }),
  patch: (endpoint: string, body: unknown) => request(endpoint, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: (endpoint: string) => request(endpoint, { method: 'DELETE' }),
  postFormData: (endpoint: string, formData: FormData) => request(endpoint, { method: 'POST', body: formData }),

  // ========== ADICIONAMOS O NOVO MÉTODO AO SERVIÇO ==========
  getBlob: (endpoint: string) => requestBlob(endpoint),
};