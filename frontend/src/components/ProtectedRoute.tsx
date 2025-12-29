import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { isAuthenticated, getCurrentUser } from '../api/client'

interface ProtectedRouteProps {
  children: ReactNode
  requireAdmin?: boolean
}

export default function ProtectedRoute({ children, requireAdmin = false }: ProtectedRouteProps) {
  const location = useLocation()
  
  if (!isAuthenticated()) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (requireAdmin) {
    const user = getCurrentUser()
    if (!user || user.role !== 'admin') {
      return <Navigate to="/" replace />
    }
  }

  return <>{children}</>
}
