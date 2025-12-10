/**
 * Platform detection utilities
 * Shared between web and desktop (Electron) versions
 */

export interface PlatformInfo {
  isElectron: boolean;
  isWeb: boolean;
  isMac: boolean;
  isWindows: boolean;
  isLinux: boolean;
  platform: string;
}

declare global {
  interface Window {
    electron?: {
      isElectron: boolean;
      getPlatform: () => Promise<string>;
      showOpenDialog: (options: any) => Promise<any>;
      showSaveDialog: (options: any) => Promise<any>;
      showMessageBox: (options: any) => Promise<any>;
      getAppVersion: () => Promise<string>;
      getAppPath: () => Promise<string>;
      onNavigateTo: (callback: (path: string) => void) => void;
    };
  }
}

/**
 * Get platform information
 */
export function getPlatformInfo(): PlatformInfo {
  const isElectron = typeof window !== 'undefined' && window.electron?.isElectron === true;
  const isWeb = !isElectron;
  
  let platform = 'unknown';
  let isMac = false;
  let isWindows = false;
  let isLinux = false;

  if (isElectron && window.electron) {
    // In Electron, we need to get platform async
    window.electron.getPlatform().then((p) => {
      platform = p;
      isMac = p === 'darwin';
      isWindows = p === 'win32';
      isLinux = p === 'linux';
    });
  } else {
    // In web, detect from user agent
    const userAgent = typeof navigator !== 'undefined' ? navigator.userAgent.toLowerCase() : '';
    platform = 'web';
    isMac = /mac|darwin/i.test(userAgent);
    isWindows = /win|windows/i.test(userAgent);
    isLinux = /linux/i.test(userAgent);
  }

  return {
    isElectron,
    isWeb,
    isMac,
    isWindows,
    isLinux,
    platform,
  };
}

/**
 * Show open file dialog (Electron only)
 */
export async function showOpenFileDialog(options?: {
  title?: string;
  defaultPath?: string;
  filters?: Array<{ name: string; extensions: string[] }>;
  properties?: string[];
}): Promise<string[] | null> {
  if (typeof window !== 'undefined' && window.electron) {
    const result = await window.electron.showOpenDialog({
      ...options,
      properties: ['openFile', ...(options?.properties || [])],
    });
    return result.canceled ? null : result.filePaths;
  }
  // Fallback for web: use HTML5 file input
  return new Promise((resolve) => {
    const input = document.createElement('input');
    input.type = 'file';
    if (options?.filters) {
      input.accept = options.filters
        .map((f) => f.extensions.map((ext) => `.${ext}`).join(','))
        .join(',');
    }
    input.onchange = (e) => {
      const files = (e.target as HTMLInputElement).files;
      if (files && files.length > 0) {
        resolve(Array.from(files).map((f) => f.name));
      } else {
        resolve(null);
      }
    };
    input.click();
  });
}

/**
 * Show save file dialog (Electron only)
 */
export async function showSaveFileDialog(options?: {
  title?: string;
  defaultPath?: string;
  filters?: Array<{ name: string; extensions: string[] }>;
}): Promise<string | null> {
  if (typeof window !== 'undefined' && window.electron) {
    const result = await window.electron.showSaveDialog(options || {});
    return result.canceled ? null : result.filePath;
  }
  // Web fallback: trigger download
  return null;
}

/**
 * Show message box (Electron only)
 */
export async function showMessageBox(options: {
  type?: 'none' | 'info' | 'error' | 'question' | 'warning';
  title?: string;
  message: string;
  detail?: string;
  buttons?: string[];
}): Promise<number> {
  if (typeof window !== 'undefined' && window.electron) {
    const result = await window.electron.showMessageBox(options);
    return result.response;
  }
  // Web fallback: use browser alert/confirm
  if (options.type === 'question' && options.buttons) {
    return window.confirm(options.message) ? 0 : 1;
  }
  window.alert(options.message);
  return 0;
}

