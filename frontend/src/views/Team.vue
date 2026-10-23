<script setup>
import { computed, inject, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSim } from '../stores/sim.js'
import { TEAM_GUIDE } from '../i18n/guide.js'
import Modal from '../components/Modal.vue'

const { t, locale } = useI18n()
const sim = useSim()
const openTask = inject('openTask')
const s = computed(() => sim.state)
const weeks = computed(() => Array.from({ length: s.value.scenario.weeks }, (_, i) => i + 1))
const guide = computed(() => TEAM_GUIDE[locale.value] ?? TEAM_GUIDE.en)

const STATE_BG = {
  payroll: 'bg-white',
  available: 'bg-emerald-50',
  training: 'bg-amber-100',
  sick: 'bg-red-100',
  holiday: 'bg-sky-100',
  other: 'bg-slate-200',
}
const UNAVAILABLE = new Set(['training', 'sick', 'holiday', 'other'])
const isConflict = (cell) => cell.activities.length > 0 && (cell.load > 100 || UNAVAILABLE.has(cell.state))

const problems = computed(() => {
  const out = []
  for (const r of s.value.resources) {
    for (const cell of r.weeks) {
      if (cell.week < s.value.clock.week || !isConflict(cell)) continue
      const text = UNAVAILABLE.has(cell.state)
        ? t('team.unavailable', { name: r.name, state: t(`team.legend.${cell.state}`).toLowerCase(), week: cell.week })
        : t('team.overloaded', { name: r.name, load: cell.load, week: cell.week })
      out.push({ key: `${r.no}-${cell.week}`, text, activities: cell.activities })
    }
  }
  return out
})

const GUIDE_KEY = 'simultrain:team-guide-hidden'
const guideHidden = ref(false)
try {
  guideHidden.value = localStorage.getItem(GUIDE_KEY) === '1'
} catch {}
function toggleGuide() {
  guideHidden.value = !guideHidden.value
  try {
    localStorage.setItem(GUIDE_KEY, guideHidden.value ? '1' : '0')
  } catch {}
}

const proposal = ref(null)
async function level() {
  try {
    proposal.value = await sim.leveling()
  } catch (e) {
    sim.error = e.message
  }
}
async function accept() {
  await sim.setAssignments(proposal.value.assignments)
  proposal.value = null
}
const name = (no) => sim.resource(no).name
</script>

<template>
  <div class="mx-auto max-w-7xl space-y-5">
    <!-- how to use -->
    <button v-if="guideHidden" class="text-sm text-accent hover:underline" @click="toggleGuide">{{ t('team.showGuide') }}</button>
    <section v-else class="card p-5">
      <div class="flex items-start justify-between gap-4">
        <h2 class="font-medium text-slate-900">{{ t('team.guideTitle') }}</h2>
        <button class="text-sm text-slate-400 hover:text-slate-700" @click="toggleGuide">{{ t('team.hideGuide') }}</button>
      </div>
      <ol class="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <li v-for="(step, i) in guide" :key="i" class="text-sm leading-relaxed">
          <span class="flex items-center gap-2 font-medium text-slate-800">
            <span class="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-accent-soft text-xs font-semibold text-accent">{{ i + 1 }}</span>
            {{ step.title }}
          </span>
          <p class="mt-1.5 text-slate-600">{{ step.text }}</p>
        </li>
      </ol>
    </section>

    <!-- problems -->
    <section class="card p-5" :class="problems.length ? 'border-red-200' : 'border-emerald-200'">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <h2 class="font-medium" :class="problems.length ? 'text-red-700' : 'text-emerald-700'">
          {{ t('team.problems') }}<span v-if="problems.length"> · {{ problems.length }}</span>
        </h2>
        <button class="btn btn-ghost" :disabled="sim.running || sim.ended" @click="level">{{ t('team.leveling') }}</button>
      </div>
      <p v-if="sim.running" class="mt-2 text-xs text-amber-700">{{ t('team.pauseFirst') }}</p>
      <p v-if="!problems.length" class="mt-2 text-sm text-slate-600">{{ t('team.noProblems') }}</p>
      <ul v-else class="mt-3 space-y-2">
        <li v-for="p in problems" :key="p.key" class="flex flex-wrap items-center gap-2 text-sm text-slate-700">
          <span>{{ p.text }}</span>
          <button
            v-for="a in p.activities"
            :key="a"
            class="rounded-md border border-slate-200 px-2 py-0.5 text-xs hover:border-accent hover:text-accent"
            @click="openTask(a)"
          >
            {{ a }} · {{ sim.activity(a).name }}
          </button>
        </li>
      </ul>
    </section>

    <!-- grid -->
    <div class="card overflow-x-auto">
      <table class="w-full min-w-[900px] table-fixed text-sm">
        <thead>
          <tr class="border-b border-slate-200 text-xs text-slate-500">
            <th class="w-60 px-4 py-2.5 text-left font-medium">{{ t('team.person') }}</th>
            <th v-for="w in weeks" :key="w" class="py-2.5 font-medium" :class="{ 'text-accent': w === s.clock.week }">
              {{ w }}<span v-if="w === s.clock.week" class="block text-[10px] font-normal">{{ t('team.thisWeek') }}</span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="r in s.resources" :key="r.no">
            <td class="px-4 py-2">
              <div class="font-medium text-slate-800">{{ r.name }}</div>
              <div class="truncate text-xs text-slate-500" :title="r.role">{{ r.role }} · {{ t('team.rate', { rate: r.rate }) }}</div>
            </td>
            <td v-for="cell in r.weeks" :key="cell.week" class="p-0.5" :class="{ 'opacity-40': cell.week < s.clock.week }">
              <div
                class="flex h-10 flex-wrap items-center justify-center gap-0.5 rounded-md border border-slate-100"
                :class="[STATE_BG[cell.state], isConflict(cell) ? 'ring-2 ring-inset ring-red-500' : '']"
                :title="t(`team.legend.${cell.state}`) + (cell.activities.length ? ` · ${cell.load}%` : '')"
              >
                <button
                  v-for="a in cell.activities"
                  :key="a"
                  class="rounded px-1 text-xs font-medium text-slate-700 tabular-nums hover:bg-accent hover:text-white"
                  @click="openTask(a)"
                >
                  {{ a }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- legend -->
    <div class="flex flex-wrap gap-4 text-xs text-slate-600">
      <span v-for="(cls, st) in STATE_BG" :key="st" class="flex items-center gap-1.5">
        <span class="h-3 w-3 rounded-sm border border-slate-300" :class="cls" />{{ t(`team.legend.${st}`) }}
      </span>
      <span class="flex items-center gap-1.5"><span class="h-3 w-3 rounded-sm ring-2 ring-red-500 ring-inset" />{{ t('team.overload') }}</span>
    </div>

    <Modal v-if="proposal" :title="t('team.levelingTitle')" @close="proposal = null">
      <p v-if="!proposal.changes.length" class="text-sm text-slate-600">{{ t('team.noChanges') }}</p>
      <ul v-else class="space-y-2 text-sm text-slate-700">
        <li v-for="(c, i) in proposal.changes" :key="i" class="rounded-lg bg-slate-50 px-3 py-2">
          {{ t('team.move', { activity: `${c.activity} ${sim.activity(c.activity).name}`, from: name(c.from), to: name(c.to), percent: c.percent }) }}
        </li>
      </ul>
      <template #footer>
        <button class="btn btn-ghost" @click="proposal = null">{{ t('team.cancel') }}</button>
        <button v-if="proposal.changes.length" class="btn btn-primary" :disabled="sim.busy" @click="accept">{{ t('team.accept') }}</button>
      </template>
    </Modal>
  </div>
</template>
