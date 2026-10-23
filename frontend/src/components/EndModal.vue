<script setup>
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useSim } from '../stores/sim.js'
import Modal from './Modal.vue'
import IndexCard from './IndexCard.vue'

const emit = defineEmits(['close'])
const { t } = useI18n()
const router = useRouter()
const sim = useSim()

function again() {
  sim.disconnect()
  router.push('/control')
}
</script>

<template>
  <Modal wide @close="emit('close')">
    <template #header>
      <h2 class="text-lg font-semibold text-slate-900">{{ t('end.title') }}</h2>
      <p class="mt-1 text-sm text-slate-500">{{ t('end.lead') }}</p>
    </template>

    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <IndexCard v-for="k in ['cost', 'schedule', 'quality', 'motivation']" :key="k" :label="t(`dim.${k}`)" :value="sim.state.indexes[k]" />
    </div>

    <h3 class="label mt-6">{{ t('end.decisions') }}</h3>
    <ul class="mt-2 space-y-2 text-sm">
      <li v-for="d in sim.state.decisions" :key="d.id" class="flex justify-between gap-4">
        <span class="text-slate-600">{{ d.subject }}</span>
        <span class="text-right font-medium text-slate-900">
          {{ d.option_label }}
          <span v-if="d.resolved_by === 'auto'" class="ml-1 text-xs font-normal text-amber-700">({{ t('decision.autoShort') }})</span>
        </span>
      </li>
    </ul>

    <template v-if="sim.state.learning_points.length">
      <h3 class="label mt-6">{{ t('end.learning') }}</h3>
      <ul class="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
        <li v-for="(p, i) in sim.state.learning_points" :key="i">{{ p }}</li>
      </ul>
    </template>

    <template #footer>
      <button class="btn btn-ghost" @click="emit('close')">{{ t('end.explore') }}</button>
      <button class="btn btn-primary" @click="again">{{ t('end.again') }}</button>
    </template>
  </Modal>
</template>
