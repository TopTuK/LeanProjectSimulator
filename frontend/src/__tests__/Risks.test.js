import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import i18n, { setLocale } from '../i18n/index.js'
import Risks from '../views/Risks.vue'
import { useSim } from '../stores/sim.js'

const RISK = {
  key: 'vendor', name: 'Hosting supplier delay', description: 'Capacity may arrive late.', category: 'Supplier',
  decision_id: 42, status: 'open', response_key: null, response_label: null, response_effects: null,
  deadline: { week: 2, weekday: 0, hour: 17, minute: 0 }, probability: 45, outcome: null,
}

describe('Risks', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setLocale('en')
  })

  it('shows identified risks and opens their response decision', async () => {
    const openDecision = vi.fn()
    const sim = useSim()
    sim.state = { risks: [RISK] }
    const wrapper = mount(Risks, { global: { plugins: [i18n], provide: { openDecision } } })
    expect(wrapper.find('[data-test="risk-vendor"]').text()).toContain('Response needed')
    expect(wrapper.find('[data-test="risk-vendor"]').text()).toContain('45%')
    await wrapper.find('[data-test="open-response"]').trigger('click')
    expect(openDecision).toHaveBeenCalledWith(42)
  })

  it('shows an avoided outcome', () => {
    const sim = useSim()
    sim.state = { risks: [{ ...RISK, status: 'avoided', outcome: { occurred: false } }] }
    const wrapper = mount(Risks, { global: { plugins: [i18n], provide: { openDecision: vi.fn() } } })
    expect(wrapper.text()).toContain('Avoided')
    expect(wrapper.text()).toContain('did not occur')
  })
})
