#!/usr/bin/env node
/**
 * Development shim that defers to the single Python launcher (start_ui.py).
 * Keeping this script allows `npm run dev` to keep working while ensuring
 * we only have one entry point that prompts for desktop vs web.
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const repoRoot = path.join(__dirname, '..', '..');
const launcher = path.join(repoRoot, 'start_ui.py');
const frontendDir = path.join(__dirname, '..');
const pythonCandidates = process.env.PYTHON
  ? [process.env.PYTHON]
  : process.platform === 'win32'
    ? ['py', 'python', 'python3']
    : ['python3', 'python'];
const npmCmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';

let fallbackStarted = false;

function runViteOnly(reason) {
  if (fallbackStarted) {
    return;
  }
  fallbackStarted = true;
  if (reason) {
    console.warn(`⚠️  ${reason}`);
  }
  console.warn('Launching Vite dev server directly (API/backend disabled).');
  const fallback = spawn(npmCmd, ['run', 'dev:web'], {
    cwd: frontendDir,
    stdio: 'inherit',
    env: {
      ...process.env,
      OSDASH_API_OFFLINE: '1',
      DEV_MODE: 'web',
    },
  });
  fallback.on('exit', (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
    } else {
      process.exit(code ?? 0);
    }
  });
}

function spawnLauncher(cmds) {
  if (cmds.length === 0) {
    runViteOnly('Unable to locate a Python interpreter for start_ui.py.');
    return;
  }

  const [cmd, ...rest] = cmds;
  const proc = spawn(cmd, [launcher], {
    cwd: repoRoot,
    stdio: 'inherit',
  });

  proc.on('error', (err) => {
    if (rest.length > 0) {
      spawnLauncher(rest);
      return;
    }
    runViteOnly(`Failed to launch start_ui.py: ${err.message}`);
  });

  proc.on('exit', (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
      return;
    }
    if ((code ?? 0) !== 0) {
      runViteOnly(`start_ui.py exited with code ${code}.`);
    } else {
      process.exit(0);
    }
  });
}

console.log('Forwarding to start_ui.py (single dev entry point)...');
spawnLauncher(pythonCandidates);
