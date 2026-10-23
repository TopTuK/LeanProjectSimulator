import { vi } from 'vitest'

export function jsonResponse(status, body) {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: `HTTP ${status}`,
    json: async () => body,
  }
}

// fetch stub answering by "METHOD /path"; unknown routes are 404
export function mockFetch(routes) {
  const fn = vi.fn(async (url, opts = {}) => {
    const key = `${opts.method ?? 'GET'} ${url}`
    const hit = routes[key]
    if (!hit) return jsonResponse(404, { detail: 'not found' })
    return typeof hit === 'function' ? hit(opts) : jsonResponse(...hit)
  })
  vi.stubGlobal('fetch', fn)
  return fn
}

export const USER = { id: 7, login: 'ivan', name: 'Ivan Petrov', email: 'ivan@yandex.ru', avatar_url: null }
