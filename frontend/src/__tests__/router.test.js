import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory } from 'vue-router'
import { createAppRouter } from '../router.js'
import { useAuth } from '../stores/auth.js'
import { mockFetch, USER } from './helpers.js'

async function setup(me) {
  mockFetch({ 'GET /api/auth/me': me })
  const auth = useAuth()
  auth.login = vi.fn()
  const router = createAppRouter(createMemoryHistory())
  await router.push('/')
  return { router, auth }
}

describe('router guard', () => {
  beforeEach(() => setActivePinia(createPinia()))

  it('keeps the landing page public', async () => {
    const { router, auth } = await setup([401, { detail: 'login required' }])
    expect(router.currentRoute.value.path).toBe('/')
    expect(auth.login).not.toHaveBeenCalled()
  })

  it('sends anonymous visitors of /control to the sign-in options', async () => {
    const { router, auth } = await setup([401, { detail: 'login required' }])
    await router.push('/control')
    expect(router.currentRoute.value.path).toBe('/')
    expect(router.currentRoute.value.query).toEqual({ login: '1', next: '/control' })
    expect(auth.login).not.toHaveBeenCalled()
  })

  it('keeps the full simulation path for after sign-in', async () => {
    const { router } = await setup([401, { detail: 'login required' }])
    await router.push('/sim/abc/gantt?tab=1')
    expect(router.currentRoute.value.query.next).toBe('/sim/abc/gantt?tab=1')
  })

  it('lets signed-in users through', async () => {
    const { router, auth } = await setup([200, USER])
    await router.push('/control')
    expect(router.currentRoute.value.path).toBe('/control')
    await router.push('/sim/abc')
    expect(router.currentRoute.value.path).toBe('/sim/abc/office')
    expect(auth.login).not.toHaveBeenCalled()
  })
})
