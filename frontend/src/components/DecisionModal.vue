<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSim } from '../stores/sim.js'
import { useFormat } from '../format.js'
import Modal from './Modal.vue'
import EffectChips from './EffectChips.vue'

const props = defineProps({ id: { type: Number, required: true } })
const emit = defineEmits(['close'])
const { t } = useI18n()
const { shortTime } = useFormat()
const sim = useSim()

const d = computed(() => sim.state.decisions.find((x) => x.id === props.id))
const fridayNoon = computed(() => {
  const week = sim.state.clock.week
  return (week - 1) * 3300 + 4 * 660 + 4 * 60
})
const canPostpone = computed(() => d.value && !d.value.postponed && fridayNoon.value > sim.state.clock.minutes)

async function choose(key) {
  await sim.decide(props.id, key)
  if (key === 'postpone') emit('close')
}
</script>

<template>
  <Modal v-if="d" @close="emit('close')">
    <template #header>
      <p class="label">{{ t('decision.title') }}</p>
      <h2 class="mt-1 text-base font-semibold text-slate-900">{{ d.subject }}</h2>
    </template>

    <p class="text-sm leading-relaxed text-slate-700">{{ d.prompt }}</p>

    <template v-if="d.status === 'open'">
      <p class="mt-3 text-xs text-slate-500">
        {{ t('decision.deadline', { time: shortTime(d.deadline) }) }}
        <span v-if="d.postponed" class="ml-2 rounded bg-slate-100 px-1.5 py-0.5">{{ t('decision.postponed') }}</span>
      </p>
      <div class="mt-5 space-y-2">
        <button
          v-for="o in d.options"
          :key="o.key"
          class="w-full rounded-lg border border-slate-200 px-4 py-3 text-left text-sm text-slate-800 transition hover:border-accent hover:bg-accent-soft disabled:opacity-50"
          :disabled="sim.busy || sim.ended"
          @click="choose(o.key)"
        >
          {{ o.label }}
        </button>
      </div>
    </template>

    <template v-else>
      <div class="mt-5 rounded-lg bg-slate-50 p-4">
        <p class="label">{{ t('decision.yourChoice') }}</p>
        <p class="mt-1 text-sm font-medium text-slate-900">{{ d.option_label }}</p>
        <p v-if="d.resolved_by === 'auto'" class="mt-1 text-xs text-amber-700">{{ t('decision.auto') }}</p>
        <p class="mt-3 text-sm leading-relaxed text-slate-700">{{ d.feedback }}</p>
        <EffectChips :effects="d.effects" class="mt-3" />
      </div>
      <div v-if="d.learning_point" class="mt-4 border-l-2 border-accent pl-4">
        <p class="label">{{ t('decision.learning') }}</p>
        <p class="mt-1 text-sm text-slate-700">{{ d.learning_point }}</p>
      </div>
    </template>

    <template #footer>
      <button v-if="d.status === 'open' && canPostpone" class="btn btn-ghost" :disabled="sim.busy" @click="choose('postpone')">
        {{ t('decision.later') }}
      </button>
      <button v-if="d.status !== 'open'" class="btn btn-primary" @click="emit('close')">{{ t('decision.close') }}</button>
    </template>
  </Modal>
</template>
