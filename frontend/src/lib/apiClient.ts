import axios, { type AxiosError, type AxiosRequestConfig, type AxiosResponse } from 'axios'

const ACCESS_TOKEN_KEY = 'access_token'
const TENANT_ID_KEY = 'osd-tenant-id'
const WORKSPACE_ID_KEY = 'osd-workspace-id'
const DEFAULT_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT) || 30000

const stripTrailingSlash = (value: string) => value.replace(/\/+$/, '')
const isAbsoluteUrl = (value: string) => /^https?:\/\//.test(value)

export const normalizeApiBase = (value: string): string => {
  const trimmed = stripTrailingSlash(String(value || '').trim())
  if (!trimmed || trimmed === '/') return '/api'

  try {
    const parsed = new URL(trimmed)
    if (!parsed.pathname || parsed.pathname === '/') {
      parsed.pathname = '/api'
    }
    return stripTrailingSlash(parsed.toString())
  } catch {
    // Non-absolute base (handled below).
  }

  if (!trimmed.startsWith('/')) {
    return `/${trimmed}`
  }

  return trimmed
}

const resolveApiBase = (): string => {
  const envBase = import.meta.env.VITE_API_BASE || import.meta.env.VITE_API_BASE_URL
  if (envBase) {
    const normalized = normalizeApiBase(String(envBase))
    if (import.meta.env.DEV && isAbsoluteUrl(String(envBase))) {
      return '/api'
    }
    return normalized
  }

  if (typeof document !== 'undefined') {
    const base = document.querySelector('base')?.getAttribute('href')
    if (base && base.includes('/api')) return normalizeApiBase(base)
  }

  return '/api'
}

export const apiPath = (path: string): string => {
  if (!path) return resolveApiBase()
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  if (path.startsWith('/')) return path
  const base = resolveApiBase()
  return `${stripTrailingSlash(base)}/${path}`
}

export const getAccessToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return window.localStorage.getItem(ACCESS_TOKEN_KEY)
}

export const setAccessToken = (token: string | null): void => {
  if (typeof window === 'undefined') return
  if (token) {
    window.localStorage.setItem(ACCESS_TOKEN_KEY, token)
  } else {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY)
  }
}

const hasHeader = (headers: Record<string, string>, name: string) =>
  Object.keys(headers).some((key) => key.toLowerCase() === name.toLowerCase())

const isFormData = (value: unknown): value is FormData =>
  typeof FormData !== 'undefined' && value instanceof FormData

const createRequestId = (): string => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `req_${Date.now()}_${Math.random().toString(16).slice(2)}`
}

const getTenantId = (): string => {
  if (typeof window === 'undefined') return 'default-tenant'
  return window.localStorage.getItem(TENANT_ID_KEY) || 'default-tenant'
}

const getWorkspaceId = (): string => {
  if (typeof window === 'undefined') return 'default-workspace'
  return window.localStorage.getItem(WORKSPACE_ID_KEY) || 'default-workspace'
}

export type ApiClientConfig = Pick<
  AxiosRequestConfig,
  'headers' | 'params' | 'signal' | 'timeout' | 'responseType' | 'withCredentials'
>

export interface ApiClientResponse<T> extends AxiosResponse<T> {
  requestId?: string
}

export interface ApiClientError extends Error {
  response?: AxiosResponse
  status?: number
  code?: string
  requestId?: string
}

const extractRequestId = (response?: AxiosResponse | null): string | undefined => {
  if (!response?.headers) return undefined
  const headers = response.headers as Record<string, string>
  return headers['x-correlation-id'] || headers['x-request-id']
}

const extractErrorMessage = (error: AxiosError): string => {
  if (error.code === 'ERR_NETWORK') {
    return 'Backend server is not running. Please start the backend server and try again.'
  }

  const data = error.response?.data
  if (typeof data === 'string') {
    return data
  }

  if (data && typeof data === 'object') {
    const record = data as Record<string, unknown>
    const detail =
      record.detail ||
      record.message ||
      (record.error && typeof record.error === 'object'
        ? (record.error as Record<string, unknown>).message
        : undefined) ||
      (record.error && typeof record.error === 'string' ? record.error : undefined)
    if (detail) {
      return String(detail)
    }
  }

  return error.message || 'Request failed.'
}

const normalizeError = (error: AxiosError): ApiClientError => {
  const requestId = extractRequestId(error.response)
  const normalized = new Error(extractErrorMessage(error)) as ApiClientError
  normalized.name = 'ApiClientError'
  normalized.response = error.response
  normalized.status = error.response?.status
  normalized.code = error.code
  normalized.requestId = requestId
  normalized.stack = error.stack
  return normalized
}

const request = async <T>(
  method: AxiosRequestConfig['method'],
  url: string,
  data?: unknown,
  config: ApiClientConfig = {}
): Promise<ApiClientResponse<T>> => {
  const headers = { ...(config.headers as Record<string, string> | undefined) } as Record<string, string>
  const token = getAccessToken()
  const requestId = createRequestId()

  if (token && !hasHeader(headers, 'authorization')) {
    headers.Authorization = `Bearer ${token}`
  }

  if (!hasHeader(headers, 'x-request-id')) {
    headers['X-Request-Id'] = requestId
  }
  if (!hasHeader(headers, 'x-tenant-id')) {
    headers['X-Tenant-Id'] = getTenantId()
  }
  if (!hasHeader(headers, 'x-workspace-id')) {
    headers['X-Workspace-Id'] = getWorkspaceId()
  }
  if (['post', 'put', 'patch', 'delete'].includes(String(method).toLowerCase())) {
    if (!hasHeader(headers, 'x-idempotency-key')) {
      headers['X-Idempotency-Key'] = requestId
    }
  }

  if (data != null && !isFormData(data) && !hasHeader(headers, 'content-type')) {
    headers['Content-Type'] = 'application/json'
  }

  try {
    const response = await axios.request<T>({
      method,
      url,
      data,
      headers,
      params: config.params,
      signal: config.signal,
      timeout: config.timeout ?? DEFAULT_TIMEOUT_MS,
      responseType: config.responseType,
      withCredentials: config.withCredentials,
    })
    const requestId = extractRequestId(response)
    return Object.assign(response, { requestId })
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw normalizeError(error)
    }
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Request failed.')
  }
}

const apiClient = {
  get: <T>(url: string, config?: ApiClientConfig) => request<T>('get', url, undefined, config),
  post: <T>(url: string, data?: unknown, config?: ApiClientConfig) =>
    request<T>('post', url, data, config),
  put: <T>(url: string, data?: unknown, config?: ApiClientConfig) =>
    request<T>('put', url, data, config),
  patch: <T>(url: string, data?: unknown, config?: ApiClientConfig) =>
    request<T>('patch', url, data, config),
  delete: <T>(url: string, config?: ApiClientConfig) => request<T>('delete', url, undefined, config),
}

export default apiClient
