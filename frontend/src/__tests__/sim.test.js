import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { lastSessionId, useSim } from '../stores/sim.js'
import { useAuth } from '../stores/auth.js'
import { mockFetch } from './helpers.js'

const STATE = { id: 's1', status: 'ready', messages: [{ id: 1, read: false }], decisions: [], activities: [], resources: [] }

describe('sim store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('creates a session and remembers it', async () => {
    mockFetch({ 'POST /api/sessions': [201, STATE] })
    const sim = useSim()
    await sim.create({ speed: 'test' })
    expect(sim.state.id).toBe('s1')
    expect(sim.unread).toHaveLength(1)
    expect(lastSessionId()).toBe('s1')
    expect(sim.busy).toBe(false)
  })

  it('keeps the server error message', async () => {
    mockFetch({ 'POST /api/sessions/s1/clock/start': [409, { detail: 'simulation has ended' }], 'GET /api/sessions/s1': [200, STATE] })
    const sim = useSim()
    await sim.load('s1')
    await expect(sim.start()).rejects.toMatchObject({ status: 409 })
    expect(sim.error).toBe('simulation has ended')
  })

  it('sends the player to sign in when the login has expired', async () => {
    mockFetch({ 'GET /api/sessions/s1': [401, { detail: 'login required' }] })
    const auth = useAuth()
    auth.chooseLogin = vi.fn()
    await expect(useSim().load('s1')).rejects.toMatchObject({ status: 401 })
    expect(auth.chooseLogin).toHaveBeenCalledWith(window.location.pathname)
  })
})
