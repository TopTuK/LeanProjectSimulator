import { beforeEach, describe, expect, it } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import i18n, { setLocale } from '../i18n/index.js'
import Control from '../pages/Control.vue'
import { mockFetch } from './helpers.js'

describe('Control page', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setLocale('en')
  })

  it('shows mode-specific durations at the selected speed', async () => {
    mockFetch({ 'GET /api/scenarios': [200, [{ code: 'webshop', title: { en: 'Webshop' } }]] })
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div />' } },
        { path: '/control', component: Control },
        { path: '/simulations', component: { template: '<div />' } },
      ],
    })
    await router.push('/control')
    await router.isReady()
    const wrapper = mount(Control, { global: { plugins: [i18n, router] } })
    await flushPromises()
    expect(wrapper.find('[data-test="duration"]').text()).toContain('35 minutes')
    await wrapper.findAll('[data-test="mode"] button')[1].trigger('click')
    expect(wrapper.find('[data-test="duration"]').text()).toContain('315 minutes')
    const testSpeed = wrapper.findAll('button').find((b) => b.text() === 'Test · 2 min/day')
    await testSpeed.trigger('click')
    expect(wrapper.find('[data-test="duration"]').text()).toContain('90 minutes')
  })
})
