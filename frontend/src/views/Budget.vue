<script setup>
import { computed, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSim } from '../stores/sim.js'
import { useFormat } from '../format.js'

const { t } = useI18n()
const { money, pct } = useFormat()
const sim = useSim()
const openTask = inject('openTask')

const s = computed(() => sim.state)
const people = (no) =>
  s.value.assignments
    .filter((x) => x.activity_no === no)
    .map((x) => sim.resource(x.resource_no).name + (x.percent < 100 ? ` ${x.percent}%` : ''))
    .join(', ')

const m = computed(() => s.value.money)
const totals = computed(() => [
  { label: t('budget.labour'), actual: m.value.labour_actual, eac: m.value.labour_eac, planned: m.value.labour_budget },
  { label: t('budget.pm'), actual: m.value.pm_actual, eac: m.value.pm_budget, planned: m.value.pm_budget },
  { label: t('budget.material'), actual: m.value.material_actual, eac: m.value.material_budget, planned: m.value.material_budget },
  { label: t('budget.other'), actual: m.value.other_actual, eac: m.value.other_eac, planned: m.value.other_budget },
])
const over = (eac, planned) => eac > planned * 1.005
</script>

<template>
  <div class="card mx-auto max-w-6xl overflow-x-auto">
    <table class="w-full min-w-[760px] text-sm">
      <thead>
        <tr class="border-b border-slate-200 text-left text-xs text-slate-500">
          <th class="px-4 py-3 font-medium">{{ t('budget.activity') }}</th>
          <th class="w-40 px-4 py-3 font-medium">{{ t('budget.progress') }}</th>
          <th class="px-4 py-3 text-right font-medium">{{ t('budget.actual') }}</th>
          <th class="px-4 py-3 text-right font-medium">{{ t('budget.eac') }}</th>
          <th class="px-4 py-3 text-right font-medium">{{ t('budget.planned') }}</th>
          <th class="px-4 py-3 font-medium">{{ t('budget.people') }}</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
        <tr v-for="a in s.activities" :key="a.no" class="cursor-pointer hover:bg-slate-50" @click="openTask(a.no)">
          <td class="px-4 py-2.5">
            <span class="mr-2 text-xs text-slate-400 tabular-nums">{{ a.no }}</span>
            <span :class="a.critical ? 'font-medium text-slate-900' : 'text-slate-700'">{{ a.name }}</span>
          </td>
          <td class="px-4 py-2.5">
            <div class="flex items-center gap-2">
              <div class="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-100">
                <div class="h-full rounded-full" :class="a.status === 'done' ? 'bg-emerald-500' : 'bg-accent'" :style="{ width: `${a.progress * 100}%` }" />
              </div>
              <span class="w-10 text-right text-xs text-slate-500 tabular-nums">{{ pct(a.progress * 100) }}</span>
            </div>
          </td>
          <td class="px-4 py-2.5 text-right tabular-nums">{{ money(a.actual_cost) }}</td>
          <td class="px-4 py-2.5 text-right tabular-nums" :class="over(a.eac, a.planned_cost) ? 'text-red-600' : ''">{{ money(a.eac) }}</td>
          <td class="px-4 py-2.5 text-right text-slate-500 tabular-nums">{{ money(a.planned_cost) }}</td>
          <td class="max-w-56 truncate px-4 py-2.5 text-slate-600" :class="{ 'text-amber-600 italic': !people(a.no) }">{{ people(a.no) || '—' }}</td>
        </tr>
      </tbody>
      <tbody class="border-t-2 border-slate-200">
        <tr v-for="row in totals" :key="row.label" class="text-slate-700">
          <td class="px-4 py-2.5" colspan="2">{{ row.label }}</td>
          <td class="px-4 py-2.5 text-right tabular-nums">{{ money(row.actual) }}</td>
          <td class="px-4 py-2.5 text-right tabular-nums" :class="over(row.eac, row.planned) ? 'text-red-600' : ''">{{ money(row.eac) }}</td>
          <td class="px-4 py-2.5 text-right text-slate-500 tabular-nums">{{ money(row.planned) }}</td>
          <td />
        </tr>
        <tr class="border-t border-slate-200 font-semibold text-slate-900">
          <td class="px-4 py-3" colspan="2">{{ t('budget.total') }}</td>
          <td class="px-4 py-3 text-right tabular-nums">{{ money(m.labour_actual + m.pm_actual + m.material_actual + m.other_actual) }}</td>
          <td class="px-4 py-3 text-right tabular-nums" :class="over(m.eac, m.bac) ? 'text-red-600' : ''">{{ money(m.eac) }}</td>
          <td class="px-4 py-3 text-right tabular-nums">{{ money(m.bac) }}</td>
          <td />
        </tr>
      </tbody>
    </table>
  </div>
</template>
