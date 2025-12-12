const test = require('node:test');
const assert = require('node:assert/strict');
const http = require('http');

const backendLauncher = require('../backendLauncher.cjs');

async function startServer(responder) {
  const server = http.createServer(responder);
  return new Promise((resolve, reject) => {
    const onError = (error) => {
      server.off('error', onError);
      try {
        server.close();
      } catch {
        // ignore
      }
      if (error && error.code === 'EPERM') {
        resolve(null);
        return;
      }
      reject(error);
    };
    server.once('error', onError);
    try {
      server.listen(0, '127.0.0.1', () => {
        server.off('error', onError);
        const { port } = server.address();
        resolve({ server, port });
      });
    } catch (error) {
      onError(error);
    }
  });
}

test('buildBackendArgs uses custom entry, host, and port', () => {
  const args = backendLauncher.buildBackendArgs('module:app', '0.0.0.0', 9999);
  assert.deepEqual(args, ['-m', 'uvicorn', 'module:app', '--factory', '--host', '0.0.0.0', '--port', '9999']);
});

test('resolvePythonExecutable honors overrides', () => {
  const command = backendLauncher.resolvePythonExecutable({
    OSDASH_BACKEND_PYTHON: '/custom/python',
  });
  assert.strictEqual(command, '/custom/python');
});

test('checkBackendServer detects healthy HTTP server', async (t) => {
  const serverInfo = await startServer((req, res) => {
    if (req.url === '/health') {
      res.writeHead(200).end('ok');
    } else {
      res.writeHead(404).end();
    }
  });
  if (!serverInfo) {
    t.skip('Binding to 127.0.0.1 is not permitted in this environment.');
    return;
  }
  const { server, port } = serverInfo;
  try {
    const ok = await backendLauncher.checkBackendServer(`http://127.0.0.1:${port}`);
    assert.equal(ok, true);
  } finally {
    server.close();
  }
});

test('waitForBackendReady resolves once the server responds', async (t) => {
  const serverInfo = await startServer((req, res) => {
    res.writeHead(200).end('ok');
  });
  if (!serverInfo) {
    t.skip('Binding to 127.0.0.1 is not permitted in this environment.');
    return;
  }
  const { server, port } = serverInfo;
  try {
    const ready = await backendLauncher.waitForBackendReady(`http://127.0.0.1:${port}`, {
      timeoutMs: 1500,
      pollInterval: 100,
    });
    assert.equal(ready, true);
  } finally {
    server.close();
  }
});
