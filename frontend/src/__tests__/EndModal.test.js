import { beforeEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import i18n, { setLocale } from '../i18n/index.js'
import EndModal from '../components/EndModal.vue'
import { useSim } from '../stores/sim.js'

describe('EndModal', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setLocale('en')
  })

  it('shows the full-game score, grade, badges, and risk statistics', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: { template: '<div />' } }, { path: '/control', component: { template: '<div />' } }],
    })
    await router.push('/')
    await router.isReady()
    const sim = useSim()
    sim.state = {
      config: { mode: 'full' },
      indexes: { cost: 98, schedule: 100, quality: 100, motivation: 97 },
      game: {
        score: 95, grade: 'gold', badges: ['cost', 'schedule', 'quality', 'motivation', 'risk'],
        completion: 100, decision_count: 32, auto_decisions: 2, risk_count: 12, risks_mitigated: 10, risks_occurred: 3,
      },
      decisions: [], learning_points: ['Manage risks before their triggers.'],
    }
    const wrapper = mount(EndModal, { global: { plugins: [i18n, router] } })
    expect(wrapper.text()).toContain('Project complete')
    expect(wrapper.find('[data-test="final-score"]').text()).toContain('95')
    expect(wrapper.text()).toContain('Gold')
    expect(wrapper.text()).toContain('Risk manager')
    expect(wrapper.text()).toContain('30/32')
    expect(wrapper.text()).toContain('10/12')
  })
})
