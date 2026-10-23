<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSim } from '../stores/sim.js'
import { useFormat } from '../format.js'
import LineChart from '../components/LineChart.vue'
import IndexCard from '../components/IndexCard.vue'
import EffectChips from '../components/EffectChips.vue'

const { t } = useI18n()
const { money, num, shortTime } = useFormat()
const sim = useSim()
const s = computed(() => sim.state)

const TILES = ['description', 'org', 'dashboard', 'cpi', 'spi', 'quality', 'motivation', 'hours', 'ev', 'decisions', 'learning', 'status']
const tile = ref(null)

watch(
  () => Math.floor(s.value.clock.minutes / 60),
  () => sim.loadSnapshots().catch(() => {}),
  { immediate: true },
)

const snaps = computed(() => sim.snapshots)
const line = (key, color, name) => ({ name, color, points: snaps.value.map((p) => [p.minute, p[key]]) })
const xMax = computed(() => s.value.clock.end_minutes)
const charts = computed(() => ({
  cpi: {
    series: [{ name: 'CPI', color: '#2563eb', points: snaps.value.map((p) => [p.minute, p.ac > 0 ? (100 * p.ev) / p.ac : 100]) }],
    reference: 100,
    format: (v) => `${Math.round(v)}%`,
  },
  spi: { series: [line('schedule', '#2563eb', 'SPI')], reference: 100, format: (v) => `${Math.round(v)}%` },
  quality: { series: [line('quality', '#10b981', t('dim.quality'))], reference: 100, format: (v) => `${Math.round(v)}%` },
  motivation: { series: [line('motivation', '#f59e0b', t('dim.motivation'))], reference: 100, format: (v) => `${Math.round(v)}%` },
  hours: { series: [line('hours', '#2563eb', t('reports.tiles.hours'))], yMin: 0, format: (v) => num(v) },
  ev: {
    series: [line('pv', '#94a3b8', t('reports.pv')), line('ev', '#2563eb', t('reports.ev')), line('ac', '#ef4444', t('reports.ac'))],
    yMin: 0,
    format: (v) => money(v),
  },
}))

const roles = computed(() => {
  const groups = {}
  for (const r of s.value.resources) (groups[r.role] ??= []).push(r)
  return groups
})
const resolved = computed(() => s.value.decisions.filter((d) => d.status === 'resolved'))

const notesKey = computed(() => `simultrain:notes:${s.value.id}`)
const notes = ref('')
try {
  notes.value = localStorage.getItem(notesKey.value) ?? ''
} catch {}
watch(notes, (v) => {
  try {
    localStorage.setItem(notesKey.value, v)
  } catch {}
})
</script>

<template>
  <div class="mx-auto max-w-6xl">
    <div v-if="!tile" class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
      <button v-for="(k, i) in TILES" :key="k" class="card p-5 text-left transition hover:border-accent hover:shadow-sm" @click="tile = k">
        <span class="text-xs text-slate-400 tabular-nums">{{ String(i + 1).padStart(2, '0') }}</span>
        <span class="mt-2 block text-sm font-medium text-slate-800">{{ t(`reports.tiles.${k}`) }}</span>
      </button>
    </div>

    <div v-else class="space-y-4">
      <button class="text-sm text-slate-500 hover:text-slate-800" @click="tile = null">← {{ t('reports.back') }}</button>
      <div class="card p-6">
        <h2 class="mb-4 text-lg font-semibold text-slate-900">{{ t(`reports.tiles.${tile}`) }}</h2>

        <template v-if="tile === 'description'">
          <h3 class="font-medium text-slate-800">{{ s.scenario.title }}</h3>
          <p class="mt-2 max-w-3xl text-sm leading-relaxed text-slate-600">{{ s.scenario.description }}</p>
          <dl class="mt-6 grid max-w-xl grid-cols-2 gap-3 text-sm">
            <dt class="text-slate-500">{{ t('budget.total') }}</dt><dd class="font-medium">{{ money(s.money.bac) }}</dd>
            <dt class="text-slate-500">{{ t('task.duration') }}</dt><dd class="font-medium">{{ t('weekN', { n: s.scenario.weeks }) }}</dd>
          </dl>
        </template>

        <template v-else-if="tile === 'org'">
          <div class="mb-6 flex flex-wrap gap-3">
            <div class="rounded-lg border border-slate-200 px-4 py-3 text-sm"><p class="label">{{ t('reports.sponsor') }}</p><p class="mt-1 font-medium">{{ s.messages.at(-1)?.sender }}</p></div>
            <div class="rounded-lg border border-accent bg-accent-soft px-4 py-3 text-sm"><p class="label">{{ t('reports.pmYou') }}</p></div>
          </div>
          <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <div v-for="(people, role) in roles" :key="role" class="rounded-lg border border-slate-200 px-4 py-3">
              <p class="text-xs text-slate-500">{{ role }}</p>
              <p class="mt-1 text-sm font-medium text-slate-800">{{ people.map((p) => p.name).join(', ') }}</p>
            </div>
          </div>
        </template>

        <template v-else-if="tile === 'dashboard'">
          <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <IndexCard v-for="k in ['cost', 'schedule', 'quality', 'motivation']" :key="k" :label="t(`dim.${k}`)" :value="s.indexes[k]" />
          </div>
          <dl class="mt-6 grid max-w-xl grid-cols-2 gap-3 text-sm">
            <dt class="text-slate-500">{{ t('reports.pv') }}</dt><dd class="font-medium tabular-nums">{{ money(s.money.pv) }}</dd>
            <dt class="text-slate-500">{{ t('reports.ev') }}</dt><dd class="font-medium tabular-nums">{{ money(s.money.ev) }}</dd>
            <dt class="text-slate-500">{{ t('reports.ac') }}</dt><dd class="font-medium tabular-nums">{{ money(s.money.labour_actual) }}</dd>
            <dt class="text-slate-500">CPI / SPI</dt><dd class="font-medium tabular-nums">{{ num(s.money.cpi, 2) }} / {{ num(s.money.spi, 2) }}</dd>
            <dt class="text-slate-500">{{ t('office.forecast') }}</dt><dd class="font-medium tabular-nums">{{ money(s.money.eac) }}</dd>
          </dl>
        </template>

        <template v-else-if="charts[tile]">
          <p v-if="snaps.length < 2" class="text-sm text-slate-400">{{ t('reports.noData') }}</p>
          <LineChart v-else v-bind="charts[tile]" :x-max="xMax" />
        </template>

        <template v-else-if="tile === 'decisions'">
          <p v-if="!resolved.length" class="text-sm text-slate-400">{{ t('reports.noDecisions') }}</p>
          <ul class="divide-y divide-slate-100">
            <li v-for="d in resolved" :key="d.id" class="py-4">
              <div class="flex flex-wrap items-baseline justify-between gap-2">
                <span class="font-medium text-slate-900">{{ d.subject }}</span>
                <span class="text-xs text-slate-400">{{ shortTime(d.deadline) }} · {{ d.resolved_by === 'auto' ? t('decision.auto') : t('decision.team') }}</span>
              </div>
              <p class="mt-1 text-sm text-slate-700">→ {{ d.option_label }}</p>
              <p class="mt-1 text-sm text-slate-500">{{ d.feedback }}</p>
              <EffectChips :effects="d.effects" class="mt-2" />
            </li>
          </ul>
        </template>

        <template v-else-if="tile === 'learning'">
          <p v-if="!s.learning_points.length" class="text-sm text-slate-400">{{ t('reports.noLearning') }}</p>
          <ol class="list-decimal space-y-2 pl-5 text-sm text-slate-700">
            <li v-for="(p, i) in s.learning_points" :key="i">{{ p }}</li>
          </ol>
        </template>

        <template v-else-if="tile === 'status'">
          <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <IndexCard v-for="k in ['cost', 'schedule', 'quality', 'motivation']" :key="k" :label="t(`dim.${k}`)" :value="s.indexes[k]" />
          </div>
          <label class="label mt-6 block">{{ t('reports.statusNotes') }}</label>
          <textarea v-model="notes" rows="6" class="mt-2 w-full rounded-lg border border-slate-200 p-3 text-sm focus:border-accent focus:outline-none" :placeholder="t('reports.statusPlaceholder')" />
          <p class="mt-1 text-xs text-slate-400">{{ t('reports.statusSaved') }}</p>
        </template>
      </div>
    </div>
  </div>
</template>
