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

  it('loads all session summaries', async () => {
    mockFetch({ 'GET /api/sessions': [200, [{ id: 's1' }, { id: 's2' }]] })
    const sim = useSim()
    await sim.loadSessions()
    expect(sim.sessions.map((s) => s.id)).toEqual(['s1', 's2'])
    expect(sim.listBusy).toBe(false)
  })

  it('removes a running session and cleans up its stream and remembered id', async () => {
    const close = vi.fn()
    vi.stubGlobal('EventSource', class {
      constructor() { this.close = close }
    })
    mockFetch({
      'GET /api/sessions/s1': [200, { ...STATE, status: 'running' }],
      'DELETE /api/sessions/s1': [204, null],
    })
    const sim = useSim()
    await sim.load('s1')
    sim.sessions = [{ id: 's1' }, { id: 's2' }]
    await sim.remove('s1')
    expect(close).toHaveBeenCalledOnce()
    expect(sim.state).toBeNull()
    expect(sim.sessions).toEqual([{ id: 's2' }])
    expect(lastSessionId()).toBeNull()
    expect(sim.deleting).toBeNull()
  })
})
