const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "/api";

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    const message = await response.text();
    throw new Error(`API error ${response.status}: ${message || path}`);
  }
  if (response.status === 204) {
    // @ts-expect-error allow undefined payloads when the caller expects void
    return undefined;
  }
  return (await response.json()) as T;
}

export { API_BASE_URL };
