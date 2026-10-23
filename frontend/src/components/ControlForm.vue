<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Segmented from './Segmented.vue'
import { setLocale } from '../i18n/index.js'

const props = defineProps({
  scenarios: { type: Array, default: () => [] },
  readonly: Boolean,
})
const cfg = defineModel({ type: Object, required: true })
const { t, locale } = useI18n()

const yesNo = computed(() => [
  { value: true, label: t('yes') },
  { value: false, label: t('no') },
])
const levels = computed(() => ['easy', 'standard', 'hard'].map((v) => ({ value: v, label: t(`level.${v}`) })))
const speeds = computed(() => ['test', 'fast', 'demo'].map((v) => ({ value: v, label: t(`speed.${v}`) })))
const scenarioOptions = computed(() =>
  props.scenarios.map((s) => ({ value: s.code, label: s.title[locale.value] ?? s.title.en })),
)
const lang = computed({
  get: () => cfg.value.locale,
  set: (v) => {
    cfg.value.locale = v
    setLocale(v)
  },
})
</script>

<template>
  <div class="divide-y divide-slate-100">
    <div class="grid gap-2 py-4 sm:grid-cols-[12rem_1fr] sm:items-center">
      <span class="text-sm text-slate-600">{{ t('control.language') }}</span>
      <Segmented v-model="lang" :disabled="readonly" :options="[{ value: 'en', label: 'English' }, { value: 'ru', label: 'Русский' }]" />
    </div>
    <div class="grid gap-2 py-4 sm:grid-cols-[12rem_1fr] sm:items-center">
      <span class="text-sm text-slate-600">{{ t('control.scenario') }}</span>
      <Segmented v-model="cfg.scenario" :disabled="readonly" :options="scenarioOptions" />
    </div>
    <div class="grid gap-2 py-4 sm:grid-cols-[12rem_1fr] sm:items-center">
      <span class="text-sm text-slate-600">{{ t('control.speed') }}</span>
      <Segmented v-model="cfg.speed" :disabled="readonly" :options="speeds" />
    </div>
    <div class="grid gap-2 py-4 sm:grid-cols-[12rem_1fr] sm:items-center">
      <span class="text-sm text-slate-600">{{ t('control.planned') }}</span>
      <Segmented v-model="cfg.already_planned" :disabled="readonly" :options="yesNo" />
    </div>
    <div class="grid gap-2 py-4 sm:grid-cols-[12rem_1fr] sm:items-center">
      <span class="text-sm text-slate-600">{{ t('control.risk') }}</span>
      <div class="flex items-center gap-3">
        <Segmented v-model="cfg.risk" disabled :options="yesNo" />
        <span class="text-xs text-slate-400">{{ t('control.notInDemo') }}</span>
      </div>
    </div>
    <div class="grid gap-2 py-4 sm:grid-cols-[12rem_1fr] sm:items-center">
      <span class="text-sm text-slate-600">{{ t('control.raci') }}</span>
      <div class="flex items-center gap-3">
        <Segmented v-model="cfg.raci" disabled :options="yesNo" />
        <span class="text-xs text-slate-400">{{ t('control.notInDemo') }}</span>
      </div>
    </div>
    <div v-for="d in ['cost', 'schedule', 'quality', 'motivation', 'risk']" :key="d" class="grid gap-2 py-4 sm:grid-cols-[12rem_1fr] sm:items-center">
      <span class="text-sm text-slate-600">{{ t('control.difficulty') }} · {{ t(`dim.${d}`) }}</span>
      <Segmented v-model="cfg[`difficulty_${d}`]" :disabled="readonly || d === 'risk'" :options="levels" />
    </div>
  </div>
</template>
