<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSim } from '../stores/sim.js'

const { t } = useI18n()
const sim = useSim()
const s = computed(() => sim.state)

const week = ref(s.value.clock.week)
const HOURS = Array.from({ length: 11 }, (_, i) => 8 + i)
const ROW = 44
const items = computed(() => s.value.calendar.filter((c) => c.week === week.value))
const now = computed(() => {
  const c = s.value.clock
  if (c.week !== week.value) return null
  return { weekday: c.weekday, top: (c.hour - 8 + c.minute / 60) * ROW }
})
</script>

<template>
  <div class="mx-auto max-w-6xl space-y-4">
    <div class="flex flex-wrap items-center gap-1">
      <button
        v-for="w in s.scenario.weeks"
        :key="w"
        class="h-8 min-w-8 rounded-md px-2 text-sm tabular-nums"
        :class="w === week ? 'bg-slate-900 text-white' : w === s.clock.week ? 'text-accent hover:bg-slate-100' : 'text-slate-500 hover:bg-slate-100'"
        @click="week = w"
      >
        {{ w }}
      </button>
      <span class="ml-3 text-sm text-slate-500">{{ t('calendar.hint') }}</span>
    </div>

    <div class="card overflow-x-auto">
      <div class="grid min-w-[720px] grid-cols-[3.5rem_repeat(5,1fr)]">
        <div class="border-b border-slate-200" />
        <div v-for="d in 5" :key="d" class="border-b border-l border-slate-200 px-3 py-2 text-sm font-medium" :class="now && now.weekday === d - 1 ? 'text-accent' : 'text-slate-700'">
          {{ t(`weekdays.${d - 1}`) }}
        </div>

        <div>
          <div v-for="h in HOURS" :key="h" class="pr-2 text-right text-xs text-slate-400 tabular-nums" :style="{ height: `${ROW}px` }">{{ h }}:00</div>
        </div>
        <div v-for="d in 5" :key="d" class="relative border-l border-slate-200" :style="{ height: `${ROW * HOURS.length}px` }">
          <div v-for="h in HOURS" :key="h" class="border-b border-slate-100" :style="{ height: `${ROW}px` }" />
          <div
            v-for="c in items.filter((i) => i.weekday === d - 1)"
            :key="c.key"
            class="absolute right-1 left-1 overflow-hidden rounded-md border-l-2 border-accent bg-accent-soft px-2 py-1 text-xs"
            :style="{ top: `${(c.hour - 8) * ROW + 1}px`, height: `${Math.max(c.duration, 0.5) * ROW - 2}px` }"
            :title="c.body"
          >
            <span class="font-medium text-slate-800">{{ c.hour }}:00</span>
            <span class="ml-1 text-slate-700">{{ c.title }}</span>
          </div>
          <div v-if="now && now.weekday === d - 1" class="absolute right-0 left-0 h-px bg-red-500" :style="{ top: `${now.top}px` }" />
        </div>
      </div>
    </div>
  </div>
</template>
