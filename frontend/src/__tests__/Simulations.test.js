import { beforeEach, describe, expect, it } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import i18n, { setLocale } from '../i18n/index.js'
import Simulations from '../pages/Simulations.vue'
import { mockFetch } from './helpers.js'

const SESSION = {
  id: 's1-running',
  status: 'running',
  locale: 'en',
  created_at: '2026-11-27T12:00:00+00:00',
  config: { mode: 'full', speed: 'fast', risk: true },
  clock: { week: 2, weekday: 1, hour: 10, minute: 30 },
  completion: 25,
  scenario: { code: 'webshop', title: 'Webshop Launch' },
}

async function render(sessions = [SESSION], extraRoutes = {}) {
  const fetch = mockFetch({ 'GET /api/sessions': [200, sessions], ...extraRoutes })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/login', component: { template: '<div />' } },
      { path: '/simulations', component: Simulations },
      { path: '/control', component: { template: '<div />' } },
      { path: '/sim/:id/:view', component: { template: '<div />' } },
    ],
  })
  await router.push('/simulations')
  const wrapper = mount(Simulations, { global: { plugins: [router, i18n] } })
  await flushPromises()
  return { wrapper, fetch }
}

describe('Simulations dashboard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setLocale('en')
  })

  it('shows an empty state with a creation action', async () => {
    const { wrapper } = await render([])
    expect(wrapper.find('[data-test="sessions-empty"]').text()).toContain('No simulations yet')
    expect(wrapper.find('[data-test="new-simulation"]').attributes('href')).toBe('/control')
  })

  it('shows independent settings, progress, status, and open links', async () => {
    const ended = {
      ...SESSION,
      id: 's2-ended', status: 'ended', completion: 100,
      config: { mode: 'demo', speed: 'test', risk: false },
    }
    const { wrapper } = await render([SESSION, ended])
    expect(wrapper.find('[data-test="session-s1-running"]').text()).toContain('Full · 45 days')
    expect(wrapper.find('[data-test="session-s1-running"]').text()).toContain('25%')
    expect(wrapper.find('[data-test="status-s1-running"]').text()).toBe('Running')
    expect(wrapper.find('[data-test="session-s2-ended"]').text()).toContain('Demo · 1 week')
    expect(wrapper.find('[data-test="open-s1-running"]').attributes('href')).toBe('/sim/s1-running/office')
  })

  it('cancels deletion without calling the API', async () => {
    const { wrapper, fetch } = await render()
    await wrapper.find('[data-test="delete-s1-running"]').trigger('click')
    expect(wrapper.find('[data-test="delete-confirmation"]').text()).toContain('permanently removed')
    expect(wrapper.text()).toContain('currently running')
    await wrapper.find('[data-test="delete-cancel"]').trigger('click')
    expect(wrapper.find('[data-test="delete-confirm"]').exists()).toBe(false)
    expect(fetch).not.toHaveBeenCalledWith('/api/sessions/s1-running', expect.anything())
    expect(wrapper.find('[data-test="session-s1-running"]').exists()).toBe(true)
  })

  it('deletes a running simulation after confirmation', async () => {
    const { wrapper, fetch } = await render([SESSION], { 'DELETE /api/sessions/s1-running': [204, null] })
    await wrapper.find('[data-test="delete-s1-running"]').trigger('click')
    await wrapper.find('[data-test="delete-confirm"]').trigger('click')
    await flushPromises()
    expect(fetch).toHaveBeenCalledWith('/api/sessions/s1-running', expect.objectContaining({ method: 'DELETE' }))
    expect(wrapper.find('[data-test="session-s1-running"]').exists()).toBe(false)
    expect(wrapper.find('[data-test="sessions-empty"]').exists()).toBe(true)
  })

  it('keeps the simulation and shows an error when deletion fails', async () => {
    const { wrapper } = await render([SESSION], { 'DELETE /api/sessions/s1-running': [500, { detail: 'database unavailable' }] })
    await wrapper.find('[data-test="delete-s1-running"]').trigger('click')
    await wrapper.find('[data-test="delete-confirm"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-test="session-s1-running"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="sessions-error"]').text()).toContain('database unavailable')
  })
})
