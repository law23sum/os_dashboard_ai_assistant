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

import { spawn } from 'child_process'
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
const electronBin = process.platform === 'win32'
  ? path.join(frontendDir, 'node_modules', '.bin', 'electron.cmd')
  : path.join(frontendDir, 'node_modules', '.bin', 'electron')

const DEFAULT_PORT = Number(process.env.VITE_DEV_SERVER_PORT || process.env.PORT || 5173)
const PORT_SCAN_LIMIT = 30

let viteProcess = null
let electronProcess = null
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
    process.exit(code)
  })
}

async function main() {
  try {
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
