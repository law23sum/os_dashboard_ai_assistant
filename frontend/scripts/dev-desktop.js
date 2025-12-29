#!/usr/bin/env node
/**
 * Desktop development entry point that keeps Electron and Vite in sync.
 *
 * Historically the desktop workflow launched `npm run dev:web-only` and a
 * separate Electron process that assumed Vite always bound to port 5173. When
 * that port was occupied (for example, a lingering web preview), the Vite
 * subprocess exited immediately and Electron rendered a blank page.
 *
 * This script discovers a free port, boots Vite with the forwarded --port
 * argument, waits for it to come online, and then launches Electron pointed at
 * that exact origin. It also relays process exits (Ctrl+C propagates to both
 * children) so the launcher never gets stuck with zombie Node processes.
 */

import { spawn, spawnSync } from 'child_process'
import path from 'path'
import fs from 'fs'
import net from 'net'
import { fileURLToPath } from 'url'
import { checkPortAvailable } from './dev-desktop-utils.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const repoRoot = path.resolve(__dirname, '..', '..')
const frontendDir = path.join(repoRoot, 'frontend')
const npmCmd = process.platform === 'win32' ? 'npm.cmd' : 'npm'
const pythonCandidates = process.env.PYTHON
  ? [process.env.PYTHON]
  : process.platform === 'win32'
    ? ['py', 'python', 'python3']
    : ['python3', 'python']
const electronBin = process.platform === 'win32'
  ? path.join(frontendDir, 'node_modules', '.bin', 'electron.cmd')
  : path.join(frontendDir, 'node_modules', '.bin', 'electron')

const DEFAULT_PORT = Number(process.env.VITE_DEV_SERVER_PORT || process.env.PORT || 5173)
const PORT_SCAN_LIMIT = 30

let viteProcess = null
let electronProcess = null
let autoFixProcess = null
let shuttingDown = false

const logPrefix = (label) => `[dev-desktop] ${label}`

async function findAvailablePort(startPort) {
  let candidate = startPort
  for (let attempts = 0; attempts < PORT_SCAN_LIMIT; attempts += 1) {
    // eslint-disable-next-line no-await-in-loop
    const open = await checkPortAvailable(candidate)
    if (open) {
      return candidate
    }
    candidate += 1
  }
  throw new Error(`Unable to locate a free port near ${startPort}. Close existing Vite/Electron windows.`)
}

function waitForPort(port, timeoutMs = 20000) {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + timeoutMs

    const tryConnect = () => {
      const socket = net.createConnection(port, '127.0.0.1')
      socket.once('connect', () => {
        socket.end()
        resolve(true)
      })
      socket.once('error', (err) => {
        socket.destroy()
        if (Date.now() > deadline) {
          reject(new Error(`Timed out waiting for Vite on port ${port}: ${err && err.message ? err.message : err}`))
          return
        }
        setTimeout(tryConnect, 250)
      })
    }

    tryConnect()
  })
}

function ensureElectronBinary() {
  if (fs.existsSync(electronBin)) {
    return electronBin
  }
  const fallback = process.platform === 'win32' ? 'npx.cmd' : 'npx'
  return fallback
}

function shutdown(code = 0) {
  if (shuttingDown) return
  shuttingDown = true
  const procs = [
    { name: 'vite', proc: viteProcess },
    { name: 'electron', proc: electronProcess },
  ]
  procs.forEach(({ proc }) => {
    if (proc && proc.exitCode == null) {
      proc.kill('SIGINT')
    }
  })
  Promise.all(
    procs.map(
      ({ proc }) =>
        new Promise((resolve) => {
          if (!proc) {
            resolve()
            return
          }
          if (proc.exitCode != null) {
            resolve()
            return
          }
          proc.once('exit', () => resolve())
        }),
    ),
  ).finally(() => {
    stopAutoFixMonitor()
    process.exit(code)
  })
}

function resolvePythonBinary() {
  for (const candidate of pythonCandidates) {
    try {
      spawnSync(candidate, ['--version'], { stdio: 'ignore' })
      return candidate
    } catch (err) {
      // keep searching
    }
  }
  return null
}

function startAutoFixMonitor() {
  if (process.env.OSDASH_DISABLE_AUTOFIX?.toLowerCase() === 'true') {
    return
  }
  if (process.env.OSDASH_AUTOFIX_ACTIVE) {
    return
  }
  const scriptPath = path.join(repoRoot, 'scripts', 'ai_auto_fix.py')
  if (!fs.existsSync(scriptPath)) {
    return
  }
  const pythonCmd = resolvePythonBinary()
  if (!pythonCmd) {
    console.warn(logPrefix('Unable to locate Python interpreter for auto-fix monitor.'))
    return
  }
  const args = [scriptPath, '--backend', 'none', '--frontend', 'none', '--logs-only', '--daemon']
  const env = {
    ...process.env,
    PYTHONUNBUFFERED: '1',
  }
  try {
    autoFixProcess = spawn(pythonCmd, args, {
      cwd: repoRoot,
      env,
      stdio: 'ignore',
    })
    const pidString = String(autoFixProcess.pid)
    process.env.OSDASH_AUTOFIX_ACTIVE = pidString
    autoFixProcess.once('exit', (code) => {
      if (process.env.OSDASH_AUTOFIX_ACTIVE === pidString) {
        delete process.env.OSDASH_AUTOFIX_ACTIVE
      }
      autoFixProcess = null
      console.log(logPrefix(`Auto-fix monitor exited (${code ?? 0}).`))
    })
    console.log(logPrefix('Auto-fix monitor started (frontend fallback).'))
  } catch (error) {
    console.warn(
      logPrefix(`Failed to start auto-fix monitor: ${error && error.message ? error.message : error}`),
    )
    autoFixProcess = null
  }
}

function stopAutoFixMonitor() {
  if (!autoFixProcess) {
    return
  }
  if (autoFixProcess.exitCode == null) {
    autoFixProcess.kill('SIGINT')
  }
  if (process.env.OSDASH_AUTOFIX_ACTIVE === String(autoFixProcess.pid)) {
    delete process.env.OSDASH_AUTOFIX_ACTIVE
  }
  autoFixProcess = null
}

async function main() {
  try {
    startAutoFixMonitor()
    const port = await findAvailablePort(DEFAULT_PORT)
    console.log(logPrefix(`Using Vite dev server port ${port}`))

    const commonEnv = {
      ...process.env,
      DEV_MODE: 'desktop',
      OSDASH_UI_MODE: 'desktop',
      VITE_DEV_SERVER_PORT: String(port),
      PORT: String(port),
    }

    viteProcess = spawn(
      npmCmd,
      ['run', 'dev:web-only', '--', '--port', String(port), '--strictPort'],
      {
        cwd: frontendDir,
        env: commonEnv,
        stdio: 'inherit',
      },
    )

    viteProcess.once('exit', (code) => {
      if (shuttingDown) return
      console.error(logPrefix(`Vite process exited with code ${code ?? 0}`))
      shutdown(code ?? 1)
    })

    await waitForPort(port)
    console.log(logPrefix(`Vite is ready on http://localhost:${port}`))

    const electronEnv = {
      ...commonEnv,
      NODE_ENV: 'development',
      VITE_DEV_SERVER_URL: `http://localhost:${port}`,
    }

    const electronCmd = ensureElectronBinary()
    const electronArgs =
      electronCmd === electronBin
        ? ['.']
        : ['electron', '.']

    electronProcess = spawn(electronCmd, electronArgs, {
      cwd: frontendDir,
      env: electronEnv,
      stdio: 'inherit',
    })

    electronProcess.once('exit', (code, signal) => {
      if (shuttingDown) return
      if (signal === 'SIGINT') {
        shutdown(0)
        return
      }
      console.log(logPrefix(`Electron exited with code ${code ?? 0}`))
      shutdown(code ?? 0)
    })

    const handleExit = () => shutdown(0)
    process.on('SIGINT', handleExit)
    process.on('SIGTERM', handleExit)
  } catch (error) {
    console.error(logPrefix(error instanceof Error ? error.message : String(error)))
    shutdown(1)
  }
}

main()
