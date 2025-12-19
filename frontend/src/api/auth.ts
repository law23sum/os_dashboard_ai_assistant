import apiClient, { apiPath, setAccessToken } from '../lib/apiClient'

export interface AuthUser {
  id: string
  email: string
  display_name: string
  is_admin: boolean
  environment: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

export const login = async (email: string, password: string): Promise<TokenResponse> => {
  const { data } = await apiClient.post<TokenResponse>(apiPath('auth/login'), { email, password })
  setAccessToken(data.access_token)
  return data
}

export const signup = async (
  email: string,
  password: string,
  display_name: string,
  environment: 'demo' | 'prod' = 'demo'
): Promise<TokenResponse> => {
  const { data } = await apiClient.post<TokenResponse>(apiPath('auth/signup'), {
    email,
    password,
    display_name,
    environment,
  })
  setAccessToken(data.access_token)
  return data
}

export const me = async (): Promise<AuthUser> => {
  const { data } = await apiClient.get<AuthUser>(apiPath('auth/me'))
  return data
}

export const logout = async () => {
  setAccessToken(null)
}

