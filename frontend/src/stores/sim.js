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

function forgetSession(id) {
  try {
    if (localStorage.getItem(LAST_KEY) === id) localStorage.removeItem(LAST_KEY)
  } catch {}
}

export const useSim = defineStore('sim', () => {
  const state = ref(null)
  const sessions = ref([])
  const snapshots = ref([])
  const error = ref('')
  const busy = ref(false)
  const listBusy = ref(false)
  const deleting = ref(null)
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
      if (e.status === 401) useAuth().chooseLogin(window.location.pathname)
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

  async function loadSessions() {
    error.value = ''
    listBusy.value = true
    try {
      sessions.value = await api.list()
      return sessions.value
    } catch (e) {
      if (e.status === 401) useAuth().chooseLogin(window.location.pathname)
      error.value = e.message
      throw e
    } finally {
      listBusy.value = false
    }
  }

  async function remove(sessionId) {
    error.value = ''
    deleting.value = sessionId
    try {
      await api.remove(sessionId)
      sessions.value = sessions.value.filter((s) => s.id !== sessionId)
      if (state.value?.id === sessionId) {
        disconnect()
        state.value = null
        snapshots.value = []
      }
      forgetSession(sessionId)
    } catch (e) {
      if (e.status === 401) useAuth().chooseLogin(window.location.pathname)
      error.value = e.message
      throw e
    } finally {
      deleting.value = null
    }
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
    state, sessions, snapshots, error, busy, listBusy, deleting, running, ended, unread, openDecisions, activity, resource,
    create, load, loadSessions, remove, disconnect,
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
