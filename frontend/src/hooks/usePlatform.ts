import { useEffect, useState } from 'react';
import { getPlatformInfo, PlatformInfo } from '../utils/platform';

/**
 * React hook to get platform information
 */
export function usePlatform(): PlatformInfo & { loading: boolean } {
  const [platformInfo, setPlatformInfo] = useState<PlatformInfo>({
    isElectron: false,
    isWeb: true,
    isMobile: false,
    isBrowserExtension: false,
    isMac: false,
    isWindows: false,
    isLinux: false,
    platform: 'web',
    platformName: 'Web',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const info = getPlatformInfo();
    
    // If Electron, get actual platform async
    if (info.isElectron && typeof window !== 'undefined' && window.electron) {
      window.electron.getPlatform().then((platform) => {
        setPlatformInfo({
          ...info,
          isMac: platform === 'darwin',
          isWindows: platform === 'win32',
          isLinux: platform === 'linux',
          platformName: platform === 'darwin' ? 'macOS' : platform === 'win32' ? 'Windows' : 'Linux',
        });
        setLoading(false);
      });
    } else {
      setPlatformInfo(info);
      setLoading(false);
    }
  }, []);

  return { ...platformInfo, loading };
}

