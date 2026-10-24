import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api.js'

export const useAuth = defineStore('auth', () => {
  const user = ref(null)
  const loaded = ref(false)
  let pending = null

  // asks the server once; later calls reuse the answer
  function fetch() {
    if (loaded.value) return Promise.resolve(user.value)
    pending ??= api
      .me()
      .then((me) => (user.value = me))
      .catch((e) => {
        if (e.status !== 401) console.warn('auth check failed', e)
        user.value = null
      })
      .then(() => {
        loaded.value = true
        pending = null
        return user.value
      })
    return pending
  }

  function login(provider = 'yandex', next = '/') {
    window.location.assign(api.loginUrl(provider, next))
  }

  // the landing page lists the providers and comes back to next
  function chooseLogin(next = '/') {
    window.location.assign(`/?login=1&next=${encodeURIComponent(next)}`)
  }

  async function logout() {
    await api.logout()
    user.value = null
  }

  return { user, loaded, fetch, login, chooseLogin, logout }
})
