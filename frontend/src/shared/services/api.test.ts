import { describe, it, expect, beforeEach } from 'vitest'

beforeEach(() => {
  localStorage.clear()
})

describe('API client', () => {
  it('has a base URL containing /api', async () => {
    const api = await import('./api')
    expect(api.default.defaults.baseURL).toContain('/api')
  })

  it('sets JSON content type', async () => {
    const api = await import('./api')
    expect(api.default.defaults.headers['Content-Type']).toBe('application/json')
  })
})
