<script setup>
import { useI18n } from 'vue-i18n'
import { useSim } from '../stores/sim.js'
import Icon from './Icon.vue'

const { t } = useI18n()
const sim = useSim()
</script>

<template>
  <span v-if="sim.ended" class="rounded-lg bg-slate-100 px-3 py-2 text-sm font-medium text-slate-500">{{ t('clock.ended') }}</span>
  <button v-else-if="sim.running" class="btn btn-ghost" :disabled="sim.busy" @click="sim.pause()">
    <Icon name="pause" class="h-4 w-4" /> {{ t('clock.pause') }}
  </button>
  <button v-else class="btn btn-primary" :disabled="sim.busy" @click="sim.start()">
    <Icon name="play" class="h-4 w-4" />
    {{ sim.state.status === 'paused' ? t('clock.resume') : t('clock.start') }}
  </button>
</template>
