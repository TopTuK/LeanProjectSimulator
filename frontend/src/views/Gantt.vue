<script setup>
import { computed, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSim } from '../stores/sim.js'

const { t } = useI18n()
const sim = useSim()
const openTask = inject('openTask')

const s = computed(() => sim.state)
const days = computed(() => s.value.scenario.total_days)
const weeks = computed(() => Array.from({ length: s.value.scenario.weeks }, (_, i) => i + 1))
const x = (d) => `${(100 * d) / days.value}%`
const today = computed(() => x(s.value.clock.work_days))
const people = (no) =>
  s.value.assignments
    .filter((a) => a.activity_no === no)
    .map((a) => sim.resource(a.resource_no).name)
    .join(', ')
</script>

<template>
  <div class="mx-auto max-w-7xl space-y-4">
    <div class="card overflow-x-auto">
      <div class="min-w-[900px]">
        <div class="grid grid-cols-[16rem_1fr] border-b border-slate-200 text-xs text-slate-500">
          <div class="px-4 py-2" />
          <div class="grid" :style="{ gridTemplateColumns: `repeat(${weeks.length}, 1fr)` }">
            <div v-for="w in weeks" :key="w" class="border-l border-slate-100 py-2 text-center" :class="{ 'font-semibold text-accent': w === s.clock.week }">
              {{ t('week') }} {{ w }}
            </div>
          </div>
        </div>

        <div class="relative">
          <div v-for="a in s.activities" :key="a.no" class="grid cursor-pointer grid-cols-[16rem_1fr] hover:bg-slate-50" @click="openTask(a.no)">
            <div class="truncate px-4 py-2 text-sm">
              <span class="mr-2 text-xs text-slate-400 tabular-nums">{{ a.no }}</span>
              <span :class="a.critical ? 'font-medium text-slate-900' : 'text-slate-700'">{{ a.name }}</span>
            </div>
            <div class="relative h-9">
              <div class="absolute inset-0 grid" :style="{ gridTemplateColumns: `repeat(${weeks.length}, 1fr)` }">
                <div v-for="w in weeks" :key="w" class="border-l border-slate-100" />
              </div>
              <template v-if="a.milestone">
                <div class="absolute top-1/2 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 rotate-45" :class="a.status === 'done' ? 'bg-emerald-500' : 'bg-slate-900'" :style="{ left: x(a.es + a.duration / 2) }" :title="a.name" />
              </template>
              <template v-else>
                <div
                  v-if="a.slack > 0"
                  class="absolute top-1/2 h-0.5 -translate-y-1/2 border-t border-dashed border-slate-300"
                  :style="{ left: x(a.ef), width: x(a.slack) }"
                />
                <div
                  class="absolute top-2 bottom-2 overflow-hidden rounded"
                  :class="a.critical ? 'bg-red-100 ring-1 ring-red-300' : 'bg-slate-100 ring-1 ring-slate-300'"
                  :style="{ left: x(a.es), width: x(a.duration) }"
                  :title="people(a.no)"
                >
                  <div class="h-full" :class="a.status === 'done' ? 'bg-emerald-500' : a.critical ? 'bg-red-400' : 'bg-accent'" :style="{ width: `${a.progress * 100}%` }" />
                </div>
                <span class="pointer-events-none absolute top-1/2 -translate-y-1/2 pl-2 text-[11px] whitespace-nowrap text-slate-500" :style="{ left: x(a.ef) }">
                  {{ people(a.no) }}
                </span>
              </template>
            </div>
          </div>
          <div class="pointer-events-none absolute top-0 bottom-0 left-64 right-0">
            <div class="absolute top-0 bottom-0 w-px bg-accent" :style="{ left: today }">
              <span class="absolute -top-0 left-1 rounded bg-accent px-1 text-[10px] text-white">{{ t('gantt.today') }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="flex flex-wrap gap-5 text-xs text-slate-600">
      <span class="flex items-center gap-2"><span class="h-3 w-6 rounded bg-slate-100 ring-1 ring-slate-300" />{{ t('gantt.legendActivity') }}</span>
      <span class="flex items-center gap-2"><span class="h-3 w-6 rounded bg-red-100 ring-1 ring-red-300" />{{ t('gantt.legendCritical') }}</span>
      <span class="flex items-center gap-2"><span class="h-3 w-6 rounded bg-accent" />{{ t('gantt.legendProgress') }}</span>
      <span class="flex items-center gap-2"><span class="h-3 w-3 rotate-45 bg-slate-900" />{{ t('gantt.legendMilestone') }}</span>
      <span class="flex items-center gap-2"><span class="w-6 border-t border-dashed border-slate-400" />{{ t('gantt.legendSlack') }}</span>
    </div>
  </div>
</template>
