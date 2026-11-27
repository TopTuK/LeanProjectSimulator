<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useSim } from '../stores/sim.js'
import Modal from './Modal.vue'
import IndexCard from './IndexCard.vue'
import endImg from '../assets/week-end.jpg'

const emit = defineEmits(['close'])
const { t } = useI18n()
const router = useRouter()
const sim = useSim()
const mode = computed(() => sim.state.config.mode || 'demo')
const game = computed(() => sim.state.game)

function again() {
  sim.disconnect()
  router.push('/control')
}
</script>

<template>
  <Modal wide @close="emit('close')">
    <template #header>
      <h2 class="text-lg font-semibold text-slate-900">{{ t(`end.${mode}Title`) }}</h2>
      <p class="mt-1 text-sm text-slate-500">{{ t(`end.${mode}Lead`) }}</p>
    </template>

    <img :src="endImg" alt="" class="mx-auto mb-4 h-24 w-auto mix-blend-multiply" />

    <section class="mb-5 rounded-xl bg-slate-900 p-5 text-center text-white" data-test="final-score">
      <p class="text-xs tracking-wide text-slate-300 uppercase">{{ t('end.score') }}</p>
      <p class="mt-1 text-4xl font-semibold">{{ game.score }}<span class="text-lg text-slate-400">/100</span></p>
      <p class="mt-1 text-sm font-medium text-amber-300">{{ t(`end.grade.${game.grade}`) }}</p>
      <div v-if="game.badges.length" class="mt-3 flex flex-wrap justify-center gap-2">
        <span v-for="b in game.badges" :key="b" class="rounded-full bg-white/10 px-3 py-1 text-xs">{{ t(`end.badges.${b}`) }}</span>
      </div>
    </section>

    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <IndexCard v-for="k in ['cost', 'schedule', 'quality', 'motivation']" :key="k" :label="t(`dim.${k}`)" :value="sim.state.indexes[k]" />
    </div>

    <dl class="mt-5 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
      <div class="rounded-lg bg-slate-50 p-3"><dt class="text-xs text-slate-500">{{ t('end.completion') }}</dt><dd class="mt-1 font-semibold">{{ game.completion }}%</dd></div>
      <div class="rounded-lg bg-slate-50 p-3"><dt class="text-xs text-slate-500">{{ t('end.onTimeDecisions') }}</dt><dd class="mt-1 font-semibold">{{ game.decision_count - game.auto_decisions }}/{{ game.decision_count }}</dd></div>
      <div v-if="game.risk_count" class="rounded-lg bg-slate-50 p-3"><dt class="text-xs text-slate-500">{{ t('end.risksManaged') }}</dt><dd class="mt-1 font-semibold">{{ game.risks_mitigated }}/{{ game.risk_count }}</dd></div>
      <div v-if="game.risk_count" class="rounded-lg bg-slate-50 p-3"><dt class="text-xs text-slate-500">{{ t('end.risksOccurred') }}</dt><dd class="mt-1 font-semibold">{{ game.risks_occurred }}</dd></div>
    </dl>

    <details class="mt-6">
      <summary class="label cursor-pointer">{{ t('end.decisions') }} · {{ game.decision_count }}</summary>
      <ul class="mt-2 max-h-64 space-y-2 overflow-y-auto pr-2 text-sm">
        <li v-for="d in sim.state.decisions" :key="d.id" class="flex justify-between gap-4">
          <span class="text-slate-600">{{ d.subject }}</span>
          <span class="text-right font-medium text-slate-900">
            {{ d.option_label }}
            <span v-if="d.resolved_by === 'auto'" class="ml-1 text-xs font-normal text-amber-700">({{ t('decision.autoShort') }})</span>
          </span>
        </li>
      </ul>
    </details>

    <template v-if="sim.state.learning_points.length">
      <h3 class="label mt-6">{{ t('end.learning') }}</h3>
      <ul class="mt-2 max-h-48 list-disc space-y-1 overflow-y-auto pl-5 text-sm text-slate-700">
        <li v-for="(p, i) in sim.state.learning_points" :key="i">{{ p }}</li>
      </ul>
    </template>

    <template #footer>
      <button class="btn btn-ghost" @click="emit('close')">{{ t('end.explore') }}</button>
      <button class="btn btn-primary" @click="again">{{ t('end.again') }}</button>
    </template>
  </Modal>
</template>
