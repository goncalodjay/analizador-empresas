import type { NewsFeedResponse, PriceSeriesResponse, Strategy, StrategyCreate, StrategyUpdate } from '@/lib/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new ApiError(res.status, error.detail || 'Request failed');
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json();
}

// --- Strategy API client (Deliverable 6) ---

export function getStrategies(): Promise<Strategy[]> {
  return apiFetch<Strategy[]>('/strategies');
}

export function getStrategy(id: string): Promise<Strategy> {
  return apiFetch<Strategy>(`/strategies/${id}`);
}

export function createStrategy(data: StrategyCreate): Promise<Strategy> {
  return apiFetch<Strategy>('/strategies', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function updateStrategy(id: string, data: StrategyUpdate): Promise<Strategy> {
  return apiFetch<Strategy>(`/strategies/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export function deleteStrategy(id: string): Promise<void> {
  return apiFetch<void>(`/strategies/${id}`, { method: 'DELETE' });
}

export function activateStrategy(id: string, isActive: boolean): Promise<Strategy> {
  return apiFetch<Strategy>(`/strategies/${id}/activate`, {
    method: 'PATCH',
    body: JSON.stringify({ is_active: isActive }),
  });
}

export function setPrimaryStrategy(id: string): Promise<Strategy> {
  return apiFetch<Strategy>(`/strategies/${id}/primary`, { method: 'PATCH' });
}

// --- Price History API client (Deliverable 8) ---

export function getPriceHistory(
  ticker: string,
  from?: string,
  to?: string,
): Promise<PriceSeriesResponse> {
  const params = new URLSearchParams();
  if (from) params.set('from', from);
  if (to) params.set('to', to);
  const qs = params.toString();
  return apiFetch<PriceSeriesResponse>(
    `/prices/${ticker.toUpperCase()}${qs ? `?${qs}` : ''}`,
  );
}

// --- News Feed API client (Deliverable 7) ---

export function getNews(ticker: string): Promise<NewsFeedResponse> {
  return apiFetch<NewsFeedResponse>(`/news/${ticker.toUpperCase()}`);
}
