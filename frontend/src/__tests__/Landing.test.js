import { beforeEach, describe, expect, it } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import i18n, { setLocale } from '../i18n/index.js'
import Landing from '../pages/Landing.vue'
import { mockFetch, USER } from './helpers.js'

async function render() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: Landing },
      { path: '/login', component: { template: '<div />' } },
      { path: '/simulations', component: { template: '<div />' } },
    ],
  })
  await router.push('/')
  const wrapper = mount(Landing, { global: { plugins: [router, i18n] } })
  await flushPromises()
  return wrapper
}

describe('Landing', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setLocale('en')
  })

  it('links anonymous visitors to the separate sign-in page', async () => {
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const w = await render()
    expect(w.find('[data-test="start"]').exists()).toBe(false)
    expect(w.find('[data-test="login-start"]').text()).toContain('Sign in to start')
    expect(w.find('[data-test="login-start"]').attributes('href')).toBe('/login?next=/simulations')
    expect(w.find('[data-test="login"]').attributes('href')).toBe('/login?next=/')
    expect(w.find('[data-test="login-options"]').exists()).toBe(false)
  })

  it('offers the dashboard and user name when signed in', async () => {
    mockFetch({ 'GET /api/auth/me': [200, USER] })
    const w = await render()
    expect(w.find('[data-test="start"]').attributes('href')).toBe('/simulations')
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

  it('is translated to Russian', async () => {
    setLocale('ru')
    mockFetch({ 'GET /api/auth/me': [401, { detail: 'login required' }] })
    const w = await render()
    expect(w.find('[data-test="login-start"]').text()).toContain('Войти и начать')
  })
})
