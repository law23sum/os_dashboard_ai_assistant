import { Navigate } from 'react-router-dom'
import { useAuth } from './AuthContext'

export function RequireAdmin({ children }: { children: React.ReactNode }) {
  const { state } = useAuth()
  if (state.status !== 'authenticated') {
    return <Navigate to="/login" replace />
  }
  if (!state.user.is_admin) {
    return <Navigate to="/" replace />
  }
  return <>{children}</>
}

