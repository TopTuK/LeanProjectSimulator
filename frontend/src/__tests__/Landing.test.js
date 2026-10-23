import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import i18n, { setLocale } from '../i18n/index.js'
import Landing from '../pages/Landing.vue'
import { useAuth } from '../stores/auth.js'
import { mockFetch, USER } from './helpers.js'

async function render(query = '') {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: Landing },
      { path: '/control', component: { template: '<div />' } },
    ],
  })
  await router.push(`/${query}`)
  const wrapper = mount(Landing, { global: { plugins: [router, i18n] } })
  await flushPromises()
  return wrapper
}

describe('Landing', () => {
  let pinia
  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    setLocale('en')
  })

  it('asks anonymous visitors to sign in with Yandex', async () => {
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const w = await render()
    expect(w.find('[data-test="start"]').exists()).toBe(false)
    expect(w.find('[data-test="login-start"]').text()).toContain('Sign in with Yandex to start')
    expect(w.find('[data-test="login"]').exists()).toBe(true)
  })

  it('sign-in button returns to the control page', async () => {
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const auth = useAuth()
    auth.login = vi.fn()
    const w = await render()
    await w.find('[data-test="login-start"]').trigger('click')
    expect(auth.login).toHaveBeenCalledWith('/control')
  })

  it('offers Start and the user name when signed in', async () => {
    mockFetch({ 'GET /api/auth/me': [200, USER] })
    const w = await render()
    expect(w.find('[data-test="start"]').attributes('href')).toBe('/control')
    expect(w.find('[data-test="user-name"]').text()).toBe('Ivan Petrov')
    expect(w.find('[data-test="login-start"]').exists()).toBe(false)
  })

  it('signs out', async () => {
    mockFetch({ 'GET /api/auth/me': [200, USER], 'POST /api/auth/logout': [204, null] })
    const w = await render()
    await w.find('[data-test="logout"]').trigger('click')
    await flushPromises()
    expect(w.find('[data-test="start"]').exists()).toBe(false)
    expect(w.find('[data-test="login-start"]').exists()).toBe(true)
  })

  it('shows a Yandex sign-in error', async () => {
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const w = await render('?auth_error=1')
    expect(w.find('[data-test="auth-error"]').text()).toContain('Sign-in with Yandex failed')
  })

  it('is translated to Russian', async () => {
    setLocale('ru')
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const w = await render()
    expect(w.find('[data-test="login-start"]').text()).toContain('Войти через Яндекс')
  })
})
