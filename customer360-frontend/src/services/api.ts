import type {
  AccountSearchResponse,
  BriefingAcceptedResponse,
  BriefingCitationsResponse,
  BriefingResponse,
} from '../types/briefing';
import type { LoginRequest, LoginResponse } from '../types/auth';

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL ?? '/api/v1';

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {}
    const err = new Error(detail);
    (err as any).status = res.status;
    throw err;
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const authApi = {
  login: (payload: LoginRequest): Promise<LoginResponse> =>
    request('/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
};

export const accountsApi = {
  search: (q: string, token: string): Promise<AccountSearchResponse> =>
    request(`/accounts/search?q=${encodeURIComponent(q)}`, {}, token),
};

export const briefingsApi = {
  generate: (
    account_id: string,
    site_id: string | null,
    token: string
  ): Promise<BriefingAcceptedResponse> =>
    request(
      '/briefings/generate',
      { method: 'POST', body: JSON.stringify({ account_id, site_id }) },
      token
    ),

  get: (briefingId: string, token: string): Promise<BriefingResponse> =>
    request(`/briefings/${briefingId}`, {}, token),

  getCitations: (
    briefingId: string,
    token: string
  ): Promise<BriefingCitationsResponse> =>
    request(`/briefings/${briefingId}/citations`, {}, token),

  exportPdf: async (briefingId: string, token: string): Promise<Blob> => {
    const res = await fetch(`${API_BASE}/briefings/${briefingId}/export`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      let detail = `HTTP ${res.status}`;
      try { const b = await res.json(); detail = b.detail ?? detail; } catch {}
      const err = new Error(detail);
      (err as any).status = res.status;
      throw err;
    }
    return res.blob();
  },
};
