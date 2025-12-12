import net from 'net'

const OPTIONAL_IPV6_ERRORS = new Set(['EADDRNOTAVAIL', 'EAFNOSUPPORT', 'EINVAL', 'ENETUNREACH'])

function probeHost(port, host, skipErrors = OPTIONAL_IPV6_ERRORS, netModule = net) {
  return new Promise((resolve) => {
    const server = netModule.createServer()
    if (typeof server.unref === 'function') {
      server.unref()
    }

    let settled = false
    const settle = (result) => {
      if (settled) return
      settled = true
      resolve(result)
    }

    server.once('error', (err) => {
      if (skipErrors.has(err?.code)) {
        settle({ available: true, skipped: true })
        return
      }
      settle({ available: false, skipped: false })
    })

    server.listen({ port, host, exclusive: true }, () => {
      if (typeof server.close === 'function') {
        server.close(() => settle({ available: true, skipped: false }))
        return
      }
      settle({ available: true, skipped: false })
    })
  })
}

export async function checkPortAvailable(port, netModule = net) {
  const ipv6Result = await probeHost(port, '::1', OPTIONAL_IPV6_ERRORS, netModule)
  if (!ipv6Result.available && !ipv6Result.skipped) {
    return false
  }
  const ipv4Loopback = await probeHost(port, '127.0.0.1', new Set(), netModule)
  if (!ipv4Loopback.available) {
    return false
  }
  const ipv4Any = await probeHost(port, '0.0.0.0', new Set(), netModule)
  return ipv4Any.available
}
