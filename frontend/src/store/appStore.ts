import { create } from 'zustand'

interface AppState {
  // Platform info
  platform: 'web' | 'desktop' | 'mobile' | 'extension'
  platformName: string
  
  // UI state
  sidebarOpen: boolean
  theme: 'light' | 'dark' | 'auto'
  
  // User preferences
  lastVisitedRoute: string | null
  
  // Actions
  setPlatform: (platform: 'web' | 'desktop' | 'mobile' | 'extension', name: string) => void
  setSidebarOpen: (open: boolean) => void
  setTheme: (theme: 'light' | 'dark' | 'auto') => void
  setLastVisitedRoute: (route: string) => void
}

export const useAppStore = create<AppState>((set) => ({
  platform: 'web',
  platformName: 'Web',
  sidebarOpen: true,
  theme: 'auto',
  lastVisitedRoute: null,
  
  setPlatform: (platform, platformName) => set({ platform, platformName }),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setTheme: (theme) => set({ theme }),
  setLastVisitedRoute: (route) => set({ lastVisitedRoute: route }),
}))
