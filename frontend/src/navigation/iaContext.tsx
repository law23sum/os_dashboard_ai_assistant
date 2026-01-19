import { createContext, useContext, useMemo, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { findRouteContext, type IAPlatform, type IACategory, type IAFeature } from '../data/iaManifest'

export interface IARouteContextValue {
  platform?: IAPlatform
  category?: IACategory
  feature?: IAFeature
  isCategoryHome: boolean
  isPlatformLanding?: boolean
}

const IARouteContext = createContext<IARouteContextValue>({
  isCategoryHome: false,
  isPlatformLanding: false,
})

interface IANavigationProviderProps {
  children: ReactNode
}

export function IANavigationProvider({ children }: IANavigationProviderProps) {
  const location = useLocation()
  
  const routeContext = useMemo(() => {
    return findRouteContext(location.pathname)
  }, [location.pathname])

  return (
    <IARouteContext.Provider value={routeContext}>
      {children}
    </IARouteContext.Provider>
  )
}

export function useIARouteContext(): IARouteContextValue {
  return useContext(IARouteContext)
}
