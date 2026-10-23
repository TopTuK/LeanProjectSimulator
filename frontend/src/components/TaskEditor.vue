<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSim } from '../stores/sim.js'
import { useFormat } from '../format.js'
import Modal from './Modal.vue'

const props = defineProps({ no: { type: Number, required: true } })
const emit = defineEmits(['close'])
const { t } = useI18n()
const { money, num, pct } = useFormat()
const sim = useSim()

const a = computed(() => sim.activity(props.no))
const locked = computed(() => sim.running || sim.ended || a.value?.status === 'done')
const rows = ref(sim.state.assignments.filter((x) => x.activity_no === props.no).map((x) => ({ ...x })))
const PERCENTS = [25, 50, 75, 100]

const week = computed(() => sim.state.clock.week)
const free = computed(() => sim.state.resources.filter((r) => !rows.value.some((x) => x.resource_no === r.no)))
const stateTone = {
  payroll: 'text-slate-500',
  available: 'text-emerald-600',
  training: 'text-amber-600',
  sick: 'text-red-600',
  holiday: 'text-sky-600',
  other: 'text-slate-400',
}

function add(e) {
  const no = Number(e.target.value)
  if (no) rows.value.push({ activity_no: props.no, resource_no: no, percent: 100 })
  e.target.value = ''
}

async function save() {
  const others = sim.state.assignments.filter((x) => x.activity_no !== props.no)
  await sim.setAssignments([...others, ...rows.value])
  emit('close')
}
</script>

<template>
  <Modal v-if="a" @close="emit('close')">
    <template #header>
      <p class="label">{{ t('task.title', { no: a.no }) }}<span v-if="a.critical" class="ml-2 text-red-600">· {{ t('task.critical') }}</span></p>
      <h2 class="mt-1 text-base font-semibold text-slate-900">{{ a.name }}</h2>
    </template>

    <dl class="grid grid-cols-2 gap-x-6 gap-y-3 text-sm sm:grid-cols-3">
      <div><dt class="text-slate-500">{{ t('task.duration') }}</dt><dd class="font-medium">{{ t('task.days', { n: a.duration }) }}</dd></div>
      <div><dt class="text-slate-500">{{ t('task.effort') }}</dt><dd class="font-medium">{{ t('task.hours', { n: num(a.effort) }) }}</dd></div>
      <div><dt class="text-slate-500">{{ t('task.done') }}</dt><dd class="font-medium">{{ pct(a.progress * 100) }}</dd></div>
      <div><dt class="text-slate-500">{{ t('task.plannedWindow') }}</dt><dd class="font-medium">{{ t('weekN', { n: Math.floor(a.es / 5) + 1 }) }} – {{ t('weekN', { n: Math.ceil(a.ef / 5) }) }}</dd></div>
      <div><dt class="text-slate-500">{{ t('budget.planned') }}</dt><dd class="font-medium">{{ money(a.planned_cost) }}</dd></div>
      <div><dt class="text-slate-500">{{ t('task.preds') }}</dt><dd class="font-medium">{{ a.preds.length ? a.preds.join(', ') : t('task.none') }}</dd></div>
    </dl>
    <p class="mt-3 text-xs text-slate-500">{{ t(`task.status.${a.status}`) }}</p>

    <h3 class="label mt-6">{{ t('task.assignments') }}</h3>
    <ul class="mt-2 divide-y divide-slate-100 rounded-lg border border-slate-200">
      <li v-for="(row, i) in rows" :key="row.resource_no" class="flex items-center gap-3 px-3 py-2 text-sm">
        <span class="min-w-0 flex-1">
          <span class="font-medium text-slate-800">{{ sim.resource(row.resource_no).name }}</span>
          <span class="ml-2 text-xs text-slate-500">{{ sim.resource(row.resource_no).role }}</span>
          <span class="ml-2 text-xs" :class="stateTone[sim.resource(row.resource_no).weeks[week - 1].state]">
            {{ t(`team.legend.${sim.resource(row.resource_no).weeks[week - 1].state}`) }}
          </span>
        </span>
        <select v-model.number="row.percent" :disabled="locked" class="rounded-md border border-slate-200 px-2 py-1 text-sm">
          <option v-for="p in PERCENTS" :key="p" :value="p">{{ p }}%</option>
        </select>
        <button v-if="!locked" class="text-xs text-slate-400 hover:text-red-600" @click="rows.splice(i, 1)">{{ t('task.remove') }}</button>
      </li>
      <li v-if="!locked" class="px-3 py-2">
        <select class="w-full rounded-md border border-dashed border-slate-300 px-2 py-1.5 text-sm text-slate-500" @change="add">
          <option value="">+ {{ t('task.add') }}</option>
          <option v-for="r in free" :key="r.no" :value="r.no">
            {{ r.name }} — {{ r.role }} · {{ t(`team.legend.${r.weeks[week - 1].state}`) }} · {{ t('team.rate', { rate: r.rate }) }}
          </option>
        </select>
      </li>
    </ul>
    <p v-if="locked && a.status !== 'done' && !sim.ended" class="mt-3 text-xs text-amber-700">{{ t('task.locked') }}</p>

    <template #footer>
      <button class="btn btn-ghost" @click="emit('close')">{{ t('task.close') }}</button>
      <button v-if="!locked" class="btn btn-primary" :disabled="sim.busy" @click="save">{{ t('task.save') }}</button>
    </template>
  </Modal>
</template>
