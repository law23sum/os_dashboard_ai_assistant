const { spawn, spawnSync } = require('child_process');
const http = require('http');
const https = require('https');
const path = require('path');

const DEFAULT_ENTRY_POINT =
  process.env.BACKEND_ENTRY || 'assistant_hub.api.server:create_app';
const HEALTH_PATHS = ['/health', '/api/health', '/app/'];
const DEFAULT_TIMEOUT_MS = 45_000;
const PYTHON_OVERRIDE_KEYS = [
  'OSDASH_BACKEND_PYTHON',
  'OSDASH_PYTHON',
  'PYTHON_OVERRIDE',
];

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function buildHealthUrls(baseUrl, paths = HEALTH_PATHS) {
  return paths.map((suffix) => {
    try {
      return new URL(suffix, baseUrl).toString();
    } catch {
      return `${baseUrl.replace(/\/+$/, '')}${suffix}`;
    }
  });
}

function checkBackendServer(baseUrl, { paths = HEALTH_PATHS, timeoutMs = 2000 } = {}) {
  const urls = buildHealthUrls(baseUrl, paths);
  return new Promise((resolve) => {
    const tryIndex = (index) => {
      if (index >= urls.length) {
        resolve(false);
        return;
      }
      const target = urls[index];
      const lib = target.startsWith('https') ? https : http;
      const req = lib
        .get(target, { timeout: timeoutMs }, (res) => {
          const ok = (res.statusCode || 500) < 400;
          res.resume();
          if (ok) {
            resolve(true);
          } else {
            tryIndex(index + 1);
          }
        })
        .on('error', () => tryIndex(index + 1))
        .on('timeout', () => {
          req.destroy();
          tryIndex(index + 1);
        });
    };
    tryIndex(0);
  });
}

async function waitForBackendReady(
  baseUrl,
  { timeoutMs = DEFAULT_TIMEOUT_MS, pollInterval = 750, paths = HEALTH_PATHS } = {},
) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (await checkBackendServer(baseUrl, { paths })) {
      return true;
    }
    await delay(pollInterval);
  }
  throw new Error(`Backend did not respond within ${timeoutMs}ms`);
}

function detectPythonCandidates(
  env = process.env,
  { platform = process.platform, execPath = process.execPath } = {},
) {
  const seen = new Set();
  const push = (value) => {
    if (value && !seen.has(value)) {
      seen.add(value);
    }
  };

  PYTHON_OVERRIDE_KEYS.forEach((key) => push(env[key]));
  if (env.PYTHON_EXECUTABLE) push(env.PYTHON_EXECUTABLE);
  if (env.PYTHON) push(env.PYTHON);
  if (env.PYTHON3) push(env.PYTHON3);
  if (env.py) push(env.py);
  if (env.VIRTUAL_ENV) {
    const suffix = platform === 'win32' ? '\\Scripts\\python.exe' : '/bin/python3';
    push(path.join(env.VIRTUAL_ENV, suffix));
  }
  if (execPath && /python/i.test(path.basename(execPath))) {
    push(execPath);
  }

  if (platform === 'win32') {
    push('python.exe');
    push('py');
  } else {
    push('python3');
    push('python');
  }
  return Array.from(seen).filter(Boolean);
}

function resolvePythonExecutable(env = process.env) {
  for (const key of PYTHON_OVERRIDE_KEYS) {
    if (env[key]) {
      return env[key];
    }
  }
  const candidates = detectPythonCandidates(env);
  for (const candidate of candidates) {
    try {
      const result = spawnSync(candidate, ['--version'], {
        stdio: 'ignore',
      });
      if ((result.status ?? 1) === 0) {
        return candidate;
      }
    } catch {
      continue;
    }
  }
  throw new Error('Unable to locate a Python interpreter for the backend');
}

function buildBackendArgs(entryPoint, host, port) {
  return ['-m', 'uvicorn', entryPoint, '--factory', '--host', host, '--port', String(port)];
}

function spawnBackendProcess({
  pythonCommand,
  host,
  port,
  entryPoint = DEFAULT_ENTRY_POINT,
  repoRoot,
}) {
  const args = buildBackendArgs(entryPoint, host, port);
  const child = spawn(pythonCommand, args, {
    cwd: repoRoot,
    env: { ...process.env, WATCHFILES_FORCE_POLLING: '1' },
    stdio: 'inherit',
  });
  child.on('error', (error) => {
    console.error('[Electron] Backend process error:', error);
  });
  return child;
}

async function ensureBackendServer({
  backendUrl,
  host,
  port,
  repoRoot,
  timeoutMs = DEFAULT_TIMEOUT_MS,
  entryPoint = DEFAULT_ENTRY_POINT,
}) {
  const alreadyRunning = await checkBackendServer(backendUrl);
  if (alreadyRunning) {
    return { alreadyRunning: true, process: null };
  }
  const pythonCommand = resolvePythonExecutable();
  const child = spawnBackendProcess({ pythonCommand, host, port, entryPoint, repoRoot });
  try {
    await waitForBackendReady(backendUrl, { timeoutMs });
    return { alreadyRunning: false, process: child };
  } catch (error) {
    child.kill();
    throw error;
  }
}

module.exports = {
  HEALTH_PATHS,
  DEFAULT_ENTRY_POINT,
  buildHealthUrls,
  checkBackendServer,
  waitForBackendReady,
  detectPythonCandidates,
  resolvePythonExecutable,
  buildBackendArgs,
  spawnBackendProcess,
  ensureBackendServer,
};
