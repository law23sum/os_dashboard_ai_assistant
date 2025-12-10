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
const pythonCandidates = process.env.PYTHON
  ? [process.env.PYTHON]
  : process.platform === 'win32'
    ? ['py', 'python', 'python3']
    : ['python3', 'python'];

function spawnLauncher(cmds) {
  if (cmds.length === 0) {
    console.error('Unable to locate python executable. Set the PYTHON env var.');
    process.exit(1);
  }

  const [cmd, ...rest] = cmds;
  const proc = spawn(cmd, [launcher], {
    cwd: repoRoot,
    stdio: 'inherit',
  });

  proc.on('error', (err) => {
    if (rest.length > 0) {
      spawnLauncher(rest);
    } else {
      console.error('Failed to launch start_ui.py:', err.message);
      process.exit(1);
    }
  });

  proc.on('exit', (code) => process.exit(code || 0));
}

console.log('Forwarding to start_ui.py (single dev entry point)...');
spawnLauncher(pythonCandidates);
