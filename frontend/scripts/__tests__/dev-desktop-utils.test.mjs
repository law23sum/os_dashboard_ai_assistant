import test from 'node:test'
import assert from 'node:assert/strict'
import { checkPortAvailable } from '../dev-desktop-utils.js'

function createNetStub(behaviors) {
  return {
    createServer() {
      let errorHandler = () => {}
      const server = {
        unref() {},
        once(event, handler) {
          if (event === 'error') {
            errorHandler = handler
          }
        },
        listen(options, onListen) {
          const behavior = behaviors[options.host] || {}
          if (behavior.errorCode) {
            const err = new Error(`Host ${options.host} failed`)
            err.code = behavior.errorCode
            errorHandler(err)
            return
          }
          onListen()
        },
        close(callback) {
          if (callback) callback()
        },
      }
      return server
    },
  }
}

test('allows IPv4 probe when IPv6 is not supported', async () => {
  const netStub = createNetStub({
    '::1': { errorCode: 'EAFNOSUPPORT' },
  })
  const result = await checkPortAvailable(55173, netStub)
  assert.equal(result, true)
})

test('returns false when IPv4 loopback is unavailable', async () => {
  const netStub = createNetStub({
    '127.0.0.1': { errorCode: 'EADDRINUSE' },
  })
  const result = await checkPortAvailable(55174, netStub)
  assert.equal(result, false)
})

test('fails fast when IPv6 loopback is already bound', async () => {
  const netStub = createNetStub({
    '::1': { errorCode: 'EADDRINUSE' },
  })
  const result = await checkPortAvailable(55175, netStub)
  assert.equal(result, false)
})
