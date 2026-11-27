import { beforeEach, describe, expect, it } from 'vitest'
import { reactive } from 'vue'
import { mount } from '@vue/test-utils'
import i18n, { setLocale } from '../i18n/index.js'
import ControlForm from '../components/ControlForm.vue'

function render() {
  const cfg = reactive({
    locale: 'en', scenario: 'webshop', mode: 'demo', speed: 'demo', already_planned: true,
    risk: false, raci: false, difficulty_risk: 'standard',
  })
  const wrapper = mount(ControlForm, {
    props: { modelValue: cfg, scenarios: [{ code: 'webshop', title: { en: 'Webshop', ru: 'Магазин' } }] },
    global: { plugins: [i18n] },
  })
  return { cfg, wrapper }
}

describe('ControlForm', () => {
  beforeEach(() => setLocale('en'))

  it('enables managed risks for a full game and disables them again for demo', async () => {
    const { cfg, wrapper } = render()
    expect(wrapper.find('[data-test="risk"] button').attributes('disabled')).toBeDefined()
    const modes = wrapper.findAll('[data-test="mode"] button')
    expect(modes).toHaveLength(2)
    await modes[1].trigger('click')
    expect(cfg.mode).toBe('full')
    expect(cfg.risk).toBe(true)
    expect(wrapper.find('[data-test="risk"] button').attributes('disabled')).toBeUndefined()
    expect(wrapper.text()).toContain('Normal · 7 min/day')
    await modes[0].trigger('click')
    expect(cfg.mode).toBe('demo')
    expect(cfg.risk).toBe(false)
    expect(wrapper.find('[data-test="risk"] button').attributes('disabled')).toBeDefined()
  })
})
