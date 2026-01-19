import { describe, it, expect } from 'vitest'

import { normalizeApiBase } from '../../lib/apiClient'

describe('normalizeApiBase', () => {
  it('adds /api when given a host-only url', () => {
    expect(normalizeApiBase('http://localhost:8000')).toBe('http://localhost:8000/api')
  })

  it('keeps existing api path', () => {
    expect(normalizeApiBase('http://localhost:8000/api')).toBe('http://localhost:8000/api')
  })

  it('normalizes root to /api', () => {
    expect(normalizeApiBase('/')).toBe('/api')
  })

  it('prefixes relative base paths', () => {
    expect(normalizeApiBase('api')).toBe('/api')
  })

  it('preserves non-root absolute paths', () => {
    expect(normalizeApiBase('https://example.com/v1')).toBe('https://example.com/v1')
  })
})
