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

  it('asks anonymous visitors to sign in', async () => {
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const w = await render()
    expect(w.find('[data-test="start"]').exists()).toBe(false)
    expect(w.find('[data-test="login-start"]').text()).toContain('Sign in to start')
    expect(w.find('[data-test="login"]').exists()).toBe(true)
    expect(w.find('[data-test="login-options"]').exists()).toBe(false)
  })

  it('sign-in button offers every provider and returns to the control page', async () => {
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const auth = useAuth()
    auth.login = vi.fn()
    const w = await render()
    await w.find('[data-test="login-start"]').trigger('click')
    for (const p of ['yandex', 'vk', 'ok', 'mail', 'google']) {
      await w.find(`[data-test="login-${p}"]`).trigger('click')
      expect(auth.login).toHaveBeenLastCalledWith(p, '/control')
    }
    expect(w.find('[data-test="login-ok"]').text()).toContain('Odnoklassniki')
  })

  it('header sign-in returns to the landing page', async () => {
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const auth = useAuth()
    auth.login = vi.fn()
    const w = await render()
    await w.find('[data-test="login"]').trigger('click')
    await w.find('[data-test="login-vk"]').trigger('click')
    expect(auth.login).toHaveBeenCalledWith('vk', '/')
  })

  it('opens the sign-in options when the router guard sends a visitor here', async () => {
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const auth = useAuth()
    auth.login = vi.fn()
    const w = await render('?login=1&next=%2Fsim%2Fabc%2Fgantt')
    await w.find('[data-test="login-mail"]').trigger('click')
    expect(auth.login).toHaveBeenCalledWith('mail', '/sim/abc/gantt')
  })

  it('ignores an off-site next', async () => {
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const auth = useAuth()
    auth.login = vi.fn()
    const w = await render('?login=1&next=%2F%2Fevil.example')
    await w.find('[data-test="login-yandex"]').trigger('click')
    expect(auth.login).toHaveBeenCalledWith('yandex', '/control')
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

  it('shows a sign-in error', async () => {
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const w = await render('?auth_error=1')
    expect(w.find('[data-test="auth-error"]').text()).toContain('Sign-in failed')
  })

  it('is translated to Russian', async () => {
    setLocale('ru')
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const w = await render()
    expect(w.find('[data-test="login-start"]').text()).toContain('Войти и начать')
    await w.find('[data-test="login-start"]').trigger('click')
    expect(w.find('[data-test="login-ok"]').text()).toContain('Одноклассники')
  })
})
