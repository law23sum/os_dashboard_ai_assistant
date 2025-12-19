import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { getAccessToken, setAccessToken } from '../lib/apiClient'
import { me as fetchMe, type AuthUser } from '../api/auth'

type AuthState =
  | { status: 'loading'; user: null }
  | { status: 'anonymous'; user: null }
  | { status: 'authenticated'; user: AuthUser }

interface AuthContextValue {
  state: AuthState
  refresh: () => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({ status: 'loading', user: null })

  const refresh = async () => {
    const token = getAccessToken()
    if (!token) {
      setState({ status: 'anonymous', user: null })
      return
    }
    try {
      const user = await fetchMe()
      setState({ status: 'authenticated', user })
    } catch {
      setAccessToken(null)
      setState({ status: 'anonymous', user: null })
    }
  }

  const logout = () => {
    setAccessToken(null)
    setState({ status: 'anonymous', user: null })
  }

  useEffect(() => {
    refresh()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const value = useMemo<AuthContextValue>(() => ({ state, refresh, logout }), [state])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

