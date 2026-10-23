<script setup>
import { computed, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSim } from '../stores/sim.js'
import { useFormat } from '../format.js'
import IndexCard from '../components/IndexCard.vue'
import ClockButton from '../components/ClockButton.vue'
import Icon from '../components/Icon.vue'
import QuickStart from '../components/QuickStart.vue'

const { t } = useI18n()
const { money, pct, shortTime, clockLabel } = useFormat()
const sim = useSim()
const openMail = inject('openMail')
const openDecision = inject('openDecision')

const s = computed(() => sim.state)
const today = computed(() =>
  s.value.calendar
    .filter((c) => c.week === s.value.clock.week && c.weekday === s.value.clock.weekday)
    .sort((a, b) => a.hour - b.hour),
)
const progress = computed(() => {
  const acts = s.value.activities
  const total = acts.reduce((sum, a) => sum + a.planned_cost, 0)
  return total ? (100 * acts.reduce((sum, a) => sum + a.planned_cost * a.progress, 0)) / total : 0
})
const elapsed = computed(() => (100 * s.value.clock.minutes) / s.value.clock.end_minutes)
</script>

<template>
  <div class="mx-auto max-w-6xl space-y-6">
    <div class="flex flex-wrap items-center gap-4 rounded-xl border border-blue-100 bg-accent-soft px-5 py-4">
      <div class="min-w-0 flex-1">
        <p class="text-lg font-semibold text-slate-900 tabular-nums">{{ clockLabel(s.clock) }}</p>
        <p class="text-sm text-slate-600">{{ t('office.demoBanner') }}</p>
        <div class="mt-2 h-1 max-w-md overflow-hidden rounded-full bg-white">
          <div class="h-full bg-accent transition-all" :style="{ width: `${elapsed}%` }" />
        </div>
      </div>
      <ClockButton />
    </div>

    <QuickStart :help-to="`/sim/${s.id}/help`" />

    <section>
      <h2 class="label mb-3">{{ t('office.indexes') }}</h2>
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <IndexCard v-for="k in ['cost', 'schedule', 'quality', 'motivation']" :key="k" :label="t(`dim.${k}`)" :value="s.indexes[k]" />
      </div>
    </section>

    <div class="grid gap-6 lg:grid-cols-3">
      <section class="card lg:col-span-2">
        <div class="flex items-center justify-between border-b border-slate-100 px-5 py-3">
          <h2 class="font-medium text-slate-900">{{ t('office.inbox') }}</h2>
          <button class="text-sm text-accent hover:underline" @click="openMail()">{{ t('mail.title') }} →</button>
        </div>
        <ul class="divide-y divide-slate-100">
          <li v-if="!s.messages.length" class="px-5 py-6 text-sm text-slate-400">{{ t('office.empty') }}</li>
          <li v-for="m in s.messages.slice(0, 6)" :key="m.id">
            <button class="flex w-full items-center gap-3 px-5 py-3 text-left hover:bg-slate-50" @click="openMail(m.id)">
              <Icon :name="m.channel" class="h-4 w-4 shrink-0" :class="m.read ? 'text-slate-300' : 'text-accent'" />
              <span class="min-w-0 flex-1 truncate text-sm" :class="m.read ? 'text-slate-600' : 'font-semibold text-slate-900'">{{ m.subject }}</span>
              <span class="hidden truncate text-xs text-slate-500 sm:inline">{{ m.sender }}</span>
              <span class="shrink-0 text-xs text-slate-400 tabular-nums">{{ shortTime(m.time) }}</span>
            </button>
          </li>
        </ul>
      </section>

      <div class="space-y-6">
        <section v-if="sim.openDecisions.length" class="card border-amber-200">
          <h2 class="border-b border-slate-100 px-5 py-3 font-medium text-slate-900">{{ t('office.decisions') }}</h2>
          <ul class="divide-y divide-slate-100">
            <li v-for="d in sim.openDecisions" :key="d.id" class="flex items-center gap-3 px-5 py-3">
              <span class="min-w-0 flex-1">
                <span class="block truncate text-sm font-medium text-slate-800">{{ d.subject }}</span>
                <span class="text-xs text-slate-500">{{ t('decision.deadline', { time: shortTime(d.deadline) }) }}</span>
              </span>
              <button class="btn btn-primary px-3 py-1.5" @click="openDecision(d.id)">{{ t('office.decide') }}</button>
            </li>
          </ul>
        </section>

        <section class="card">
          <h2 class="border-b border-slate-100 px-5 py-3 font-medium text-slate-900">{{ t('office.agenda') }}</h2>
          <ul class="divide-y divide-slate-100">
            <li v-if="!today.length" class="px-5 py-4 text-sm text-slate-400">{{ t('office.noAgenda') }}</li>
            <li v-for="c in today" :key="c.key" class="flex gap-3 px-5 py-3 text-sm">
              <span class="w-12 shrink-0 text-slate-400 tabular-nums">{{ c.hour }}:00</span>
              <span class="text-slate-700">{{ c.title }}</span>
            </li>
          </ul>
        </section>

        <section class="card space-y-3 p-5 text-sm">
          <h2 class="font-medium text-slate-900">{{ t('office.progress') }}</h2>
          <div class="flex justify-between"><span class="text-slate-500">{{ t('budget.progress') }}</span><span class="font-medium tabular-nums">{{ pct(progress) }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">{{ t('office.spent') }}</span><span class="font-medium tabular-nums">{{ money(s.money.ac + s.money.pm_actual) }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">{{ t('budget.planned') }}</span><span class="font-medium tabular-nums">{{ money(s.money.bac) }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">{{ t('office.forecast') }}</span><span class="font-medium tabular-nums">{{ money(s.money.eac) }}</span></div>
        </section>
      </div>
    </div>
  </div>
</template>
