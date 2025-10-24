 // /src/services/apiService.ts - VERSÃO COM REFRESH TOKEN AUTOMÁTICO

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: ApiRequestResult<unknown>) => void;
  reject: (reason?: unknown) => void;
}> = [];

type ApiRequestResult<T> = { data: T; headers: Headers } | null;

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
  } catch {
    // Se falhar ao renovar, limpa os tokens
    localStorage.removeItem("authToken");
    localStorage.removeItem("refreshToken");
    return null;
  }
}

async function request<T = unknown>(endpoint: string, options: RequestInit = {}): Promise<ApiRequestResult<T>> {
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

  if (response.status === 401) {
    if (!isRefreshing) {
      isRefreshing = true;
      const newToken = await refreshAccessToken();
      isRefreshing = false;

      if (newToken) {
        processQueue();

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

        const data = (await retryResponse.json()) as T;
        return { data, headers: retryResponse.headers };
      }

      processQueue(new Error('Token refresh failed'));
      if (typeof window !== 'undefined') {
        window.location.href = '/';
      }
      throw new Error('[401] Sessão expirada. Por favor, faça login novamente.');
    }

    return new Promise<ApiRequestResult<T>>((resolve, reject) => {
      failedQueue.push({
        resolve: (value?: ApiRequestResult<unknown>) => resolve(value as ApiRequestResult<T>),
        reject,
      });
    }).then(() => request<T>(endpoint, options));
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
  const data = (await response.json()) as T;
  return { data, headers: response.headers };
}


// ========== NOVA FUNÇÃO ESPECÍFICA PARA DOWNLOADS ==========
async function requestBlob(endpoint: string): Promise<Response> {
  const token = localStorage.getItem("authToken");
  const headers = new Headers();

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers,
  });

  // Se retorno OK, já retorna a response para o chamador processar o blob
  if (response.ok) {
    return response;
  }

  // Para outros erros que não sejam 401, tenta extrair detalhes e lança
  if (response.status !== 401) {
    const errorBody = await response.json().catch(() => null);
    const errorDetail = errorBody?.detail ? JSON.stringify(errorBody.detail) : response.statusText;
    throw new Error(`Download failed: ${errorDetail}`);
  }

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

const apiService = {
  get: <T = unknown>(endpoint: string) => request<T>(endpoint),
  post: <T = unknown>(endpoint: string, body: unknown) => request<T>(endpoint, { method: 'POST', body: JSON.stringify(body) }),
  put: <T = unknown>(endpoint: string, body: unknown) => request<T>(endpoint, { method: 'PUT', body: JSON.stringify(body) }),
  delete: <T = unknown>(endpoint: string) => request<T>(endpoint, { method: 'DELETE' }),
  postFormData: <T = unknown>(endpoint: string, formData: FormData) => request<T>(endpoint, { method: 'POST', body: formData }),
  getBlob: (endpoint: string) => requestBlob(endpoint),
} as const;

export { apiService };
export default apiService;