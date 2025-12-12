const { app, BrowserWindow, Menu, ipcMain, dialog, shell } = require('electron');
const fs = require('fs');
const path = require('path');
const backendLauncher = require('./backendLauncher.cjs');

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
const BACKEND_HOST = process.env.BACKEND_HOST || '127.0.0.1';
const BACKEND_PORT = parseInt(process.env.BACKEND_PORT || '8000', 10);
const BACKEND_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}`;
process.env.OSDASH_BACKEND_URL = BACKEND_URL;
const DEFAULT_REPO_ROOT = path.resolve(__dirname, '../..');

// Keep a global reference of the window object
let mainWindow;
let backendProcess = null;

function resolveBackendRoot() {
  if (process.env.BACKEND_REPO_ROOT) {
    return path.resolve(process.env.BACKEND_REPO_ROOT);
  }
  if (app.isPackaged) {
    const candidates = [
      path.join(process.resourcesPath, 'backend'),
      path.join(process.resourcesPath, 'apps'),
      process.resourcesPath,
    ];
    for (const candidate of candidates) {
      if (fs.existsSync(candidate)) {
        return candidate;
      }
    }
  }
  return DEFAULT_REPO_ROOT;
}

function getFallbackIndexPath() {
  const overrides = [
    process.env.OSDASH_FALLBACK_INDEX,
    app.isPackaged ? path.join(process.resourcesPath, 'dist', 'index.html') : null,
    path.join(resolveBackendRoot(), 'frontend', 'dist', 'index.html'),
  ].filter(Boolean);
  for (const candidate of overrides) {
    if (candidate && fs.existsSync(candidate)) {
      return candidate;
    }
  }
  return null;
}

async function loadFallbackBundle(targetWindow) {
  const fallbackPath = getFallbackIndexPath();
  if (fallbackPath) {
    console.warn(`[Electron] Loading fallback bundle from ${fallbackPath}`);
    await targetWindow.loadFile(fallbackPath);
    dialog.showMessageBox(targetWindow, {
      type: 'warning',
      title: 'Backend unavailable',
      message: 'FastAPI backend is offline.',
      detail: `The desktop shell loaded a local build instead. Start the backend on ${BACKEND_URL} for live data.`,
    });
    return;
  }

  const html = `<!doctype html><html><body style="background:#0f172a;color:#fff;font-family:system-ui;display:flex;align-items:center;justify-content:center;height:100vh;text-align:center;">
    <div><h1>Backend unavailable</h1><p>Start the FastAPI backend on ${BACKEND_URL} then relaunch the desktop app.</p></div>
  </body></html>`;
  await targetWindow.loadURL(`data:text/html,${encodeURIComponent(html)}`);
}

async function ensureBackendReady() {
  if (isDev) {
    return true;
  }
  try {
    const repoRoot = resolveBackendRoot();
    const result = await backendLauncher.ensureBackendServer({
      backendUrl: BACKEND_URL,
      host: BACKEND_HOST,
      port: BACKEND_PORT,
      repoRoot,
    });
    backendProcess = result.process;
    if (result.alreadyRunning) {
      console.log(`[Electron] Backend server already running at ${BACKEND_URL}`);
    } else {
      console.log('[Electron] Backend server started via Electron host');
    }
    if (backendProcess) {
      backendProcess.on('exit', (code, signal) => {
        console.warn(`[Electron] Backend exited (code=${code} signal=${signal ?? 'none'})`);
      });
    }
    return true;
  } catch (error) {
    console.error('[Electron] Backend startup failed:', error);
    dialog.showErrorBox(
      'Backend startup failed',
      [
        'The FastAPI server did not start automatically.',
        'Ensure Python + uvicorn dependencies are installed or start the API manually:',
        'python start_ui.py --mode desktop',
        '',
        String(error && error.message ? error.message : error),
      ].join('\n'),
    );
    return false;
  }
}

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    backgroundColor: '#0f172a',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: true,
    },
    icon: path.join(__dirname, 'icons', getIconFileName()),
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    show: false, // Don't show until ready
  });

  // Load the app
  const startUrl = isDev
    ? (process.env.VITE_DEV_SERVER_URL || 'http://localhost:5173')
    : `${BACKEND_URL}/app/`;

  const loadApp = () => {
    console.log(`[Electron] Loading app from: ${startUrl}`);
    return mainWindow.loadURL(startUrl).catch((error) => {
      console.error('[Electron] Failed to load primary URL:', error);
      return loadFallbackBundle(mainWindow);
    });
  };

  if (isDev) {
    loadApp();
  } else {
    ensureBackendReady()
      .then((ready) => {
        if (ready) {
          return loadApp();
        }
        return loadFallbackBundle(mainWindow);
      })
      .catch((error) => {
        console.error('[Electron] Backend readiness check failed:', error);
        return loadFallbackBundle(mainWindow);
      });
  }

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Open DevTools in development
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Create application menu
  createMenu();
}

function getIconFileName() {
  const platform = process.platform;
  if (platform === 'darwin') return 'icon.icns';
  if (platform === 'win32') return 'icon.ico';
  return 'icon.png';
}

function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Settings',
          accelerator: 'CmdOrCtrl+,',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.send('navigate-to', '/settings');
            }
          },
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          },
        },
      ],
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo', label: 'Undo' },
        { role: 'redo', label: 'Redo' },
        { type: 'separator' },
        { role: 'cut', label: 'Cut' },
        { role: 'copy', label: 'Copy' },
        { role: 'paste', label: 'Paste' },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload', label: 'Reload' },
        { role: 'forceReload', label: 'Force Reload' },
        { role: 'toggleDevTools', label: 'Toggle Developer Tools' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Actual Size' },
        { role: 'zoomIn', label: 'Zoom In' },
        { role: 'zoomOut', label: 'Zoom Out' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Toggle Full Screen' },
      ],
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize', label: 'Minimize' },
        { role: 'close', label: 'Close' },
      ],
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About OS Dashboard AI Assistant',
              message: 'OS Dashboard AI Assistant',
              detail: 'Version 0.1.0\nA unified dashboard for AI-powered task and project management.',
            });
          },
        },
      ],
    },
  ];

  // macOS specific menu adjustments
  if (process.platform === 'darwin') {
    template.unshift({
      label: app.getName(),
      submenu: [
        { role: 'about', label: 'About ' + app.getName() },
        { type: 'separator' },
        { role: 'services', label: 'Services' },
        { type: 'separator' },
        { role: 'hide', label: 'Hide ' + app.getName() },
        { role: 'hideOthers', label: 'Hide Others' },
        { role: 'unhide', label: 'Show All' },
        { type: 'separator' },
        { role: 'quit', label: 'Quit ' + app.getName() },
      ],
    });

    // Window menu
    template[4].submenu = [
      { role: 'close', label: 'Close' },
      { role: 'minimize', label: 'Minimize' },
      { role: 'zoom', label: 'Zoom' },
      { type: 'separator' },
      { role: 'front', label: 'Bring All to Front' },
    ];
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// IPC handlers for desktop-specific features
ipcMain.handle('get-platform', () => {
  return process.platform;
});

ipcMain.handle('show-open-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options);
  return result;
});

ipcMain.handle('show-save-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options);
  return result;
});

ipcMain.handle('show-message-box', async (event, options) => {
  const result = await dialog.showMessageBox(mainWindow, options);
  return result;
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('get-app-path', () => {
  return app.getAppPath();
});

// App event handlers
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    // On macOS, re-create window when dock icon is clicked
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('before-quit', () => {
  if (backendProcess) {
    console.log('[Electron] Stopping backend server...');
    backendProcess.kill();
    backendProcess = null;
  }
});

app.on('window-all-closed', () => {
  // On macOS, keep app running even when all windows are closed
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });
});
