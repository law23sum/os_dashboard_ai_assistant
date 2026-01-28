import { useEffect } from 'react'
import { usePlatform } from '../../hooks/usePlatform'
import { useAppStore } from '../../store/appStore'
import WebHome from './WebHome'
import DesktopHome from './DesktopHome'
import MobileHome from './MobileHome'
import ExtensionHome from './ExtensionHome'

/**
 * Platform-specific home page router
 * Automatically shows the appropriate home page based on detected platform
 */
export default function PlatformHome() {
  const platform = usePlatform()
  const { setPlatform } = useAppStore()

  useEffect(() => {
    // Sync platform info to store
    if (!platform.loading) {
      setPlatform(platform.platform, platform.platformName)
    }
  }, [platform.loading, platform.platform, platform.platformName, setPlatform])

  if (platform.loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="h-12 w-12 animate-spin rounded-full border-2 border-white/30 border-t-white mx-auto mb-4" />
          <p className="text-slate-400">Detecting platform...</p>
        </div>
      </div>
    )
  }

  // Route to appropriate home page based on platform
  switch (platform.platform) {
    case 'desktop':
      return <DesktopHome />
    case 'mobile':
      return <MobileHome />
    case 'extension':
      return <ExtensionHome />
    case 'web':
    default:
      return <WebHome />
  }
}
