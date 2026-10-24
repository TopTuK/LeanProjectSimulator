import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuth } from '../stores/auth.js'
import { mockFetch, USER } from './helpers.js'

describe('auth store', () => {
  beforeEach(() => setActivePinia(createPinia()))

  it('loads the signed-in user', async () => {
    mockFetch({ 'GET /api/auth/me': [200, USER] })
    const auth = useAuth()
    expect(await auth.fetch()).toEqual(USER)
    expect(auth.user).toEqual(USER)
    expect(auth.loaded).toBe(true)
  })

  it('treats 401 as signed out', async () => {
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const auth = useAuth()
    expect(await auth.fetch()).toBeNull()
    expect(auth.user).toBeNull()
    expect(auth.loaded).toBe(true)
  })

  it('asks the server only once', async () => {
    const fetch = mockFetch({ 'GET /api/auth/me': [200, USER] })
    const auth = useAuth()
    await Promise.all([auth.fetch(), auth.fetch()])
    await auth.fetch()
    expect(fetch).toHaveBeenCalledTimes(1)
  })

  it('logout clears the user', async () => {
    const fetch = mockFetch({ 'GET /api/auth/me': [200, USER], 'POST /api/auth/logout': [204, null] })
    const auth = useAuth()
    await auth.fetch()
    await auth.logout()
    expect(auth.user).toBeNull()
    expect(fetch).toHaveBeenLastCalledWith('/api/auth/logout', expect.objectContaining({ method: 'POST' }))
  })

  it('login sends the browser to the chosen provider with the return path', () => {
    const assign = vi.fn()
    vi.stubGlobal('location', { ...window.location, assign })
    useAuth().login('yandex', '/control')
    expect(assign).toHaveBeenLastCalledWith('/api/auth/yandex/login?next=%2Fcontrol')
    useAuth().login('ok', '/control')
    expect(assign).toHaveBeenLastCalledWith('/api/auth/vk/login?provider=ok&next=%2Fcontrol')
  })

  it('chooseLogin opens the sign-in options on the landing page', () => {
    const assign = vi.fn()
    vi.stubGlobal('location', { ...window.location, assign })
    useAuth().chooseLogin('/sim/a/office')
    expect(assign).toHaveBeenCalledWith('/?login=1&next=%2Fsim%2Fa%2Foffice')
  })
})
