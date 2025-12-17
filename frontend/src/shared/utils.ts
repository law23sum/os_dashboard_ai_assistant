/**
 * Shared utilities between desktop and web platforms
 * This file ensures code is shared between Electron and browser builds
 * to remove redundancies.
 */

/**
 * Platform detection utilities
 */
export const isElectron = (): boolean => {
  if (typeof window === 'undefined') return false
  const w = window as typeof window & { process?: { type?: string; versions?: { electron?: string } } }
  return w.process?.type === 'renderer' || Boolean(w.process?.versions?.electron)
}

export const isWeb = (): boolean => {
  return !isElectron()
}

export const isDesktop = (): boolean => {
  return isElectron()
}

/**
 * Get platform name for display
 */
export const getPlatformName = (): 'desktop' | 'web' => {
  return isElectron() ? 'desktop' : 'web'
}

/**
 * Format date consistently across platforms
 */
export const formatDate = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/**
 * Format datetime consistently across platforms
 */
export const formatDateTime = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Debounce function for shared use
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * Throttle function for shared use
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

/**
 * Safe JSON parse with fallback
 */
export const safeJsonParse = <T>(json: string, fallback: T): T => {
  try {
    return JSON.parse(json) as T
  } catch {
    return fallback
  }
}

/**
 * Generate a unique ID
 */
export const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Copy text to clipboard (works in both desktop and web)
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text)
      return true
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.opacity = '0'
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      return true
    }
  } catch (err) {
    console.error('Failed to copy to clipboard:', err)
    return false
  }
}
