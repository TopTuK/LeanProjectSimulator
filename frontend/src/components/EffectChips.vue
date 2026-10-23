<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useFormat } from '../format.js'

const props = defineProps({ effects: Object })
const { t } = useI18n()
const { money, num } = useFormat()

const chips = computed(() => {
  const e = props.effects || {}
  const out = []
  if (e.cost) out.push({ text: `${t('dim.cost')} ${e.cost > 0 ? '+' : ''}${money(e.cost)}`, good: e.cost < 0 })
  const effort = Object.values(e.effort || {}).reduce((a, b) => a + b, 0)
  if (effort) out.push({ text: `${t('dim.schedule')} ${effort > 0 ? '+' : ''}${t('task.hours', { n: num(effort) })}`, good: effort < 0 })
  for (const k of ['quality', 'motivation']) {
    if (e[k]) out.push({ text: `${t(`dim.${k}`)} ${e[k] > 0 ? '+' : ''}${e[k]}`, good: e[k] > 0 })
  }
  return out
})
</script>

<template>
  <div v-if="chips.length" class="flex flex-wrap gap-1.5">
    <span
      v-for="c in chips"
      :key="c.text"
      class="rounded-full px-2 py-0.5 text-xs font-medium"
      :class="c.good ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'"
    >{{ c.text }}</span>
  </div>
</template>
