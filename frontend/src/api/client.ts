const API_BASE = import.meta.env.VITE_API_URL ?? "";

const TOKEN_KEY = "mcp_access_token";
const REFRESH_KEY = "mcp_refresh_token";
const EXPIRY_KEY = "mcp_token_expiry";

export function getAccessToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return sessionStorage.getItem(REFRESH_KEY);
}

export function setTokens(access: string, refresh: string, expiresInMs = 14 * 60 * 1000) {
  sessionStorage.setItem(TOKEN_KEY, access);
  sessionStorage.setItem(REFRESH_KEY, refresh);
  sessionStorage.setItem(EXPIRY_KEY, String(Date.now() + expiresInMs));
}

export function clearTokens() {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(REFRESH_KEY);
  sessionStorage.removeItem(EXPIRY_KEY);
}

function isTokenExpiringSoon(): boolean {
  const expiry = sessionStorage.getItem(EXPIRY_KEY);
  if (!expiry) return false;
  return Date.now() > Number(expiry) - 60_000;
}

let refreshPromise: Promise<boolean> | null = null;

async function refreshAccessToken(): Promise<boolean> {
  const refresh = getRefreshToken();
  if (!refresh) return false;

  const response = await fetch(`${API_BASE}/v1/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refresh }),
  });

  if (!response.ok) {
    clearTokens();
    return false;
  }

  const data = await response.json();
  setTokens(data.access_token, data.refresh_token);
  return true;
}

async function ensureValidToken(): Promise<boolean> {
  if (!getAccessToken()) return false;
  if (!isTokenExpiringSoon()) return true;

  if (!refreshPromise) {
    refreshPromise = refreshAccessToken().finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

export class ApiClientError extends Error {
  status: number;
  requestId?: string | null;

  constructor(message: string, status: number, requestId?: string | null) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.requestId = requestId;
  }
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  auth = true,
): Promise<T> {
  if (auth) {
    const valid = await ensureValidToken();
    if (!valid) {
      throw new ApiClientError("Unauthorized", 401);
    }
  }

  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (auth) {
    const token = getAccessToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (response.status === 401 && auth) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      return apiFetch<T>(path, options, auth);
    }
    throw new ApiClientError("Session expired", 401);
  }

  if (!response.ok) {
    let detail = response.statusText;
    let requestId: string | null | undefined;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
      requestId = body.request_id;
    } catch {
      // ignore parse errors
    }
    throw new ApiClientError(detail, response.status, requestId);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
