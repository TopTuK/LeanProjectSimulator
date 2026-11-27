import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import i18n, { setLocale } from '../i18n/index.js'
import Login from '../pages/Login.vue'
import { useAuth } from '../stores/auth.js'
import { mockFetch, USER } from './helpers.js'

async function render(query = '', me = [401, { detail: 'login required' }]) {
  mockFetch({ 'GET /api/auth/me': me })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/login', component: Login },
      { path: '/simulations', component: { template: '<div />' } },
      { path: '/sim/:id/:view', component: { template: '<div />' } },
    ],
  })
  await router.push(`/login${query}`)
  const wrapper = mount(Login, { global: { plugins: [router, i18n] } })
  await flushPromises()
  return { wrapper, router }
}

describe('Login page', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setLocale('en')
  })

  it('offers every provider on a standalone page and returns to the dashboard', async () => {
    const auth = useAuth()
    auth.login = vi.fn()
    const { wrapper } = await render()
    expect(wrapper.find('[role="dialog"]').exists()).toBe(false)
    for (const provider of ['yandex', 'vk', 'ok', 'mail', 'google']) {
      await wrapper.find(`[data-test="login-${provider}"]`).trigger('click')
      expect(auth.login).toHaveBeenLastCalledWith(provider, '/simulations')
    }
  })

  it('preserves a safe simulation return path', async () => {
    const auth = useAuth()
    auth.login = vi.fn()
    const { wrapper } = await render('?next=%2Fsim%2Fabc%2Fgantt')
    await wrapper.find('[data-test="login-vk"]').trigger('click')
    expect(auth.login).toHaveBeenCalledWith('vk', '/sim/abc/gantt')
  })

  it('rejects an off-site return path', async () => {
    const auth = useAuth()
    auth.login = vi.fn()
    const { wrapper } = await render('?next=%2F%2Fevil.example')
    await wrapper.find('[data-test="login-yandex"]').trigger('click')
    expect(auth.login).toHaveBeenCalledWith('yandex', '/simulations')
  })

  it('shows OAuth errors and Russian provider labels', async () => {
    setLocale('ru')
    const { wrapper } = await render('?auth_error=1')
    expect(wrapper.find('[data-test="auth-error"]').text()).toContain('Не удалось войти')
    expect(wrapper.find('[data-test="login-ok"]').text()).toContain('Одноклассники')
  })

  it('redirects an authenticated visitor to the requested destination', async () => {
    const { router } = await render('?next=%2Fsim%2Fabc%2Fgantt', [200, USER])
    expect(router.currentRoute.value.path).toBe('/sim/abc/gantt')
  })
})
