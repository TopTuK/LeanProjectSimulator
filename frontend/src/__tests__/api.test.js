import { describe, expect, it } from 'vitest'
import { api } from '../api.js'
import { jsonResponse, mockFetch, USER } from './helpers.js'

describe('api', () => {
  it('returns parsed JSON', async () => {
    const fetch = mockFetch({ 'GET /api/auth/me': [200, USER] })
    expect(await api.me()).toEqual(USER)
    expect(fetch).toHaveBeenCalledWith('/api/auth/me', expect.objectContaining({ method: 'GET' }))
  })

  it('sends JSON bodies', async () => {
    const fetch = mockFetch({ 'POST /api/sessions': [201, { id: 's1' }] })
    await api.create({ speed: 'test' })
    const opts = fetch.mock.calls[0][1]
    expect(opts.headers).toEqual({ 'Content-Type': 'application/json' })
    expect(JSON.parse(opts.body)).toEqual({ speed: 'test' })
  })

  it('errors carry status and server detail', async () => {
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    await expect(api.me()).rejects.toMatchObject({ status: 401, message: 'login required' })
  })

  it('falls back to status text when the body is not JSON', async () => {
    mockFetch({
      'GET /api/scenarios': () => ({ ...jsonResponse(502), json: async () => { throw new Error('html') } }),
    })
    await expect(api.scenarios()).rejects.toMatchObject({ status: 502, message: 'HTTP 502' })
  })

  it('logout tolerates an empty 204 response', async () => {
    mockFetch({ 'POST /api/auth/logout': () => ({ ...jsonResponse(204), json: async () => { throw new Error('empty') } }) })
    expect(await api.logout()).toBeNull()
  })

  it('write calls include a client action id', async () => {
    const fetch = mockFetch({ 'POST /api/sessions/s1/clock/start': [200, { id: 's1' }] })
    await api.start('s1')
    expect(JSON.parse(fetch.mock.calls[0][1].body).client_action_id).toBeTruthy()
  })

  it('builds the Yandex login URL with an encoded return path', () => {
    expect(api.loginUrl('/sim/a b/office?x=1')).toBe('/api/auth/yandex/login?next=%2Fsim%2Fa%20b%2Foffice%3Fx%3D1')
    expect(api.loginUrl()).toBe('/api/auth/yandex/login?next=%2F')
  })
})
