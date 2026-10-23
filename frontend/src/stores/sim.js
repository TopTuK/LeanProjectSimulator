import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api } from '../api.js'
import { useAuth } from './auth.js'

const LAST_KEY = 'simultrain:last-session'

export function lastSessionId() {
  try {
    return localStorage.getItem(LAST_KEY)
  } catch {
    return null
  }
}

function rememberSession(id) {
  try {
    localStorage.setItem(LAST_KEY, id)
  } catch {}
}

export const useSim = defineStore('sim', () => {
  const state = ref(null)
  const snapshots = ref([])
  const error = ref('')
  const busy = ref(false)
  let source = null

  const running = computed(() => state.value?.status === 'running')
  const ended = computed(() => state.value?.status === 'ended')
  const unread = computed(() => state.value?.messages.filter((m) => !m.read) ?? [])
  const openDecisions = computed(() => state.value?.decisions.filter((d) => d.status === 'open') ?? [])
  const activity = (no) => state.value?.activities.find((a) => a.no === no)
  const resource = (no) => state.value?.resources.find((r) => r.no === no)

  function apply(next) {
    state.value = next
    if (next.status === 'running') connect()
    else disconnect()
  }

  async function run(fn) {
    error.value = ''
    busy.value = true
    try {
      const next = await fn()
      if (next && next.id) apply(next)
      return next
    } catch (e) {
      // signed out elsewhere or the cookie expired: sign in again and come back
      if (e.status === 401) useAuth().login(window.location.pathname)
      error.value = e.message
      throw e
    } finally {
      busy.value = false
    }
  }

  function connect() {
    if (source || !state.value) return
    source = api.stream(state.value.id)
    source.onmessage = (ev) => {
      const next = JSON.parse(ev.data)
      state.value = next
      if (next.status !== 'running') disconnect()
    }
    source.onerror = () => {
      // EventSource retries on its own; drop it if the session has stopped
      if (state.value?.status !== 'running') disconnect()
    }
  }

  function disconnect() {
    source?.close()
    source = null
  }

  async function create(cfg) {
    const next = await run(() => api.create(cfg))
    rememberSession(next.id)
    return next
  }

  async function load(id) {
    if (state.value?.id === id) return state.value
    disconnect()
    state.value = null
    const next = await run(() => api.get(id))
    rememberSession(id)
    return next
  }

  const id = () => state.value.id

  return {
    state, snapshots, error, busy, running, ended, unread, openDecisions, activity, resource,
    create, load, disconnect,
    start: () => run(() => api.start(id())),
    pause: () => run(() => api.pause(id())),
    decide: (decisionId, option) => run(() => api.decide(id(), decisionId, option)),
    read: (messageId) => run(() => api.read(id(), messageId)),
    setAssignments: (list) => run(() => api.setAssignments(id(), list)),
    leveling: () => api.leveling(id()),
    async loadSnapshots() {
      snapshots.value = await api.snapshots(id())
    },
  }
})
