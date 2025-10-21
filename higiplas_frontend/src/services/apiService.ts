 // /src/services/apiService.ts - VERSÃO COM REFRESH TOKEN AUTOMÁTICO

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: Error | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve();
    }
  });

  failedQueue = [];
};

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem("refreshToken");

  if (!refreshToken) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/users/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Failed to refresh token');
    }

    const data = await response.json();

    // Armazena os novos tokens
    localStorage.setItem("authToken", data.access_token);
    localStorage.setItem("refreshToken", data.refresh_token);

    return data.access_token;
  } catch (error) {
    // Se falhar ao renovar, limpa os tokens
    localStorage.removeItem("authToken");
    localStorage.removeItem("refreshToken");
    return null;
  }
}

async function request(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem("authToken");
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

  // Se receber 401, tenta renovar o token
  if (response.status === 401) {
    if (!isRefreshing) {
      isRefreshing = true;

      const newToken = await refreshAccessToken();
      isRefreshing = false;

      if (newToken) {
        processQueue();

        // Tenta novamente a requisição original com o novo token
        headers.set('Authorization', `Bearer ${newToken}`);
        const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
          ...options,
          headers,
        });

        if (!retryResponse.ok && retryResponse.status !== 204) {
          const errorBody = await retryResponse.json().catch(() => null);
          const errorDetail = errorBody?.detail ? JSON.stringify(errorBody.detail) : retryResponse.statusText;
          throw new Error(`[${retryResponse.status}] ${errorDetail}`);
        }

        if (retryResponse.status === 204) {
          return null;
        }

        const data = await retryResponse.json();
        return { data, headers: retryResponse.headers };
      } else {
        processQueue(new Error('Token refresh failed'));
        // Redireciona para login
        if (typeof window !== 'undefined') {
          window.location.href = '/';
        }
        throw new Error('[401] Sessão expirada. Por favor, faça login novamente.');
      }
    } else {
      // Se já está renovando, adiciona à fila
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then(() => {
        // Tenta novamente após a renovação
        return request(endpoint, options);
      });
    }
  }

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
  const token = localStorage.getItem("authToken");
  const headers = new Headers();

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers,
  });

  // Se receber 401, tenta renovar o token
  if (response.status === 401) {
    const newToken = await refreshAccessToken();

    if (newToken) {
      // Tenta novamente com o novo token
      headers.set('Authorization', `Bearer ${newToken}`);
      const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers,
      });

      if (!retryResponse.ok) {
        const errorBody = await retryResponse.json().catch(() => null);
        const errorDetail = errorBody?.detail ? JSON.stringify(errorBody.detail) : retryResponse.statusText;
        throw new Error(`[${retryResponse.status}] ${errorDetail}`);
      }

      return retryResponse;
    } else {
      // Redireciona para login
      if (typeof window !== 'undefined') {
        window.location.href = '/';
      }
      throw new Error('[401] Sessão expirada. Por favor, faça login novamente.');
    }
  }

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